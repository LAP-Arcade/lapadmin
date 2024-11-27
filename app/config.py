from pathlib import Path

import yaml

PATH = Path("config.yml")


class Config:
    DISCORD_CLIENT_ID: str
    DISCORD_CLIENT_SECRET: str
    DEFAULT_ENTRY: str = "lap2"

    def __init__(self):
        if not PATH.exists():
            print(f"Creating {PATH} with default values...")
            with PATH.open("w") as f:
                yaml.safe_dump(
                    {
                        "DISCORD_CLIENT_ID": False,
                        "DISCORD_CLIENT_SECRET": "xxxx",
                    },
                    f,
                )
        with PATH.open() as f:
            data = yaml.safe_load(f)
        for key, value in data.items():
            setattr(self, key, value)
