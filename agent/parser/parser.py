from bs4 import BeautifulSoup as bs
from httpx import AsyncClient

class WebParser:
    """
    Class for parsing of web pages.
    """
    def __init__(self):
        self._client = AsyncClient()

    async def get_site_info(self, url: str) -> str:
        """
        Gets the useful text from web page.

        Args:
            url (str): url for web page to parse.

        Returns:
            str: useful text from web page.
        """
        return await self._parse(url)

    async def _parse(self, url: str) -> str:
        """
        Gets the html page and returns useful text from it.

        Args: 
            url (str):  url for web page to parse.

        Returns:
            str: useful text from web page.
        """
        response = await self._client.get(url)
        return self._extract_useful_text(response.text)

    @staticmethod
    def _extract_useful_text(html_content: str) -> str:
        """
        Extracts the useful text from html.

        Args:
            html_content (str): content of html page.

        Returns:
            str: extracted useful text.
        """
        soup = bs(html_content, 'html.parser')

        for tag in soup(['script', 'style', 'header', 'footer', 'nav', 'aside', 'meta', 'link']):
            tag.decompose()

        text = soup.get_text(separator=' ', strip=True)
        lines = (line.strip() for line in text.splitlines())
        chunks = (phrase.strip() for line in lines for phrase in line.split("  "))
        text = '\n'.join(chunk for chunk in chunks if chunk)

        return text
