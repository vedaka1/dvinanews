from dataclasses import dataclass
from datetime import datetime


@dataclass
class News:
    link: str
    posted_at: datetime
    title: str
