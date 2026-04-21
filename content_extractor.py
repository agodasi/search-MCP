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
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/123.0.0.0 Safari/537.36",
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8",
            "Accept-Language": "ja,en-US;q=0.9,en;q=0.8",
        }
        try:
            response = requests.get(url, timeout=15, headers=headers)
            response.raise_for_status()
            
            # 手動でエンコーディングを設定（Noneの場合はapparent_encodingを使用）
            if response.encoding is None or response.encoding == 'ISO-8859-1':
                response.encoding = response.apparent_encoding

            soup = BeautifulSoup(response.text, 'html.parser')
            
            # Remove script and style elements
            for script_or_style in soup(["script", "style", "header", "footer", "nav"]):
                script_or_style.decompose()

            # Get text and clean up whitespace
            text = soup.get_text(separator=' ')
            lines = (line.strip() for line in text.splitlines())
            chunks = (phrase.strip() for line in lines for phrase in line.split("  "))
            text = '\n'.join(chunk for chunk in chunks if chunk)

            logger.info(f"Successfully extracted text from: {url} (Length: {len(text)})")
            return text
        except Exception as e:
            logger.error(f"Error during content extraction: {e}")
            raise e