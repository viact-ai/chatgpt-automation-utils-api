from typing import Any, Coroutine, TypedDict

from bs4 import BeautifulSoup
from utils.http_helper import async_request
from utils.logger_utils import get_logger

logger = get_logger()


class SearchItemResult(TypedDict):
    title: str
    link: str
    description: str


async def crawl_search_google(
    search_term: str,
    limit=5,
) -> list[SearchItemResult]:
    """Crawl result from google search

    Args:
        search_term (str): keywords to search, seperate by space
        limit (int, optional): number of result item to get from search
        result. Defaults to 10.

    Returns:
        list[SearchItemResult]: List of result

        SearchItemResult: Dict of result item
        {
            "title": str,
            "link": str,
            "description": str,
        }

    Code from quora: https://www.quora.com/How-do-I-crawl-Google-results-with-scrapy
    """

    # https://docs.python-requests.org/en/master/user/quickstart/#passing-parameters-in-urls
    params = {
        "q": search_term,
        "hl": "en",  # language
        "gl": "us",  # country of the search, US -> USA
        "start": 0,  # number page by default up to 0
        # "filter": 0       # shows more than 10 pages.
        # By default up to ~10-13 if filter = 1.
    }

    # https://docs.python-requests.org/en/master/user/quickstart/#custom-headers
    headers = {
        "User-Agent": (
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
            " (KHTML, like Gecko) Chrome/106.0.0.0 Safari/537.36"
        )
    }

    page_num = 0
    website_description_data = []
    while True:
        page_num += 1
        logger.info(f"page: {page_num}")

        html = await async_request(
            "https://www.google.com/search",
            params=params,
            headers=headers,
            timout=30,
        )

        soup = BeautifulSoup(html.text, "lxml")

        for result in soup.select(".tF2Cxc"):
            if len(website_description_data) >= limit:
                break

            title = result.select_one("h3").text
            link = result.select_one("a")["href"]
            try:
                description = result.select_one(".VwiC3b").text
            except Exception as err:
                logger.exception(err)
                description = None

            website_description_data.append(
                {
                    "title": title,
                    "link": link,
                    "description": description,
                }
            )

        if len(website_description_data) >= limit:
            break

        if soup.select_one(".d6cvqb a[id=pnnext]"):
            params["start"] += 10
        else:
            break

    return website_description_data


class WebContentResult(TypedDict):
    title: str
    description: str
    text_content: str


async def crawl_website(
    link: str,
) -> Coroutine[Any, Any, WebContentResult | None]:
    """Crawl website content

    Args:
        link (str): website link

    Returns:
        WebContentResult: website content

        WebContentResult: Dict of website content
        {
            "title": str,
            "description": str,
            "text_content": str,
        }
    """

    try:
        response = await async_request(link, timout=30)
    except Exception as err:
        logger.exception(err)
        return

    soup = BeautifulSoup(response.content, "html.parser")

    # Find the title and description tags in the HTML
    title_tag = soup.find("title")
    description_tag = soup.find("meta", attrs={"name": "description"})

    # Extract the text content from the tags
    title = title_tag.get_text() if title_tag else ""
    description = description_tag["content"] if description_tag else ""

    # Find all the text content in the HTML using the get_text() method
    text_content = soup.get_text()

    text_content = soup.get_text().replace("\n", " ").replace("\r", "")
    return {
        "title": title,
        "description": description,
        "text_content": text_content,
    }
