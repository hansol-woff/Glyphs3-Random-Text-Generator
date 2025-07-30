#MenuTitle: Random Text Generator
# -*- coding: utf-8 -*-
__doc__="""
Fetches a random article from Wikipedia and displays its plain text content in the current Edit View via a simple UI.
"""

import GlyphsApp
import urllib.request
import urllib.parse
import json
import ssl
import webbrowser
from vanilla import FloatingWindow, Button, TextBox

def fetch_random_wikipedia_text(lang='en'):
    """
    Fetches a random article from Wikipedia in the specified language and returns its plain text and URL.
    """
    print(f"Fetching a random Wikipedia article in '{lang}'...")
    
    ssl_context = ssl._create_unverified_context()
    
    # 1. Get a random article title
    try:
        random_url = f"https://{lang}.wikipedia.org/w/api.php?action=query&list=random&format=json&rnnamespace=0&rnlimit=1"
        with urllib.request.urlopen(random_url, context=ssl_context) as response:
            random_data = json.loads(response.read().decode())
        
        random_title = random_data["query"]["random"][0]["title"]
        print(f"Found random article: '{random_title}'")
        
        # Create the article URL
        article_url = f"https://{lang}.wikipedia.org/wiki/{urllib.parse.quote(random_title.replace(' ', '_'))}"

    except Exception as e:
        error_msg = f"Error fetching random article title: {e}"
        print(error_msg)
        return None, None, error_msg

    # 2. Get the content of that article
    try:
        base_url = f"https://{lang}.wikipedia.org/w/api.php"
        params = {
            "action": "query",
            "format": "json",
            "titles": random_title,
            "prop": "extracts",
            "exintro": False,
            "explaintext": True,
            "redirects": 1,
        }
        content_url = f"{base_url}?{urllib.parse.urlencode(params)}"

        with urllib.request.urlopen(content_url, context=ssl_context) as response:
            content_data = json.loads(response.read().decode())

        pages = content_data["query"]["pages"]
        page_id = next(iter(pages))
        
        if page_id == "-1":
            error_msg = f"Error: Article '{random_title}' could not be found."
            print(error_msg)
            return None, None, error_msg

        extract = pages[page_id].get("extract", "")
        return extract, article_url, None

    except Exception as e:
        error_msg = f"An error occurred while fetching content: {e}"
        print(error_msg)
        return None, None, error_msg

class RandomTextGenerator(object):
    def __init__(self):
        if not Glyphs.font:
            Glyphs.showMacroWindow()
            print("Error: No font is open. Please open a font file first.")
            return

        self.w = FloatingWindow((320, 150), "Random Text Generator")
        
        self.w.descriptionText = TextBox((10, 10, -10, 30), "Click a button to fetch random text from Wikipedia (CC BY-SA 4.0).", sizeStyle='small')
        self.w.wikiENButton = Button((10, 45, -10, 25), "Wikipedia (EN)", callback=self.generate_text_callback)
        self.w.wikiKOButton = Button((10, 80, -10, 25), "Wikipedia (KO+EN)", callback=self.generate_text_callback)
        
        self.w.viewOriginalButton = Button((10, 115, -10, 25), "View Original Article", callback=self.view_original_callback)
        self.w.viewOriginalButton.enable(False)
        
        self.article_url = None

        self.w.open()

    def generate_text_callback(self, sender):
        Glyphs.clearLog()
        
        text = None
        error = None
        self.article_url = None
        self.w.viewOriginalButton.enable(False)

        if sender == self.w.wikiENButton:
            text, self.article_url, error = fetch_random_wikipedia_text(lang='en')
        elif sender == self.w.wikiKOButton:
            text, self.article_url, error = fetch_random_wikipedia_text(lang='ko')

        if error:
            Glyphs.showMacroWindow()
            print(f"Failed to fetch text: {error}")
            return

        if text:
            if Glyphs.font.currentTab:
                Glyphs.font.currentText = text
            else:
                Glyphs.font.newTab(text)
            print("Successfully displayed random text in the Edit View.")
            self.w.viewOriginalButton.enable(True)
        else:
            Glyphs.showMacroWindow()
            print("Failed to fetch or display text. The article might be empty.")

    def view_original_callback(self, sender):
        if self.article_url:
            webbrowser.open(self.article_url)

if 'Glyphs' in globals():
    RandomTextGenerator()
else:
    print("This script must be run from within Glyphs App.")
