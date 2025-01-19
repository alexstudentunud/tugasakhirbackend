from pydantic import BaseModel
from typing import List

class AudioInstrumenData(BaseModel):
    _id: str
    audio_name: str
    audio_path: str
    id_instrumen: str
