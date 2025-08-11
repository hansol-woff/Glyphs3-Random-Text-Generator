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
from vanilla import FloatingWindow, Button, TextBox, PopUpButton

MIN_LENGTH = 100
MAX_LENGTH = 1000
MAX_RETRIES = 5

LANGUAGES = {
    "English": "en",
    "한국어": "ko",
    "日本語": "ja",
    "中文": "zh",
    "Deutsch": "de",
    "Français": "fr",
    "Español": "es",
    "Русский": "ru",
    "Tiếng Việt": "vi",
    "العربية": "ar"
}

def fetch_random_wikipedia_text(lang='en'):
    """
    Fetches a random article from Wikipedia, ensuring the text is within a reasonable length.
    Retries on temporary errors and only reports a final failure.
    """
    ssl_context = ssl._create_unverified_context()
    last_error = "No specific error was recorded."

    for i in range(MAX_RETRIES):
        print(f"Fetching a random Wikipedia article in '{lang}'... (Attempt {i+1}/{MAX_RETRIES})")
        
        try:
            # 1. Get a random article title
            random_url = f"https://{lang}.wikipedia.org/w/api.php?action=query&list=random&format=json&rnnamespace=0&rnlimit=1"
            with urllib.request.urlopen(random_url, context=ssl_context) as response:
                random_data = json.loads(response.read().decode())
            
            random_title = random_data["query"]["random"][0]["title"]
            print(f"Found random article: '{random_title}'")
            
            article_url = f"https://{lang}.wikipedia.org/wiki/{urllib.parse.quote(random_title.replace(' ', '_'))}"

            # 2. Get the content of that article
            base_url = f"https://{lang}.wikipedia.org/w/api.php"
            params = {
                "action": "query",
                "format": "json",
                "titles": random_title,
                "prop": "extracts",
                "explaintext": True,
                "redirects": 1,
            }
            content_url = f"{base_url}?{urllib.parse.urlencode(params)}"

            with urllib.request.urlopen(content_url, context=ssl_context) as response:
                content_data = json.loads(response.read().decode())

            pages = content_data["query"]["pages"]
            page_id = next(iter(pages))
            
            if page_id == "-1":
                print(f"Article '{random_title}' could not be found. Retrying...")
                continue

            extract = pages[page_id].get("extract", "")

            if len(extract) < MIN_LENGTH:
                print(f"Article is too short ({len(extract)} chars). Retrying for a longer one.")
                continue
            
            if len(extract) > MAX_LENGTH:
                print(f"Article is too long ({len(extract)} chars). Truncating to {MAX_LENGTH} chars.")
                extract = extract[:MAX_LENGTH]

            # Success!
            return extract, article_url, None

        except Exception as e:
            last_error = f"<{e.__class__.__name__}> {e}"
            # Silently retry
            continue
            
    # This part is reached only if the loop completes without returning successfully.
    final_error_msg = f"Failed to find a suitable article after {MAX_RETRIES} attempts. Last error: {last_error}"
    return None, None, final_error_msg

class RandomTextGenerator(object):
    def __init__(self):
        if not Glyphs.font:
            Glyphs.showMacroWindow()
            print("Error: No font is open. Please open a font file first.")
            return

        self.w = FloatingWindow((280, 180), "Random Text Generator")
        
        self.w.descriptionText = TextBox((10, 10, -10, 30), "Select a language and click Generate to get random text from Wikipedia (CC BY-SA 4.0).", sizeStyle='small')
        
        self.w.languageDropdown = PopUpButton((10, 45, -10, 25), list(LANGUAGES.keys()), callback=None)
        self.w.generateButton = Button((10, 80, -10, 25), "Generate Sample Text", callback=self.generate_text_callback)
        
        self.w.viewOriginalButton = Button((10, 115, -10, 25), "View Original Article", callback=self.view_original_callback)
        self.w.viewOriginalButton.enable(False)
        
        self.w.githubLink = Button((10, 150, 120, 20), "View on GitHub", callback=self.open_github_callback, sizeStyle='small')
        
        self.article_url = None

        self.w.open()

    def open_github_callback(self, sender):
        webbrowser.open("https://github.com/node-to-type/Glyphs3-Random-Text-Generator")

    def generate_text_callback(self, sender):
        Glyphs.clearLog()
        
        selected_language_name = self.w.languageDropdown.getItems()[self.w.languageDropdown.get()]
        lang_code = LANGUAGES[selected_language_name]
        
        text, self.article_url, error = fetch_random_wikipedia_text(lang=lang_code)

        self.w.viewOriginalButton.enable(False)

        if error:
            Glyphs.showMacroWindow()
            print(error)
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
