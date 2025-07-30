#MenuTitle: Random Wikipedia Text Generator
# -*- coding: utf-8 -*-
__doc__="""
Fetches a random Wikipedia article and displays its plain text content in the current Edit View via a simple UI.
"""

import GlyphsApp
import urllib.request
import urllib.parse
import json
import ssl
from vanilla import FloatingWindow, Button

def fetch_random_wikipedia_text():
    """
    Fetches a random article from Wikipedia and returns its plain text and an error message if one occurs.
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
        error_msg = f"Error fetching random article title: {e}"
        print(error_msg)
        return None, error_msg

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
            error_msg = f"Error: Article '{random_title}' could not be found after random selection."
            print(error_msg)
            return None, error_msg

        extract = pages[page_id].get("extract", "")
        return extract, None

    except Exception as e:
        error_msg = f"An error occurred while fetching content: {e}"
        print(error_msg)
        return None, error_msg

class RandomTextGenerator(object):
    def __init__(self):
        if not Glyphs.font:
            Glyphs.showMacroWindow()
            print("Error: No font is open. Please open a font file first.")
            return

        # Window dimensions and title
        self.w = FloatingWindow((300, 80), "Random Text Generator")
        
        # UI Elements
        self.w.generateButton = Button((10, 10, -10, -10), "Generate Random Text", callback=self.generate_text_callback)
        
        # Open the window
        self.w.open()
        
        # Run once on startup
        self.generate_text_callback(None)

    def generate_text_callback(self, sender):
        # Clear the Macro Window for new output
        Glyphs.clearLog()
        
        # Fetch the text
        wikipedia_text, error = fetch_random_wikipedia_text()

        if error:
            Glyphs.showMacroWindow()
            print(f"Failed to fetch Wikipedia text: {error}")
            return

        if wikipedia_text:
            # Put the text into the current tab
            if Glyphs.font.currentTab:
                Glyphs.font.currentText = wikipedia_text
            else:
                Glyphs.font.newTab(wikipedia_text)
            print("Successfully displayed random Wikipedia text in the Edit View.")
        else:
            Glyphs.showMacroWindow()
            print("Failed to fetch or display Wikipedia text. The article might be empty.")

# --- Main execution ---
# Check if the script is running in Glyphs
if 'Glyphs' in globals():
    RandomTextGenerator()
else:
    print("This script must be run from within Glyphs App.")
