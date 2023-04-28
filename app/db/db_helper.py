import urllib.parse

import pymongo
from utils.config_utils import get_config

config = get_config("db")


def get_client():
    client = pymongo.MongoClient(
        "mongodb://{}:{}@{}:{}/{}?authSource=admin".format(
            config.username,
            config.password,
            config.host,
            config.port,
            config.database,
        ),
        serverSelectionTimeoutMS=config.server_selection_timeout_ms,
        directConnection=config.direct_connection,
        tls=config.tls,
        tlsInsecure=config.tls_insecure,
    )
    return client


def test_connection(client: pymongo.MongoClient) -> bool:
    try:
        client.server_info()
        return True
    except Exception as err:
        print(err)
        return False
