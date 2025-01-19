from pydantic import BaseModel
from typing import List

class AudioGamelanData(BaseModel):
    _id: str
    audio_name: str
    audio_path: str
    id_gamelan: str
    deskripsi: str
