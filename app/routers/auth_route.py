from typing import Annotated, Optional

from fastapi import APIRouter, Cookie, HTTPException, Response
from fastapi.responses import JSONResponse, RedirectResponse
from google.auth.transport.requests import Request
from utils.auth_utils import (
    creds_from_tokens,
    get_google_auth_flow,
    get_google_auth_url,
    get_google_user_profile,
)
from utils.config_utils import get_config

router = APIRouter()

config = get_config()


@router.get("/sign_in_with_google")
def sign_in_with_google(
    response: Response,
    token: Annotated[str | None, Cookie()] = None,
    refresh_token: Annotated[str | None, Cookie()] = None,
    expiry: Annotated[str | None, Cookie()] = None,
):
    if token and refresh_token and expiry:
        # Request send with token attached in cookies
        creds = creds_from_tokens(token, refresh_token, expiry)

        if creds.valid:
            # Token valid, return to home page
            return RedirectResponse(
                url=config.app.frontend_url,
            )

        if creds.expired and creds.refresh_token:
            # Token is expired and refresh token is available
            creds.refresh(Request())

            response.set_cookie("token", creds.token)
            response.set_cookie("expiry", creds.expiry.isoformat())

            return JSONResponse(
                content={},
                headers=response.headers,
            )

        # Token is invalid or refresh token is not available
        flow = get_google_auth_flow()
        auth_url = get_google_auth_url(flow)

        return RedirectResponse(url=auth_url)

    # Request sent without token attached in cookies
    flow = get_google_auth_flow()
    auth_url = get_google_auth_url(flow)

    return RedirectResponse(url=auth_url)


@router.get("/google_profile")
def google_user_profile(
    response: Response,
    token: Annotated[str | None, Cookie()] = None,
    refresh_token: Annotated[str | None, Cookie()] = None,
    expiry: Annotated[str | None, Cookie()] = None,
):
    if not (token and refresh_token and expiry):
        raise HTTPException(status_code=401, detail="Unauthorized")

    creds = creds_from_tokens(token, refresh_token, expiry)
    if not creds.valid:
        if not (creds.expired and creds.refresh_token):
            # Token is invalid or refresh token is not available
            raise HTTPException(status_code=401, detail="Unauthorized")

        # Try to refresh token and get user profile
        creds.refresh(Request())
        profile = get_google_user_profile(creds.token)
        if not profile:
            raise HTTPException(
                status_code=500,
                detail="Failed to get user profile from Google",
            )

        response.set_cookie("token", creds.token)
        response.set_cookie("expiry", creds.expiry.isoformat())

        return JSONResponse(
            content={
                "status": "success",
                "profile": profile,
            },
            headers=response.headers,
        )

    profile = get_google_user_profile(creds.token)
    if not profile:
        raise HTTPException(
            status_code=500,
            detail="Failed to get user profile from Google",
        )

    return {
        "status": "success",
        "profile": profile,
    }


@router.get("/google_auth_callback")
def callback(
    response: Response,
    state: str,
    code: str,
    scope,
    error: Optional[str] = None,
):
    if error:
        raise HTTPException(
            status_code=401,
            detail=f"Failed to authenticate: {error}",
        )

    flow = get_google_auth_flow()

    try:
        flow.fetch_token(code=code)
    except Exception as e:
        raise HTTPException(
            status_code=401,
            detail=f"Failed to fetch token: {e}",
        )

    creds = flow.credentials

    response.set_cookie(key="token", value=creds.token)
    response.set_cookie(key="refresh_token", value=creds.refresh_token)
    response.set_cookie(key="expiry", value=creds.expiry.isoformat())

    return {
        "status": "success",
        "data": {
            "token": creds.token,
            "refresh_token": creds.refresh_token,
            "expiry": creds.expiry.isoformat(),
        },
    }


@router.get("/validate_token")
def validate(
    response: Response,
    token: Annotated[str | None, Cookie()] = None,
    refresh_token: Annotated[str | None, Cookie()] = None,
    expiry: Annotated[str | None, Cookie()] = None,
):
    if not (token and refresh_token and expiry):
        raise HTTPException(status_code=401, detail="Unauthorized")

    creds = creds_from_tokens(token, refresh_token, expiry)

    if creds.valid:
        return Response(
            content=None,
            status_code=200,
        )

    if creds.expired and creds.refresh_token:
        creds.refresh(Request())

        response.set_cookie("token", creds.token)
        response.set_cookie("expiry", creds.expiry.isoformat())

        return Response(
            content=None,
            status_code=200,
            headers=response.headers,
        )

    raise HTTPException(status_code=401, detail="Unauthorized")


@router.get("/sign_out")
def logout(response: Response):
    response.delete_cookie(key="token")
    response.delete_cookie(key="refresh_token")
    response.delete_cookie(key="expiry")

    return JSONResponse(
        content={
            "status": "success",
            "redirect_url": config.app.frontend_url,
        },
        headers=response.headers,
    )
