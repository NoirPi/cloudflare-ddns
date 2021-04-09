import json
import os
from pathlib import Path

cfg = {}

default = json.load(open("../configs/config_example.json", "r"))


class Config:

    @staticmethod
    def domains() -> dict:
        """
        Returns domains out of the config
        :return domains:
        """
        return cfg['Domains']

    @staticmethod
    def token() -> str:
        """
        Returns cloudflare token
        :return cloudflare token:
        """
        return os.getenv("Token", cfg['API'].get('Token', "No Token provided!"))

    @staticmethod
    def ip_urls() -> dict:
        """
        Returns IP urls
        :return ip_urls:
        """
        return cfg["IPURLS"]

    @staticmethod
    def cfg_load(env="example"):
        """Load the Config file for the ddns or create one if it doesnt exists"""
        config_file = config_basepath / f'config_{env}.json'
        if config_file.exists():
            with config_file.open(mode='r', encoding='utf-8') as config:
                cfg_temp = json.load(config)
                cfg.update(cfg_temp)

        else:
            with config_file.open(mode='w+', encoding='utf-8') as conf:
                json.dump(default, conf)
                cfg.update(conf)
            print(f"Written default config to {config_file.resolve()}. Make sure to edit it")


if os.name == 'nt':
    config_basepath = Path.home() / 'config' / 'ddns'
else:
    config_basepath = Path('/') / 'etc' / 'ddns'

config_basepath.mkdir(parents=True, exist_ok=True)
Config.cfg_load(os.getenv('cfg', 'multiple'))
