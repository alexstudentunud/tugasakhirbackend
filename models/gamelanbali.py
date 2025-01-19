from pydantic import BaseModel
from typing import List

class Audio(BaseModel):
    audio_name: str
    audio_path: str

class GamelanData(BaseModel):
    _id: str
    nama_gamelan: str
    golongan: str
    description: str
    upacara: List[str]
    audio_gamelan: List[Audio]
    instrument_id: List[str]
    status: str
    createdAt: str
    updatedAt: str

