"""
FDA Medication Search - Examples and Testing

This module demonstrates how to search for medications using the FDA drug API.
You can run this script directly or import the search function into your own code.
"""

import requests
import json
from typing import Dict, List, Any

FDA_API_BASE = "https://api.fda.gov/drug/ndc.json"


def search_medication(search_term: str, search_type: str = "generic_name") -> Dict[str, Any]:
    """
    Search for medications using the FDA drug API.
    
    Args:
        search_term: The medication name or NDC code to search
        search_type: Type of search - 'generic_name', 'brand_name', or 'ndc'
    
    Returns:
        Dictionary containing search results or error information
    
    Examples:
        >>> results = search_medication("aspirin", "generic_name")
        >>> results = search_medication("Tylenol", "brand_name")
        >>> results = search_medication("0093-0147", "ndc")
    """
    try:
        if not search_term or not search_term.strip():
            return {"success": False, "error": "Search term cannot be empty"}
        
        search_term = search_term.strip()
        
        # Map search types to FDA API field names
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
            query = f'product_ndc:"{clean_ndc}"'
        else:
            # For text searches, use wildcard search
            query = f'{field}:{search_term}*'
        
        params = {
            "search": query,
            "limit": 10
        }
        
        print(f"Searching for: {search_term} ({search_type})")
        print(f"API Query: {query}\n")
        
        response = requests.get(FDA_API_BASE, params=params, timeout=10)
        print(f"Request URL: {response.url}")
        print(f"Status Code: {response.status_code}\n")
        
        if response.status_code == 200:
            data = response.json()
            
            if "results" in data and data["results"]:
                return {
                    "success": True,
                    "count": len(data.get("results", [])),
                    "results": data.get("results", [])
                }
            else:
                return {
                    "success": True,
                    "count": 0,
                    "results": [],
                    "message": "No medications found"
                }
        elif response.status_code == 404:
            # 404 means no results found
            return {
                "success": True,
                "count": 0,
                "results": [],
                "message": "No medications found. Try a different search term."
            }
        else:
            return {"success": False, "error": f"API error: HTTP {response.status_code}"}
    
    except requests.exceptions.Timeout:
        return {"success": False, "error": "Request timed out. Please try again."}
    except requests.exceptions.ConnectionError:
        return {"success": False, "error": "Connection error. Please check your internet connection."}
    except Exception as e:
        return {"success": False, "error": str(e)}


def print_medication_info(medication: Dict[str, Any]) -> None:
    """Pretty print medication information"""
    print("-" * 60)
    
    # Print basic info
    generic = medication.get("generic_name", "N/A")
    brand = medication.get("brand_name", "N/A")
    ndc = medication.get("product_ndc", "N/A")
    
    print(f"Generic Name: {generic}")
    print(f"Brand Name:   {brand}")
    print(f"NDC Code:     {ndc}")
    
    # Print active ingredients
    if "active_ingredients" in medication:
        print(f"\nActive Ingredients:")
        for ingredient in medication["active_ingredients"]:
            name = ingredient.get("name", "Unknown")
            strength = ingredient.get("strength", "")
            if strength:
                print(f"  - {name} ({strength})")
            else:
                print(f"  - {name}")
    
    # Print other details
    if "dosage_form" in medication:
        print(f"\nDosage Form:  {medication['dosage_form']}")
    
    if "labeler_name" in medication:
        print(f"Manufacturer: {medication['labeler_name']}")
    
    if "route" in medication:
        print(f"Route:        {', '.join(medication['route'])}")
    
    # Print images if available
    if "images" in medication and medication["images"]:
        print(f"\nMedication Images:")
        for idx, img in enumerate(medication["images"], 1):
            print(f"  Image {idx}: {img.get('title', 'Medication Image')}")
            print(f"    URL: {img.get('url', 'N/A')}")
    else:
        print(f"\nImages: Not available")
    
    print("-" * 60)


def main():
    """Run example searches"""
    print("=" * 60)
    print("FDA MEDICATION SEARCH - EXAMPLES")
    print("=" * 60)
    print()
    
    # Example 1: Search by generic name
    print("EXAMPLE 1: Search by Generic Name (Aspirin)")
    print("=" * 60)
    result = search_medication("aspirin", "generic_name")
    
    if result["success"] and result["count"] > 0:
        print(f"Found {result['count']} results:\n")
        for med in result["results"][:3]:  # Show first 3 results
            print_medication_info(med)
    else:
        print(f"Error: {result.get('error', 'No results found')}")
    
    print("\n")
    
    # Example 2: Search by NDC code
    print("EXAMPLE 2: Search by NDC Code (0093-0147)")
    print("=" * 60)
    result = search_medication("0093-0147", "ndc")
    
    if result["success"] and result["count"] > 0:
        print(f"Found {result['count']} results:\n")
        for med in result["results"]:
            print_medication_info(med)
    else:
        print(f"Error: {result.get('error', 'No results found')}")
    
    print("\n")
    
    # Example 3: Search by brand name
    print("EXAMPLE 3: Search by Brand Name (Tylenol)")
    print("=" * 60)
    result = search_medication("Tylenol", "brand_name")
    
    if result["success"] and result["count"] > 0:
        print(f"Found {result['count']} results:\n")
        for med in result["results"][:2]:  # Show first 2 results
            print_medication_info(med)
    else:
        print(f"Error: {result.get('error', 'No results found')}")


if __name__ == "__main__":
    main()
