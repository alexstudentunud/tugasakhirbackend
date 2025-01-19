from pydantic import BaseModel, Field
from typing import List
from datetime import time

class InstrumenData(BaseModel):
    _id: str
    nama_instrument: str 
    description: str
    trid_image: str
    fungsi: str
    image_instrumen: str
    status: str
    bahan: List[str]
    createdAt: str
    updatedAt: str