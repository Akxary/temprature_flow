from dataclasses import dataclass


@dataclass(frozen=True)
class Config:
    HOST = "127.0.0.1"
    PORT = 8585