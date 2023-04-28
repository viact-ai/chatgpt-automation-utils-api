from fastapi import APIRouter
from utils import crawler_utils

router = APIRouter()


@router.get("/google_result")
def crawl_google_result(
    q: str,
    limit: int = 10,
    get_content: bool = False,
):
    results = crawler_utils.crawl_search_google(q, limit)
    if not get_content:
        return results

    response = []
    for result in results:
        result["text_content"] = crawler_utils.crawl_website(result["link"])[
            "text_content"
        ]
        response.append(result)
    return response


@router.get("/website")
def crawl_website_content(
    link: str,
):
    content = crawler_utils.crawl_website(link)

    return content
