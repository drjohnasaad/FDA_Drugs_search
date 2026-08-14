# FDA Medication Search Application

A web application for searching medications using the FDA drug database API.

## Features

- 🔍 Search medications by generic name, brand name, or NDC code
- 📱 Responsive design works on desktop and mobile
- 📷 Display medication photos from FDA RxImage database
- 🎨 Beautiful placeholder images when real photos aren't available
- ⚡ Real-time search results with detailed medication information
- 🎨 Clean, modern user interface
- 🐛 Built-in debugging and troubleshooting

## Prerequisites

- Python 3.7+
- pip (Python package manager)
- Internet connection (to access FDA API)

## Quick Start

1. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

2. **Run the Flask application:**
   ```bash
   python3 app.py
   ```

3. **Open your browser and navigate to:**
   ```
   http://localhost:5000
   ```

4. **Try searching for:**
   - Generic name: "aspirin"
   - Brand name: "tylenol"  
   - NDC code: "00930147" (from the original example without dashes)

## Usage

### Web Interface

1. Enter a medication name (e.g., "aspirin"), brand name (e.g., "Tylenol"), or NDC code
2. Select the search type from the dropdown
3. Click "Search Medications"
4. View detailed information about the found medications, including:
   - **📷 Medication Photos**: 
     - Real photos from FDA RxImage database (when available)
     - Beautiful placeholder images if no real photos exist
   - Manufacturer and dosage information
   - Active ingredients
   - Route of administration

### Image Display

The app automatically fetches medication photos from the FDA RxImage database. If no real images are available:
- The app displays a **placeholder image** with the medication name
- This is normal - not all medications have photos in the FDA database
- Placeholder images still help identify the medication visually
- You can see "Source: Placeholder" label to identify these

**Pro tip**: Try searching for common medications like "aspirin" or "ibuprofen" to see real FDA RxImage photos. Then try searching for other medications to see placeholder images.

### Command Line / Python Script

Run the example searches:
```bash
python3 test.py
```

This will show you how the API works and provide real medication data.

## API Endpoints

### POST /api/search

Search for medications.

**Request body:**
```json
{
  "search_term": "aspirin",
  "search_type": "generic_name"
}
```

**Response:**
```json
{
  "success": true,
  "count": 10,
  "results": [
    {
      "generic_name": "ASPIRIN",
      "brand_name": "ASPIRIN",
      "product_ndc": "0093-0147",
      "dosage_form": "TABLET",
      "labeler_name": "BAYER",
      "active_ingredients": [...],
      "route": ["ORAL"],
      "images": [
        {
          "url": "https://rximage.nlm.nih.gov/...",
          "title": "ASPIRIN 500MG TABLET",
          "source": "FDA RxImage"
        }
      ]
    }
  ]
}
```

The `images` array contains:
- **url**: Direct link to the medication photo from FDA RxImage API
- **title**: Description of the medication image
- **source**: "FDA RxImage" - indicates the source of the image

## Search Types

- **Generic Name**: Search by the generic/chemical name (e.g., "aspirin", "ibuprofen")
  - Format: `aspirin` (partial match with wildcard)
  
- **Brand Name**: Search by the brand name (e.g., "Tylenol", "Advil")
  - Format: `tylenol` (partial match with wildcard)
  
- **NDC Code**: Search by NDC (National Drug Code)
  - Format: Use with or without dashes: `0093-0147` or `00930147`
  - The app will automatically normalize it

## Troubleshooting

### Getting 404 Error?

The FDA API returns 404 when no results are found. This usually means:

1. **Check spelling** - Is the medication name spelled correctly?
2. **Try different search types** - Switch between Generic Name and Brand Name
3. **Remove dashes from NDC** - Use `00930147` instead of `0093-0147`
4. **Use lowercase** - Try "aspirin" instead of "ASPIRIN"

For detailed help, see [TROUBLESHOOTING.md](TROUBLESHOOTING.md)

### Other Issues?

1. Check the console output for DEBUG messages when running the Flask app
2. Run the test script: `python3 test.py`
3. Check your internet connection
4. See [TROUBLESHOOTING.md](TROUBLESHOOTING.md) for more help

## Example Searches

These searches should work:

| Type | Search Term | Expected Results |
|------|-------------|-------------------|
| Generic Name | aspirin | Multiple aspirin products |
| Brand Name | tylenol | Tylenol products (acetaminophen) |
| NCN Code | 00930147 | Aspirin 500mg tablet |

## File Structure

```
.
├── app.py                    # Flask application and API endpoints
├── test.py                   # Example usage and testing
├── test_api.py              # Direct FDA API testing
├── quickstart.py            # Setup verification script
├── requirements.txt         # Python dependencies
├── README.md                # This file
├── TROUBLESHOOTING.md       # Troubleshooting guide
└── templates/
    └── index.html           # Web interface
```

## Data Source

Data is retrieved from the [FDA Drug API](https://open.fda.gov/apis/drug/ndc/), which is a public API with no authentication required.

## How to Get Help

1. **Check the console** - Look for DEBUG messages when searching
2. **Read TROUBLESHOOTING.md** - Common issues and solutions
3. **Run test.py** - See actual working searches
4. **Check FDA API docs** - https://open.fda.gov/apis/drug/ndc/

## License

This project uses the public FDA Drug API, which is in the public domain.
