import asyncio

from fastapi import APIRouter
from utils import crawler_utils

router = APIRouter()


@router.get("/google_result")
async def crawl_google_result(
    q: str,
    limit: int = 10,
    get_content: bool = False,
):
    results = await crawler_utils.crawl_search_google(q, limit)
    if not get_content:
        return results

    responses = await asyncio.gather(
        *map(
            crawler_utils.crawl_website,
            [r["link"] for r in results],
        )
    )

    result = []
    for resp, r in zip(responses, results):
        if resp is None:
            r["text_content"] = None
        else:
            content = resp["text_content"].strip()
            if content:
                r["text_content"] = content

        result.append(r)
    return result


@router.get("/website")
def crawl_website_content(
    link: str,
):
    content = crawler_utils.crawl_website(link)

    return content
