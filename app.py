from flask import Flask, render_template, request, jsonify
import requests
import json
import base64
import os
from typing import Dict, List, Any
import urllib.parse
from concurrent.futures import ThreadPoolExecutor, as_completed
import random

app = Flask(__name__)

FDA_API_BASE = "https://api.fda.gov/drug/ndc.json"
FDA_RXIMAGE_API = "https://rximage.nlm.nih.gov/api/rximage/1/rxnorm"

# Typical pharmacy price ranges (in USD) - for demonstration purposes
PHARMACY_BASE_PRICES = {
    "cvs": {"markup": 1.35, "name": "CVS Pharmacy"},
    "walgreens": {"markup": 1.38, "name": "Walgreens"},
    "walmart": {"markup": 1.25, "name": "Walmart"},
}
GOODRX_DISCOUNT = 0.25  # Average 25% discount with GoodRx

# Map manufacturer/labeler names (from the FDA labeler_name field) to their
# corporate domains so we can fetch real brand logos. Keywords are matched
# case-insensitively against the full labeler name, in order.
MANUFACTURER_DOMAINS = [
    # Large pharma / brand manufacturers
    ("pfizer", "pfizer.com"),
    ("viatris", "viatris.com"),
    ("mylan", "mylan.com"),
    ("upjohn", "upjohn.com"),
    ("teva", "tevapharm.com"),
    ("sandoz", "sandoz.com"),
    ("novartis", "novartis.com"),
    ("johnson", "jnj.com"),
    ("janssen", "janssen.com"),
    ("merck", "merck.com"),
    ("abbvie", "abbvie.com"),
    ("astrazeneca", "astrazeneca.com"),
    ("gsk", "gsk.com"),
    ("glaxosmithkline", "gsk.com"),
    ("glaxo", "gsk.com"),
    ("sanofi", "sanofi.com"),
    ("roche", "roche.com"),
    ("genentech", "gene.com"),
    ("bayer", "bayer.com"),
    ("lilly", "lilly.com"),
    ("bristol", "bms.com"),
    ("amgen", "amgen.com"),
    ("boehringer", "boehringer-ingelheim.com"),
    ("takeda", "takeda.com"),
    ("abbott", "abbott.com"),
    ("gilead", "gilead.com"),
    ("allergan", "allergan.com"),
    ("bausch", "bauschhealth.com"),
    ("endo", "endo.com"),
    ("mallinckrodt", "mallinckrodt.com"),
    ("perrigo", "perrigo.com"),
    ("lundbeck", "lundbeck.com"),
    ("otsuka", "otsuka-us.com"),
    ("shionogi", "shionogi.com"),
    ("daiichi", "daiichisankyo.com"),
    ("eisai", "eisai.com"),
    ("fresenius", "fresenius-kabi.com"),
    ("baxter", "baxter.com"),
    ("hospira", "hospira.com"),
    ("wyeth", "pfizer.com"),
    ("pharmacia", "pfizer.com"),
    ("roerig", "pfizer.com"),
    ("greenstone", "pfizer.com"),
    ("forest", "allergan.com"),
    ("watson", "tevapharm.com"),
    ("actavis", "tevapharm.com"),
    ("hikma", "hikma.com"),
    ("west-ward", "hikma.com"),

    # Generic manufacturers
    ("lupin", "lupin.com"),
    ("cipla", "cipla.com"),
    ("sun pharma", "sunpharma.com"),
    ("sun pharmaceutical", "sunpharma.com"),
    ("aurobindo", "aurobindo.com"),
    ("torrent", "torrentpharma.com"),
    ("zydus", "zydus.com"),
    ("dr. reddy", "drreddys.com"),
    ("dr reddy", "drreddys.com"),
    ("alembic", "alembicpharma.com"),
    ("glenmark", "glenmarkpharma.com"),
    ("intas", "intaspharma.com"),
    ("amneal", "amneal.com"),
    ("prasco", "prasco.com"),
    ("upsher-smith", "upsher-smith.com"),
    ("upsher smith", "upsher-smith.com"),
    ("apotex", "apotex.com"),
    ("par pharmaceutical", "parpharm.com"),
    ("qualitest", "qualitestproducts.com"),
    ("major pharmaceuticals", "majorpharmaceuticals.com"),
    ("heritage", "heritagepharma.com"),
    ("avkare", "avkare.com"),
    ("bryant ranch", "bryantranchprepack.com"),
    ("northwind", "northwindpharmaceuticals.com"),
    ("remedyrepack", "remedypack.com"),

    # Retail pharmacy chains that repackage medications
    ("cvs", "cvs.com"),
    ("walgreens", "walgreens.com"),
    ("walmart", "walmart.com"),
    ("kroger", "kroger.com"),
    ("rite aid", "riteaid.com"),
    ("costco", "costco.com"),
    ("target", "target.com"),
    ("dollar general", "dollargeneral.com"),
    ("meijer", "meijer.com"),
    ("hy-vee", "hy-vee.com"),
    ("publix", "publix.com"),
    ("safeway", "safeway.com"),
    ("albertsons", "albertsons.com"),
]

def get_full_ndc(med: Dict[str, Any]) -> str:
    """
    Extract the full NDC code from a medication record.
    
    The FDA API returns two NDC fields:
    - product_ndc: The 9-digit product NDC (e.g., "37835-571")
    - packaging[].package_ndc: The full 10/11-digit NDC (e.g., "37835-571-05")
    
    This function returns the full package NDC when available,
    falling back to the product NDC if packaging is not present.
    
    Args:
        med: A medication record from the FDA API
    
    Returns:
        The full NDC code string
    """
    packaging = med.get("packaging", [])
    if packaging:
        for pkg in packaging:
            package_ndc = pkg.get("package_ndc", "")
            if package_ndc:
                return package_ndc
    return med.get("product_ndc", "")


def get_manufacturer_domain(labeler_name: str) -> str:
    """
    Map a manufacturer/labeler name to its corporate domain for logo lookups.

    First checks a curated list of known manufacturers, then falls back to
    stripping common corporate suffixes (Inc, LLC, Laboratories, etc.) and
    building a plausible domain from the remaining name.

    Args:
        labeler_name: The labeler_name field from the FDA NDC API

    Returns:
        A corporate domain string (e.g., "pfizer.com") or "" if unknown
    """
    if not labeler_name:
        return ""

    name_lower = labeler_name.lower().strip()

    # 1) Check known manufacturers first (keywords matched in order)
    for keyword, domain in MANUFACTURER_DOMAINS:
        if keyword in name_lower:
            return domain

    # 2) Fallback: strip common corporate suffixes and build a domain
    cleaned = name_lower
    for suffix in (
        " pharmaceuticals", " pharmaceutical", " laboratories", " laboratory",
        " labs", " pharma", " group", " holdings", " healthcare", " health",
        " technologies", " usa", " u.s.", " north america", " international",
        " generics", " biopharma", " biotech", " inc", " llc", " ltd",
        " limited", " corporation", " corp", " company", " co",
    ):
        cleaned = cleaned.replace(suffix, "")

    cleaned = (
        cleaned.replace("&", "and")
        .replace(",", "")
        .replace(".", "")
        .replace("'", "")
        .replace(" ", "")
    )

    if not cleaned or len(cleaned) < 3:
        return ""

    return f"{cleaned}.com"


def get_manufacturer_logo(labeler_name: str) -> str:
    """
    Generate a manufacturer brand logo URL using Google's favicon service.

    The Google favicon service returns a free CDN-hosted PNG for any domain.
    If the manufacturer can't be resolved to a domain, returns an empty string
    so the frontend can show a fallback icon instead.

    Args:
        labeler_name: The labeler_name field from the FDA NDC API

    Returns:
        A logo image URL or "" if no domain could be determined
    """
    domain = get_manufacturer_domain(labeler_name)
    if not domain:
        return ""
    return f"https://www.google.com/s2/favicons?domain={domain}&sz=128"


def generate_placeholder_image(medication_name: str, ndc_code: str) -> str:
    """
    Generate a data URL for a placeholder image if real image is not available.
    
    Args:
        medication_name: Name of the medication
        ndc_code: NDC code of the medication
    
    Returns:
        Data URL for SVG placeholder image
    """
    # Clean up names for display
    name = medication_name[:40] if medication_name else "Medication"
    
    # Create a simple SVG placeholder
    svg = f'''<svg xmlns="http://www.w3.org/2000/svg" width="300" height="200" viewBox="0 0 300 200">
        <defs>
            <linearGradient id="grad" x1="0%" y1="0%" x2="100%" y2="100%">
                <stop offset="0%" style="stop-color:#667eea;stop-opacity:1" />
                <stop offset="100%" style="stop-color:#764ba2;stop-opacity:1" />
            </linearGradient>
        </defs>
        <rect width="300" height="200" fill="url(#grad)"/>
        <circle cx="150" cy="70" r="35" fill="white" opacity="0.3"/>
        <text x="150" y="130" font-family="Arial, sans-serif" font-size="16" font-weight="bold" 
              text-anchor="middle" fill="white">{name}</text>
        <text x="150" y="160" font-family="Arial, sans-serif" font-size="12" 
              text-anchor="middle" fill="white" opacity="0.8">Medication Image</text>
        <text x="150" y="185" font-family="Arial, sans-serif" font-size="10" 
              text-anchor="middle" fill="white" opacity="0.6">NDC: {ndc_code or 'N/A'}</text>
    </svg>'''
    
    # Convert to data URL
    svg_base64 = base64.b64encode(svg.encode()).decode()
    return f"data:image/svg+xml;base64,{svg_base64}"


def generate_pricing_info(medication_name: str, dosage_form: str = "", strength: str = "") -> Dict[str, Any]:
    """
    Generate estimated pharmacy pricing information.
    
    Args:
        medication_name: Name of the medication
        dosage_form: Form of medication (tablet, capsule, etc)
        strength: Strength of medication (e.g., "500mg")
    
    Returns:
        Dictionary containing pricing estimates and retail links
    """
    # Base estimated cost (varies by medication class and strength)
    # This is a simplified estimate - actual prices vary significantly
    base_cost = random.uniform(8.0, 35.0)  # Random between $8-35 generic cost
    
    pricing = {
        "disclaimer": "Prices shown are estimates. Actual prices vary based on location, insurance, quantity, and manufacturer.",
        "base_estimated_cost": round(base_cost, 2),
        "pharmacies": {},
        "goodrx": {},
        "links": {
            "goodrx": f"https://www.goodrx.com/?drug={urllib.parse.quote(medication_name)}",
            "cvs": f"https://www.cvs.com/search/prescriptions/results?query={urllib.parse.quote(medication_name)}",
            "walgreens": f"https://www.walgreens.com/pharmacy/search?term={urllib.parse.quote(medication_name)}",
            "walmart": f"https://www.walmart.com/search/?query={urllib.parse.quote(medication_name)}"
        }
    }
    
    # Calculate estimated prices at each pharmacy
    for pharmacy_key, pharmacy_info in PHARMACY_BASE_PRICES.items():
        estimated_price = round(base_cost * pharmacy_info["markup"], 2)
        pricing["pharmacies"][pharmacy_key] = {
            "name": pharmacy_info["name"],
            "estimated_price": estimated_price,
            "link": pricing["links"][pharmacy_key]
        }
    
    # Calculate GoodRx savings
    goodrx_price = round(base_cost * (1 - GOODRX_DISCOUNT), 2)
    goodrx_savings = round(base_cost - goodrx_price, 2)
    pricing["goodrx"] = {
        "estimated_goodrx_price": goodrx_price,
        "estimated_savings": goodrx_savings,
        "savings_percentage": round(GOODRX_DISCOUNT * 100),
        "link": pricing["links"]["goodrx"],
        "note": "GoodRx shows negotiated prices from partnered pharmacies"
    }
    
    return pricing


def fetch_medication_images(ndc_code: str, generic_name: str, brand_name: str = "") -> List[Dict[str, str]]:
    """
    Fetch medication images from the FDA RxImage API with fallbacks.
    
    Args:
        ndc_code: NDC code for the medication
        generic_name: Generic name of the medication
        brand_name: Brand name of the medication
    
    Returns:
        List of image dictionaries with URLs and metadata
    """
    images = []
    
    try:
        # Try searching by NDC first
        if ndc_code:
            try:
                ndc_clean = ndc_code.replace("-", "").replace(" ", "")
                ndc_formats = [ndc_code, ndc_clean]
                
                for ndc_to_try in ndc_formats:
                    if not ndc_to_try or len(ndc_to_try) < 5:
                        continue
                    
                    try:
                        params = {"ndc": ndc_to_try}
                        response = requests.get(FDA_RXIMAGE_API, params=params, timeout=5)
                        
                        print(f"DEBUG: RxImage NDC request - NDC: {ndc_to_try}, Status: {response.status_code}")
                        print(f"DEBUG: RxImage Response Text (first 200 chars): {response.text[:200]}")
                        
                        if response.status_code == 200:
                            data = response.json()
                            print(f"DEBUG: RxImage parsed JSON - Type: {type(data)}, Keys: {data.keys() if isinstance(data, dict) else 'N/A'}")
                            
                            # Try to extract images from response
                            extracted_images = extract_images_from_response(data)
                            if extracted_images:
                                images.extend(extracted_images)
                                print(f"DEBUG: Found {len(extracted_images)} images from NDC search")
                                return images
                    except Exception as e:
                        print(f"DEBUG: Error in NDC search iteration: {e}")
            except Exception as e:
                print(f"DEBUG: Error fetching by NDC: {e}")
        
        # If no images found by NDC, try by name
        if not images and (generic_name or brand_name):
            for search_name in [generic_name, brand_name]:
                if not search_name:
                    continue
                    
                try:
                    for name_variation in [search_name, search_name.lower(), search_name.upper()]:
                        try:
                            params = {"name": name_variation}
                            response = requests.get(FDA_RXIMAGE_API, params=params, timeout=5)
                            
                            print(f"DEBUG: RxImage name request - Name: {name_variation}, Status: {response.status_code}")
                            
                            if response.status_code == 200:
                                data = response.json()
                                extracted_images = extract_images_from_response(data)
                                if extracted_images:
                                    images.extend(extracted_images)
                                    print(f"DEBUG: Found {len(extracted_images)} images from name search")
                                    return images
                        except Exception as e:
                            print(f"DEBUG: Error in name search iteration: {e}")
                except Exception as e:
                    print(f"DEBUG: Error fetching by name: {e}")
        
        # If still no images, try brand name from the API response
        if not images and brand_name:
            try:
                params = {"name": brand_name}
                response = requests.get(FDA_RXIMAGE_API, params=params, timeout=5)
                if response.status_code == 200:
                    data = response.json()
                    extracted_images = extract_images_from_response(data)
                    if extracted_images:
                        return extracted_images
            except Exception as e:
                print(f"DEBUG: Error fetching brand name images: {e}")
        
    except Exception as e:
        print(f"DEBUG: Unexpected error in fetch_medication_images: {e}")
    
    # Fallback: Return placeholder image
    print(f"DEBUG: No real images found, using placeholder for: {generic_name or brand_name or ndc_code}")
    placeholder_url = generate_placeholder_image(generic_name or brand_name or "Medication", ndc_code or "Unknown")
    return [{
        "url": placeholder_url,
        "title": f"Placeholder Image - {generic_name or brand_name or 'Medication'}",
        "source": "Placeholder"
    }]


def extract_images_from_response(data: Any) -> List[Dict[str, str]]:
    """
    Extract images from various response formats from the RxImage API.
    
    Args:
        data: Response data from RxImage API
    
    Returns:
        List of image dictionaries
    """
    images = []
    
    try:
        if isinstance(data, dict):
            # Format 1: {"data": {"images": [...]}}
            if "data" in data and isinstance(data["data"], dict):
                if "images" in data["data"] and isinstance(data["data"]["images"], list):
                    for img_data in data["data"]["images"]:
                        url = img_data.get("imageUrl") or img_data.get("url") or ""
                        if url:
                            images.append({
                                "url": url,
                                "title": img_data.get("title", img_data.get("name", "Medication Image")),
                                "source": "FDA RxImage"
                            })
            
            # Format 2: {"images": [...]}
            elif "images" in data and isinstance(data["images"], list):
                for img_data in data["images"]:
                    url = img_data.get("imageUrl") or img_data.get("url") or ""
                    if url:
                        images.append({
                            "url": url,
                            "title": img_data.get("title", img_data.get("name", "Medication Image")),
                            "source": "FDA RxImage"
                        })
        
        # Format 3: Direct array
        elif isinstance(data, list):
            for img_data in data:
                if isinstance(img_data, dict):
                    url = img_data.get("imageUrl") or img_data.get("url") or ""
                    if url:
                        images.append({
                            "url": url,
                            "title": img_data.get("title", img_data.get("name", "Medication Image")),
                            "source": "FDA RxImage"
                        })
    except Exception as e:
        print(f"DEBUG: Error extracting images: {e}")
    
    return images


def search_medication(search_term: str, search_type: str = "generic_name") -> Dict[str, Any]:
    """
    Search for medications using the FDA drug API.
    
    Args:
        search_term: The medication name or NDC code to search
        search_type: Type of search - 'generic_name', 'brand_name', or 'ndc'
    
    Returns:
        Dictionary containing search results or error information
    """
    try:
        if not search_term or not search_term.strip():
            return {"success": False, "error": "Search term cannot be empty"}
        
        search_term = search_term.strip()
        
        # Map search types to FDA API field names
        # Note: FDA API uses specific field names that are case-sensitive
        search_fields = {
            "generic_name": "generic_name",
            "brand_name": "brand_name",
            "ndc": "product_ndc"
        }
        
        field = search_fields.get(search_type, "generic_name")
        
        # Build the search query
        if search_type == "ndc":
            # For NDC codes, format properly (with or without dashes)
            clean_ndc = search_term.replace("-", "").replace(" ", "")
            # Try exact match with quotes on both product_ndc and package_ndc (full NDC)
            query = f'product_ndc:"{clean_ndc}" OR packaging.package_ndc:"{clean_ndc}"'
        else:
            # For text searches, use wildcard search
            # Note: Wildcards are at the end
            query = f'{field}:{search_term}*'
        
        params = {
            "search": query,
            "limit": 10
        }
        
        print(f"DEBUG: Search term: {search_term}")
        print(f"DEBUG: Search type: {search_type}")
        print(f"DEBUG: Query: {query}")
        print(f"DEBUG: API Base: {FDA_API_BASE}")
        
        # Make the API request
        response = requests.get(FDA_API_BASE, params=params, timeout=10)
        
        print(f"DEBUG: Status Code: {response.status_code}")
        print(f"DEBUG: Full URL: {response.url}")
        
        if response.status_code == 200:
            data = response.json()
            
            # Check if results exist
            if "results" in data and data["results"]:
                results = data.get("results", [])
                
                # Add full NDC to each result and fetch images in parallel
                print(f"DEBUG: Fetching images for {len(results)} medications...")
                with ThreadPoolExecutor(max_workers=5) as executor:
                    futures = {}
                    for idx, med in enumerate(results):
                        # Extract the full NDC (package_ndc) for each medication
                        med["full_ndc"] = get_full_ndc(med)
                        ndc = med.get("full_ndc") or med.get("product_ndc", "")
                        generic = med.get("generic_name", "")
                        brand = med.get("brand_name", "")
                        future = executor.submit(fetch_medication_images, ndc, generic, brand)
                        futures[future] = idx
                    
                    # Add images to results as they complete
                    for future in as_completed(futures):
                        idx = futures[future]
                        try:
                            images = future.result()
                            results[idx]["images"] = images
                        except Exception as e:
                            print(f"DEBUG: Error getting images: {e}")
                            results[idx]["images"] = []
                
                # Add pricing information and manufacturer logo to each result
                for med in results:
                    med_name = med.get("generic_name", med.get("brand_name", "Medication"))
                    dosage = med.get("dosage_form", "")
                    strength = ""
                    if med.get("active_ingredients"):
                        strength = med.get("active_ingredients", [{}])[0].get("strength", "")
                    med["pricing"] = generate_pricing_info(med_name, dosage, strength)
                    med["manufacturer_logo"] = get_manufacturer_logo(med.get("labeler_name", ""))
                
                return {
                    "success": True,
                    "count": len(results),
                    "results": results
                }
            else:
                return {
                    "success": True,
                    "count": 0,
                    "results": [],
                    "message": "No medications found matching your search"
                }
        elif response.status_code == 404:
            # 404 usually means the search returned no results
            return {
                "success": True,
                "count": 0,
                "results": [],
                "message": "No medications found. Try a different search term."
            }
        else:
            # Try to parse error from response
            try:
                error_data = response.json()
                error_msg = error_data.get("error", {}).get("message", f"HTTP {response.status_code}")
            except:
                error_msg = f"API returned HTTP {response.status_code}"
            
            return {"success": False, "error": error_msg}
    
    except requests.exceptions.Timeout:
        return {"success": False, "error": "Request timed out. FDA API is not responding. Please try again later."}
    except requests.exceptions.ConnectionError:
        return {"success": False, "error": "Connection error. Please check your internet connection."}
    except requests.exceptions.RequestException as e:
        return {"success": False, "error": f"Request error: {str(e)}"}
    except Exception as e:
        return {"success": False, "error": f"Unexpected error: {str(e)}"}


@app.route("/")
def index():
    """Render the main page"""
    return render_template("index.html")


@app.route("/api/search", methods=["POST"])
def api_search():
    """API endpoint for medication search"""
    data = request.get_json()
    search_term = data.get("search_term", "").strip()
    search_type = data.get("search_type", "generic_name")
    
    if not search_term:
        return jsonify({"success": False, "error": "Search term cannot be empty"}), 400
    
    result = search_medication(search_term, search_type)
    return jsonify(result)


if __name__ == "__main__":
    # Production-ready configuration:
    # - PORT comes from the environment (Render/Railway set this automatically)
    # - HOST binds to 0.0.0.0 so the app is reachable from outside the container
    # - DEBUG is off by default; set DEBUG=true only for local development
    port = int(os.environ.get("PORT", 5000))
    debug = os.environ.get("DEBUG", "false").lower() == "true"
    app.run(host="0.0.0.0", port=port, debug=debug)
