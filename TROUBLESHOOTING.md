# FDA Medication Search App - Troubleshooting Guide

## Common Issues

### Medication Images Not Showing

The app shows medication images in three scenarios:

1. **Real Images from FDA RxImage API** - If available in the database
2. **Fallback Placeholder Images** - If RxImage doesn't have images for that medication
3. **Generic Icon** - For medications without images in the database

#### Why No Real Images?

The FDA RxImage API doesn't have images for all medications. This is normal and expected:
- Not all medications are photographed in the RxImage database
- Some medications may be new or less commonly photographed
- Generic versions may not have images while brand names do (and vice versa)

#### Solutions:

1. **Try a different medication** - Search for "aspirin" or other common medications to verify images work
2. **Try brand name vs generic name** - Sometimes one has images and the other doesn't
3. **Check the console** - When you search, the Flask console shows:
   - `DEBUG: RxImage NDC request - NDC: ..., Status: 200` - API was contacted
   - `DEBUG: Found 0 images...` - Database had no images
   - `DEBUG: No real images found, using placeholder...` - Fallback placeholder is being shown

### Understanding the Image Display

**Real Image (FDA RxImage):**
- Shows "Source: FDA RxImage" label
- Displays actual medication photos
- May show different forms or batches

**Placeholder Image:**
- Shows "Source: Placeholder" label
- Displays a gradient background with medication name
- Indicates no real image is available in FDA database
- Still useful for identifying the medication visually

## API Error 404

The FDA API returns 404 when no results are found. This is not always an error - it often just means the medication wasn't found with that search term.

### Solutions:

1. **Check Your Search Term**
   - Make sure you spelled the medication name correctly
   - Try removing special characters or numbers
   - Use generic names instead of brand names

2. **Try Different Search Types**
   - If searching by "Generic Name" returns 404, try "Brand Name"
   - For NDC codes, remove any dashes: `0093-0147` → search as `00930147`

3. **Example Searches That Should Work**
   ```
   Generic Name: "aspirin" (not "ASPIRIN")
   Brand Name: "tylenol" (not "TYLENOL")
   NDC Code: "00930147" (from original example, without dashes)
   ```

4. **Run the Command-Line Test**
   To verify the API is working:
   ```bash
   python3 test.py
   ```

## Checking Console Output

When running the Flask app (`python3 app.py`), watch the console for debug messages:

```
DEBUG: Search term: aspirin
DEBUG: Search type: generic_name
DEBUG: Query: generic_name:aspirin*
DEBUG: Status Code: 200
DEBUG: Fetching images for 10 medications...
DEBUG: RxImage NDC request - NDC: 0093-0147, Status: 200
DEBUG: RxImage parsed JSON - Type: <class 'dict'>, Keys: dict_keys([...])
DEBUG: Found 2 images from NDC search
```

**What these mean:**
- `Status Code: 200` = Search succeeded
- `Status Code: 404` = No results found for this search
- `Found X images` = Real images were found
- `using placeholder` = No real images, showing fallback
- `Status Code: 5xx` = FDA API server error

## Troubleshooting Checklist

### Images Not Showing

- [ ] Verify internet connection is working
- [ ] Try searching for a common medication (aspirin, tylenol)
- [ ] Check Flask console for DEBUG messages
- [ ] Look for "using placeholder" message - this means no FDA images exist
- [ ] Verify the image URL is valid by clicking it

### Search Not Returning Results

- [ ] Check spelling of medication name
- [ ] Remove special characters
- [ ] Try different search types (generic vs brand name)
- [ ] Use lowercase letters
- [ ] For NDC, remove dashes

### API Errors

- [ ] Check internet connection
- [ ] Try again - FDA API might be temporarily slow
- [ ] Check Flask console for detailed error messages
- [ ] Verify spelling and format

## Manual API Testing

You can test the APIs directly:

```bash
# Test FDA Medication API
curl "https://api.fda.gov/drug/ndc.json?search=generic_name:aspirin*&limit=5"

# Test FDA RxImage API
curl "https://rximage.nlm.nih.gov/api/rximage/1/rxnorm?ndc=0093-0147"

# Test with name
curl "https://rximage.nlm.nih.gov/api/rximage/1/rxnorm?name=aspirin"
```

## Getting Help

1. Check the console output for DEBUG messages
2. Look at this troubleshooting guide
3. Run `test.py` to see working examples
4. Check your internet connection
5. Try a different medication to isolate the issue
