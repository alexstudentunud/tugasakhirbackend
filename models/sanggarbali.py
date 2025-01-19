from pydantic import BaseModel
from bson import ObjectId

class SanggarData(BaseModel):
    _id: str
    image: str
    nama_sanggar: str
    alamat_lengkap: str
    no_telepon: str
    nama_jalan: str
    desa: str
    kecamatan: str
    kabupaten: str
    provinsi: str
    kode_pos: str
    id_creator: str
    createdAt: str
    status: str
    updatedAt: str
    deskripsi: str

    class Config:
        from_attributes = True  # Jika ada integrasi dengan ORM di masa depan
