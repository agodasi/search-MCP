import requests
from bs4 import BeautifulSoup
import logging

logger = logging.getLogger(__name__)

class ContentExtractor:
    """
    A class to extract text content from a given URL.
    """
    def __init__(self):
        pass

    def extract_text(self, url: str):
        """
        Fetches the URL and extracts the text content.
        """
        logger.info(f"Extracting content from: {url}")
        try:
            response = requests.get(url, timeout=10)
            response.raise_for_status()
            
            soup = BeautifulSoup(response.text, 'html.parser')
            
            # Remove script and style elements
            for script_or_style in soup(["script", "style"]):
                script_or_style.decompose()

            # Get text and clean up whitespace
            text = soup.get_text(separator=' ')
            lines = (line.strip() for line in text.splitlines())
            chunks = (phrase.strip() for line in lines for phrase in line.split("  "))
            text = '\n'.join(chunk for chunk in chunks if chunk)

            logger.info(f"Successfully extracted text from: {url}")
            return text
        except Exception as e:
            logger.error(f"Error during content extraction: {e}")
            raise e