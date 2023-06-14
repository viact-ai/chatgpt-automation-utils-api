import base64
import json
from pathlib import Path

import requests
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from utils.config_utils import get_config
from utils.logger_utils import get_logger

config = get_config()

logger = get_logger()


def read_credentials_JSON_from_env():
    b64_str = config.googleapi.credentials_string
    try:
        return json.loads(base64.b64decode(b64_str).decode("utf-8"))
    except Exception as err:
        logger.exception(err)
        return None


def creds_from_tokens(
    token: str,
    refresh_token: str,
    expiry: str,
) -> Credentials:
    creds = Credentials.from_authorized_user_info(
        {
            "token": token,
            "refresh_token": refresh_token,
            "expiry": expiry,
            "client_id": config.googleapi.client_id,
            "client_secret": config.googleapi.client_secret,
        },
        list(config.googleapi.scopes),
    )

    return creds


def get_google_auth_flow(
    redirect_uri: str = None,
) -> InstalledAppFlow:
    creds_path = Path(config.googleapi.client_secrets_file)
    if not creds_path.exists():
        creds_data = read_credentials_JSON_from_env()
        if creds_data is None:
            raise Exception("No credentials file found")

        with creds_path.open("w") as f:
            json.dump(creds_data, f)
            logger.info('Wrote credentials to "%s"', creds_path)

    return InstalledAppFlow.from_client_secrets_file(
        client_secrets_file=str(creds_path),
        scopes=list(config.googleapi.scopes),
        redirect_uri=redirect_uri or config.googleapi.auth_callback_url,
    )


def get_google_auth_url(flow: InstalledAppFlow) -> str:
    auth_url, _ = flow.authorization_url(
        prompt="consent",
        access_type="offline",
        include_granted_scopes="true",
    )
    return auth_url


def get_google_user_profile(token: str) -> dict:
    try:
        resp = requests.get(
            "https://www.googleapis.com/oauth2/v1/userinfo?alt=json",
            headers={
                "Authorization": f"Bearer {token}",
            },
        )

        data = resp.json()
        return data
    except Exception as e:
        logger.exception(e)
        return None
