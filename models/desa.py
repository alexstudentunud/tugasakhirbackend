from pydantic import BaseModel
from typing import List

class Desa(BaseModel):
    _id: str
    nama_desa: str
    kecamatan_id: str

