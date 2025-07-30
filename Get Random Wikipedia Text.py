#MenuTitle: Get Random Wikipedia Text
# -*- coding: utf-8 -*-
__doc__="""
Fetches a random Wikipedia article and displays its plain text content in the current Edit View.
"""

import GlyphsApp
import urllib.request
import urllib.parse
import json
import ssl

def fetch_random_wikipedia_text():
    """
    Fetches a random article from Wikipedia and returns its plain text.
    """
    print("Fetching a random Wikipedia article...")
    
    # Create an SSL context that does not verify certificates
    # This is a workaround for the CERTIFICATE_VERIFY_FAILED error on macOS
    ssl_context = ssl._create_unverified_context()

    # 1. Get a random article title
    try:
        random_url = "https://en.wikipedia.org/w/api.php?action=query&list=random&format=json&rnnamespace=0&rnlimit=1"
        with urllib.request.urlopen(random_url, context=ssl_context) as response:
            random_data = json.loads(response.read().decode())
        
        random_title = random_data["query"]["random"][0]["title"]
        print(f"Found random article: '{random_title}'")

    except Exception as e:
        print(f"Error fetching random article title: {e}")
        Glyphs.showMacroWindow()
        return None

    # 2. Get the content of that article
    try:
        # Prepare URL for Wikipedia API
        base_url = "https://en.wikipedia.org/w/api.php"
        params = {
            "action": "query",
            "format": "json",
            "titles": random_title,
            "prop": "extracts",
            "exintro": False, # Get the full text, not just the intro
            "explaintext": True,
            "redirects": 1,
        }
        content_url = f"{base_url}?{urllib.parse.urlencode(params)}"

        with urllib.request.urlopen(content_url, context=ssl_context) as response:
            content_data = json.loads(response.read().decode())

        # Parse the JSON response
        pages = content_data["query"]["pages"]
        page_id = next(iter(pages))
        
        if page_id == "-1":
            print(f"Error: Article '{random_title}' could not be found after random selection.")
            Glyphs.showMacroWindow()
            return None

        extract = pages[page_id].get("extract", "")
        return extract

    except Exception as e:
        print(f"An error occurred while fetching content: {e}")
        Glyphs.showMacroWindow()
        return None

# --- Main execution ---
if Glyphs.font:
    # Fetch the text
    wikipedia_text = fetch_random_wikipedia_text()

    if wikipedia_text:
        # Put the text into the current tab
        Glyphs.font.currentText = wikipedia_text
        print("Successfully displayed random Wikipedia text in the Edit View.")
    else:
        # Error message is already printed by the function
        print("Failed to fetch or display Wikipedia text.")
        Glyphs.showMacroWindow()
else:
    print("Error: No font is open. Please open a font file first.")
    Glyphs.showMacroWindow()
