from os import getenv

import dotenv
from hydra import compose, initialize
from omegaconf import DictConfig, OmegaConf

dotenv.load_dotenv()


def oc_env_resolver(key: str):
    return getenv(key, None)


OmegaConf.register_new_resolver("env", oc_env_resolver)


def get_config(module_name: str = None) -> DictConfig:
    with initialize(config_path="../config"):
        config = compose("app.yaml")
        if module_name:
            module_config = config.get(module_name, {})
            return module_config
        else:
            return config
