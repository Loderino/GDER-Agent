from httpx import AsyncClient
from bs4 import BeautifulSoup as bs


class WebParser:
    def __init__(self):
        self._client = AsyncClient()

    async def get_site_info(self, url: str) -> str:
        """Получает информацию с сайта, включая весь текстовый контент.

        Args:
            url: ссылка для парсинга.

        Returns:
            весь текст с указанной страницы.
        """
        return await self._parse(url)



    async def _parse(self, url):
        """Приватный метод для запроса и парсинга."""
        response = await self._client.get(url)
        return self._extract_useful_text(response.text)

    @staticmethod
    def _extract_useful_text(html_content):
        """Статический метод для извлечения текста из HTML."""
        soup = bs(html_content, 'html.parser')

        for tag in soup(['script', 'style', 'header', 'footer', 'nav', 'aside', 'meta', 'link']):
            tag.decompose()

        text = soup.get_text(separator=' ', strip=True)
        lines = (line.strip() for line in text.splitlines())
        chunks = (phrase.strip() for line in lines for phrase in line.split("  "))
        text = '\n'.join(chunk for chunk in chunks if chunk)

        return text
