from typing import Annotated
from urllib.parse import unquote

from fastapi import Cookie, HTTPException
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from utils.auth_utils import creds_from_tokens


async def verify_credentials(
    token: Annotated[str | None, Cookie()] = None,
    refresh_token: Annotated[str | None, Cookie()] = None,
    expiry: Annotated[str | None, Cookie()] = None,
) -> Credentials | None:
    if expiry:
        expiry = unquote(expiry)

    if not (token and refresh_token and expiry):
        raise HTTPException(status_code=401, detail="Unauthorized")

    creds = creds_from_tokens(token, refresh_token, expiry)

    if creds.valid:
        return creds

    if creds.expired and creds.refresh_token:
        creds.refresh(Request())

        return creds

    raise HTTPException(status_code=401, detail="Unauthorized")
