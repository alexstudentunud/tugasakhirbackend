from pydantic import BaseModel
from typing import List

class Kabupaten(BaseModel):
    _id: str
    nama_kabupaten: str
    provinsi_id: str

