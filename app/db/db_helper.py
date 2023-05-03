import pymongo
from utils.config_utils import get_config
from utils.logger_utils import get_logger

config = get_config("db")

logger = get_logger()


def get_client():
    client = pymongo.MongoClient(
        host=config.host,
        port=int(config.port),
        username=config.username,
        password=config.password,
        authSource=config.database,
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
        logger.exception(err)
        return False
