from pydantic import BaseModel
from typing import List

class Kecamatan(BaseModel):
    _id: str
    nama_kecamatan: str
    kabupaten_id: str

