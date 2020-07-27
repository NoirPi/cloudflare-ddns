import json
import os
from pathlib import Path

cfg = {}

default = {
    "API": {
        "Token": "EeGbyD6UTlCjECrXDUZ3td7lnQKBm3W2b4leZ2CyPW",
        "ZoneID": "oTsvYKAs3NudvxFztjgEuNRpuLzthJbs",
        "update_timer": 120
    },
    "Domains": [
        {
            "name": "www.example.com",
            "type": "A",
            "proxied": True,
            "create": True
        },
        {
            "name": "www.example.com",
            "type": "AAAA",
            "proxied": True,
            "create": True
        },
    ]
}


class Config:

    @staticmethod
    def domains():
        return cfg['Domains']

    @staticmethod
    def token():
        return os.getenv("Token", cfg['API'].get('Token', "No Token provided!"))

    @staticmethod
    def zoneid():
        return os.getenv("ZoneID", cfg['API'].get('ZoneID', "No ZoneID provided!"))

    @staticmethod
    def timer():
        return os.getenv("Timer", cfg['API'].get('update_timer', 120))

    @staticmethod
    def cfg_load(env="example"):
        """Load the Config file for the Bot or create one if it doesnt exists"""
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
Config.cfg_load(os.getenv('cfg', 'example'))
