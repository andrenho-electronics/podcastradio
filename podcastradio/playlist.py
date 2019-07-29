from dataclasses import dataclass

@dataclass
class PlaylistItem:
    filename:     str
    title:        str
    current_time: float = 0.0

@dataclass
class Playlist:
    items:     List[PlaylistItem] = field(default_factory=list)
    current:   int                = -1
    status:    str                = 'stopped'

