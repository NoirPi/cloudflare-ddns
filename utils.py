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
        if os.path.exists(f'configs/config_{env}.json'):
            with open(f"configs/config_{env}.json", 'r', encoding='utf-8') as config:
                cfg_temp = json.load(config)
                cfg.update(cfg_temp)

        else:
            with open(f"configs/config_{env}.json", 'w+', encoding='utf-8') as conf:
                json.dump(default, conf)
                cfg.update(conf)


Path('./configs').mkdir(parents=True, exist_ok=True)
Config.cfg_load(os.getenv('cfg', 'dev'))
