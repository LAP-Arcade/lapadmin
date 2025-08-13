from pydantic import BaseModel
from typing import Optional, List
from string import Template
from datetime import datetime, timedelta

import yaml
import os

from googleapiclient.discovery import build
from google_auth_oauthlib.flow import InstalledAppFlow
from google.oauth2.credentials import Credentials
from google.auth.transport.requests import Request

SCOPES = ["https://www.googleapis.com/auth/youtube.force-ssl"]

flow = InstalledAppFlow.from_client_secrets_file(
	"keys/client_secret.json", SCOPES
)

TOKEN_FILE = "keys/token.json"

if os.path.exists(TOKEN_FILE):
    creds = Credentials.from_authorized_user_file(TOKEN_FILE, SCOPES)
    creds.refresh(Request())
else:
    creds = flow.run_local_server()
    with open(TOKEN_FILE, "w") as token:
        token.write(creds.to_json())

youtube = build("youtube", "v3", credentials=creds)

# from app import DATA_DIR
from pathlib import Path
from google.oauth2.credentials import Credentials
DATA_DIR = Path("data").resolve()


class YoutubeStream(BaseModel):
    title: str
    description: str
    id: str
    url: str
    video_embed_url: Optional[str] = None
    chat_iframe_url: Optional[str] = None
    playing: bool
    created: datetime
    started: Optional[datetime] = None
    ended: Optional[datetime] = None

    @property
    def playing(self) -> bool:
        return self.started is not None and self.ended is None

    def start(self):
        if self.playing:
            raise Exception("Stream is already playing.")

        self.started = datetime.now()
        self.playing = True

        youtube.liveBroadcasts().transition(
            broadcastStatus="live",
            id=self.id,
            part="status"
        ).execute()

        print(f'Started stream: {self.title}')

    def stop(self):
        print(f'Stopping stream: {self.title}')


class GameStreamEntry(BaseModel):
    game: str
    playlist: Optional[str] = None
    unlisted: Optional[bool] = False


class GameStreamConfig(BaseModel):
    entries: List[GameStreamEntry]
    title: str
    description: str


class GameStream(BaseModel):
    game: str
    playlist: Optional[str] = None
    unlisted: Optional[bool] = False
    title: str
    description: str

    @classmethod
    def from_entry(
        cls,
        entry: GameStreamEntry,
        title_template: str,
        desc_template: str
    ) -> "GameStream":
        context = {"game": entry.game}

        return cls(
            game=entry.game,
            playlist=entry.playlist,
            unlisted=entry.unlisted,
            title=Template(title_template).substitute(context),
            description=Template(desc_template).substitute(context),
        )

    def get_latest_stream(self) -> Optional[YoutubeStream]:
        return YoutubeStream(
            title="testLatest",
            description="test",
            url="https://www.youtube.com/watch?v=test",
            video_embed_url="https://www.youtube.com/embed/test",
            chat_iframe_url="https://www.youtube.com/live_chat?is_popout=1&v=test",
            playing=False,
            created=datetime.now(),
            started=datetime.now(),
            ended=None,
        )

    def create(self) -> YoutubeStream:
        stream = youtube.liveBroadcasts().insert(
            part="snippet,status",
            body={
                "snippet": {
                    "title": self.title,
                    "description": self.description,
                    "scheduledStartTime": datetime.now().isoformat(),
                },
                "content_details": {
                    "enableAutoStart": True,
                    "enableAutoStop": True,
                },
                "cdn": {
                    "format": "1080p",
                    "frameRate": "60fps",
                    "ingestionType": "rtmp",
                },
                "status": {
                    "privacyStatus": "unlisted" if self.unlisted else "public",
                },
            }
        ).execute()

        print(f'Created stream: {stream}')

        return YoutubeStream(
            title=self.title,
            description=self.description,
            id=stream["id"],
            url=f"https://www.youtube.com/watch?v={stream['id']}",
            video_embed_url=f"https://www.youtube.com/embed/{stream['id']}",
            chat_iframe_url=f"https://www.youtube.com/live_chat?is_popout=1&v={stream['id']}",
            playing=False,
            created=datetime.now(),
            started=None,
            ended=None,
        )


def load_game_stream_config() -> GameStreamConfig:
    with (DATA_DIR / "streams.yml").open() as f:
        data = yaml.safe_load(f)["streams"]

    return GameStreamConfig(**data)


def should_create_stream(
        next_closing_time: datetime,
        now: Optional[datetime] = None
) -> bool:
    now = now or datetime.now()
    return (next_closing_time - now) >= timedelta(minutes=30)


def get() -> List[GameStream]:
    config = load_game_stream_config()
    return [
        GameStream.from_entry(entry, config.title, config.description)
        for entry in config.entries
    ]


def start():
    for stream in get():
        yt_stream = stream.get_latest_stream() or stream.create()
        if yt_stream.ended:
            yt_stream = stream.create()
        yt_stream.start()


start()