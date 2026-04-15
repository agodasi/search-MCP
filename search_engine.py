from duckduckgo_search import DDGS
import logging

logger = logging.getLogger(__name__)

class SearchEngine:
    """
    A class to handle DuckDuckGo searches.
    """
    def __init__(self):
        self.ddgs = DDGS()

    def search(self, query: str, max_results: int = 5):
        """
        Performs a DuckDuckGo search and returns the results.
        """
        logger.info(f"Searching for: {query}")
        try:
            results = list(self.ddgs.text(query, max_results=max_results))
            logger.info(f"Found {len(results)} results for: {query}")
            return results
        except Exception as e:
            logger.error(f"Error during search: {e}")
            raise e