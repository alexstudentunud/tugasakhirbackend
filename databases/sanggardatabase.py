from models.sanggarbali import *
from databases.alamatdatabase import fetch_nama_alamat_by_id_desa
from motor.motor_asyncio import AsyncIOMotorClient
from pymongo.mongo_client import MongoClient
from pymongo.server_api import ServerApi
from bson import ObjectId
import re
import time
from datetime import datetime
import cloudinary
import cloudinary.uploader
from cloudinary.utils import cloudinary_url
from typing import List

uri = "mongodb://alexbramartha14:WCknO6oCCiM8r3qC@tagamelanbaliakhir-shard-00-00.zx7dr.mongodb.net:27017,tagamelanbaliakhir-shard-00-01.zx7dr.mongodb.net:27017,tagamelanbaliakhir-shard-00-02.zx7dr.mongodb.net:27017/?ssl=true&replicaSet=atlas-qfuxr3-shard-0&authSource=admin&retryWrites=true&w=majority&appName=TAGamelanBaliAkhir"
client = AsyncIOMotorClient(uri)

database = client["tugas-akhir-data"]

collection = database["sanggar-gamelan-new"]
collection_status = database["status"]

async def get_status():
    status = []

    response = collection_status.find({})
    
    async for response_status in response:
        status_data = {
            "_id": str(response_status["_id"]),
            "status": response_status["status"]
        }
        status.append(status_data)

    return {"status_list": status}

async def fetch_all_sanggar():
    sanggar = []

    cursor_id = collection.find({})

    idDesa = []
    async for deseid in cursor_id:  
        idDesa.append(deseid["desa_id"]) 

    alamat_lengkap_nama = await fetch_nama_alamat_by_id_desa(idDesa)
    
    cursor = collection.find({})
    if alamat_lengkap_nama:
        async for document in cursor:
            desa_data = alamat_lengkap_nama.get(document["desa_id"], {})

            ts = document["createdAt"]
            
            dt = datetime.fromtimestamp(ts)
            tanggal = dt.date()
            waktu = dt.time()

            updateTs = document["updatedAt"]
            updateDt = datetime.fromtimestamp(updateTs)
            updateTanggal = updateDt.date()
            updateWaktu = updateDt.time()

            # Buat alamat lengkap
            alamat_lengkap = f"{document['nama_jalan']}, Desa {desa_data.get('nama_desa', 'Tidak Diketahui')}, Kec. {desa_data.get('kecamatan', 'Tidak Diketahui')}, Kab. {desa_data.get('kabupaten', 'Tidak Diketahui')}, {desa_data.get('provinsi', 'Tidak Diketahui')} {document['kode_pos']}"
            
            # Buat data sanggar
            sanggar_data = {
                "_id": str(document["_id"]),
                "image": document["image"],
                "nama_sanggar": document["nama_sanggar"],
                "alamat_lengkap": alamat_lengkap,
                "no_telepon": document["no_telepon"],
                "nama_jalan": document["nama_jalan"],
                "desa": desa_data.get("nama_desa", "Tidak Diketahui"),
                "kecamatan": desa_data.get("kecamatan", "Tidak Diketahui"),
                "kabupaten": desa_data.get("kabupaten", "Tidak Diketahui"),
                "provinsi": desa_data.get("provinsi", "Tidak Diketahui"),
                "kode_pos": document["kode_pos"],
                "id_creator": document["user_id"],
                "status": document["status_id"],
                "createdAt": dt,
                "createdDate": tanggal,
                "createdTime": waktu,
                "updatedAt": updateDt,
                "updatedDate": updateTanggal,
                "updateTime": updateWaktu,
                "deskripsi": document["deskripsi"],
                "id_desa": document["desa_id"],
                "gamelan_id": document["gamelan_id"]
            }

            sanggar.append(sanggar_data)
    
    return {
        "sanggar_data": sanggar
    }


async def fetch_one_sanggar(id: str):
    object_id = ObjectId(id)
    document = await collection.find_one({"_id": object_id})
    image_path = document.get("image")
    return image_path

async def fetch_sanggar_specific_by_id(id: str):
    object_id = ObjectId(id)
    sanggar = []
    cursor_id = collection.find({"_id": object_id})
    
    idDesa = []
    async for deseid in cursor_id:  
        idDesa.append(deseid["desa_id"]) 

    alamat_lengkap_nama = await fetch_nama_alamat_by_id_desa(idDesa)
    
    cursor = collection.find({"_id": object_id})
    if alamat_lengkap_nama:
        async for document in cursor:
            desa_data = alamat_lengkap_nama.get(document["desa_id"], {})

            ts = document["createdAt"]
            
            dt = datetime.fromtimestamp(ts)
            tanggal = dt.date()
            waktu = dt.time()

            updateTs = document["updatedAt"]
            updateDt = datetime.fromtimestamp(updateTs)
            updateTanggal = updateDt.date()
            updateWaktu = updateDt.time()

            # Buat alamat lengkap
            alamat_lengkap = f"{document['nama_jalan']}, Desa {desa_data.get('nama_desa', 'Tidak Diketahui')}, Kec. {desa_data.get('kecamatan', 'Tidak Diketahui')}, Kab. {desa_data.get('kabupaten', 'Tidak Diketahui')}, {desa_data.get('provinsi', 'Tidak Diketahui')} {document['kode_pos']}"
            
            # Buat data sanggar
            sanggar_data = {
                "_id": str(document["_id"]),
                "image": document["image"],
                "nama_sanggar": document["nama_sanggar"],
                "alamat_lengkap": alamat_lengkap,
                "no_telepon": document["no_telepon"],
                "nama_jalan": document["nama_jalan"],
                "desa": desa_data.get("nama_desa", "Tidak Diketahui"),
                "kecamatan": desa_data.get("kecamatan", "Tidak Diketahui"),
                "kabupaten": desa_data.get("kabupaten", "Tidak Diketahui"),
                "provinsi": desa_data.get("provinsi", "Tidak Diketahui"),
                "kode_pos": document["kode_pos"],
                "id_creator": document["user_id"],
                "status": document["status_id"],
                "createdAt": dt,
                "createdDate": tanggal,
                "createdTime": waktu,
                "updatedAt": updateDt,
                "updatedDate": updateTanggal,
                "updateTime": updateWaktu,
                "deskripsi": document["deskripsi"],
                "id_desa": document["desa_id"],
                "gamelan_id": document["gamelan_id"]
            }

            sanggar.append(sanggar_data)
    
    return {
        "sanggar_data": sanggar
    }

async def fetch_sanggar_specific(name: str):
    sanggar = []
    cursor_id = collection.find({"nama_sanggar": {"$regex": f"(?i){name}"}})
    
    idDesa = []
    async for deseid in cursor_id:  
        idDesa.append(deseid["desa_id"]) 

    alamat_lengkap_nama = await fetch_nama_alamat_by_id_desa(idDesa)
    
    cursor = collection.find({"nama_sanggar": {"$regex": f"(?i){name}"}})
    if alamat_lengkap_nama:
        async for document in cursor:
            desa_data = alamat_lengkap_nama.get(document["desa_id"], {})

            ts = document["createdAt"]
            
            dt = datetime.fromtimestamp(ts)
            tanggal = dt.date()
            waktu = dt.time()

            updateTs = document["updatedAt"]
            updateDt = datetime.fromtimestamp(updateTs)
            updateTanggal = updateDt.date()
            updateWaktu = updateDt.time()

            # Buat alamat lengkap
            alamat_lengkap = f"{document['nama_jalan']}, Desa {desa_data.get('nama_desa', 'Tidak Diketahui')}, Kec. {desa_data.get('kecamatan', 'Tidak Diketahui')}, Kab. {desa_data.get('kabupaten', 'Tidak Diketahui')}, {desa_data.get('provinsi', 'Tidak Diketahui')} {document['kode_pos']}"
            
            # Buat data sanggar
            sanggar_data = {
                "_id": str(document["_id"]),
                "image": document["image"],
                "nama_sanggar": document["nama_sanggar"],
                "alamat_lengkap": alamat_lengkap,
                "no_telepon": document["no_telepon"],
                "nama_jalan": document["nama_jalan"],
                "desa": desa_data.get("nama_desa", "Tidak Diketahui"),
                "kecamatan": desa_data.get("kecamatan", "Tidak Diketahui"),
                "kabupaten": desa_data.get("kabupaten", "Tidak Diketahui"),
                "provinsi": desa_data.get("provinsi", "Tidak Diketahui"),
                "kode_pos": document["kode_pos"],
                "id_creator": document["user_id"],
                "status": document["status_id"],
                "createdAt": dt,
                "createdDate": tanggal,
                "createdTime": waktu,
                "updatedAt": updateDt,
                "updatedDate": updateTanggal,
                "updateTime": updateWaktu,
                "deskripsi": document["deskripsi"],
                "id_desa": document["desa_id"],
                "gamelan_id": document["gamelan_id"]
            }

            sanggar.append(sanggar_data)
    
    return {
        "sanggar_data": sanggar
    }

async def fetch_sanggar_specific_by_id_creator(id: str):
    sanggar = []
    cursor_id = collection.find({"user_id": id})
    
    idDesa = []
    async for deseid in cursor_id:  
        idDesa.append(deseid["desa_id"]) 

    alamat_lengkap_nama = await fetch_nama_alamat_by_id_desa(idDesa)
    
    cursor = collection.find({"user_id": id})
    if alamat_lengkap_nama:
        async for document in cursor:
            desa_data = alamat_lengkap_nama.get(document["desa_id"], {})

            ts = document["createdAt"]
            
            dt = datetime.fromtimestamp(ts)
            tanggal = dt.date()
            waktu = dt.time()

            updateTs = document["updatedAt"]
            updateDt = datetime.fromtimestamp(updateTs)
            updateTanggal = updateDt.date()
            updateWaktu = updateDt.time()

            # Buat alamat lengkap
            alamat_lengkap = f"{document['nama_jalan']}, Desa {desa_data.get('nama_desa', 'Tidak Diketahui')}, Kec. {desa_data.get('kecamatan', 'Tidak Diketahui')}, Kab. {desa_data.get('kabupaten', 'Tidak Diketahui')}, {desa_data.get('provinsi', 'Tidak Diketahui')} {document['kode_pos']}"
            
            # Buat data sanggar
            sanggar_data = {
                "_id": str(document["_id"]),
                "image": document["image"],
                "nama_sanggar": document["nama_sanggar"],
                "alamat_lengkap": alamat_lengkap,
                "no_telepon": document["no_telepon"],
                "nama_jalan": document["nama_jalan"],
                "desa": desa_data.get("nama_desa", "Tidak Diketahui"),
                "kecamatan": desa_data.get("kecamatan", "Tidak Diketahui"),
                "kabupaten": desa_data.get("kabupaten", "Tidak Diketahui"),
                "provinsi": desa_data.get("provinsi", "Tidak Diketahui"),
                "kode_pos": document["kode_pos"],
                "id_creator": document["user_id"],
                "status": document["status_id"],
                "createdAt": dt,
                "createdDate": tanggal,
                "createdTime": waktu,
                "updatedAt": updateDt,
                "updatedDate": updateTanggal,
                "updateTime": updateWaktu,
                "deskripsi": document["deskripsi"],
                "id_desa": document["desa_id"],
                "gamelan_id": document["gamelan_id"]
            }

            sanggar.append(sanggar_data)
    
    return {
        "sanggar_data": sanggar
    }

async def fetch_sanggar_by_filter(id: str, statusId: list[str]):
    sanggar = []
    
    if statusId:
        statusId = [re.sub(r'^"|"$', '', status) for status in statusId]

    cursor_id = collection.find({"user_id": id, "status_id": {"$in": statusId}})
    
    idDesa = []
    async for deseid in cursor_id:  
        idDesa.append(deseid["desa_id"]) 

    alamat_lengkap_nama = await fetch_nama_alamat_by_id_desa(idDesa)
    
    cursor = collection.find({"user_id": id, "status_id": {"$in": statusId}})
    if alamat_lengkap_nama:
        async for document in cursor:
            desa_data = alamat_lengkap_nama.get(document["desa_id"], {})

            ts = document["createdAt"]
            
            dt = datetime.fromtimestamp(ts)
            tanggal = dt.date()
            waktu = dt.time()

            updateTs = document["updatedAt"]
            updateDt = datetime.fromtimestamp(updateTs)
            updateTanggal = updateDt.date()
            updateWaktu = updateDt.time()

            # Buat alamat lengkap
            alamat_lengkap = f"{document['nama_jalan']}, Desa {desa_data.get('nama_desa', 'Tidak Diketahui')}, Kec. {desa_data.get('kecamatan', 'Tidak Diketahui')}, Kab. {desa_data.get('kabupaten', 'Tidak Diketahui')}, {desa_data.get('provinsi', 'Tidak Diketahui')} {document['kode_pos']}"
            
            # Buat data sanggar
            sanggar_data = {
                "_id": str(document["_id"]),
                "image": document["image"],
                "nama_sanggar": document["nama_sanggar"],
                "alamat_lengkap": alamat_lengkap,
                "no_telepon": document["no_telepon"],
                "nama_jalan": document["nama_jalan"],
                "desa": desa_data.get("nama_desa", "Tidak Diketahui"),
                "kecamatan": desa_data.get("kecamatan", "Tidak Diketahui"),
                "kabupaten": desa_data.get("kabupaten", "Tidak Diketahui"),
                "provinsi": desa_data.get("provinsi", "Tidak Diketahui"),
                "kode_pos": document["kode_pos"],
                "id_creator": document["user_id"],
                "status": document["status_id"],
                "createdAt": dt,
                "createdDate": tanggal,
                "createdTime": waktu,
                "updatedAt": updateDt,
                "updatedDate": updateTanggal,
                "updateTime": updateWaktu,
                "deskripsi": document["deskripsi"],
                "id_desa": document["desa_id"],
                "gamelan_id": document["gamelan_id"]
            }

            sanggar.append(sanggar_data)
    
    return {
        "sanggar_data": sanggar
    }

async def create_sanggar_data(
    image: str, 
    nama: str,
    nama_jalan: str,
    kode_pos: str,
    no_telepon: str, 
    deskripsi: str,
    gamelan_id: list[str],
    desa_id: str,
    user_id: str
    ):
    
    data_sanggar: SanggarData
    
    timestamps = time.time()

    if gamelan_id:
        gamelan_id = [re.sub(r'"', '', id_gamelan) for id_gamelan in gamelan_id]

    data_sanggar = {
        "image": image,
        "nama_sanggar": nama,
        "no_telepon": no_telepon,
        "nama_jalan": nama_jalan,
        "kode_pos": kode_pos,
        "user_id": user_id,
        "gamelan_id": gamelan_id,
        "status_id": "67618f9ecc4fa7bc6c0bdbbb",
        "createdAt": timestamps,
        "updatedAt": timestamps,
        "deskripsi": deskripsi,
        "desa_id": desa_id
    }

    result = await collection.insert_one(data_sanggar)

    return {"_id": str(result.inserted_id), "nama_sanggar": nama, "message": "Data created successfully"}

async def update_sanggar_data(
    id: str, 
    image_path: str = None, 
    nama: str = None,
    nama_jalan: str = None,
    kode_pos: str = None,
    no_telepon: str = None, 
    deskripsi: str = None,
    gamelan_id: list[str] = None,
    id_desa: str = None
    ):
    
    object_id = ObjectId(id)

    update_data = {}
    
    if image_path:
        update_data["image"] = image_path

    if gamelan_id:
        gamelan_id = [data for data in gamelan_id if data and data != "string"]

    if not gamelan_id:
        gamelan_id = None

    if gamelan_id:
        gamelan_id = [re.sub(r'"', '', id_gamelan) for id_gamelan in gamelan_id]
        update_data["gamelan_id"] = gamelan_id

    if nama:
        update_data["nama_sanggar"] = nama
    
    if no_telepon:
        update_data["no_telepon"] = no_telepon
    
    if nama_jalan:
        update_data["nama_jalan"] = nama_jalan
    
    if kode_pos:
        update_data["kode_pos"] = kode_pos
    
    if deskripsi:
        update_data["deskripsi"] = deskripsi

    if id_desa:
        update_data["desa_id"] = id_desa

    timestamps = time.time()

    if update_data:
        update_data["updatedAt"] = timestamps

    await collection.update_one(
        {"_id": object_id},
        {"$set": update_data},
    )

    return {"message": "Data updated successfully", "updated_data": update_data}

async def delete_sanggar_data(id: str):
    object_id = ObjectId(id)

    sanggar_image = []

    cursor = collection.find({"_id": object_id})

    async for document in cursor:
        sanggar_image_data = document["image"]
        
        sanggar_image.append(sanggar_image_data)

    for path_todelete_sanggar in sanggar_image:
        public_id = extract_public_id(path_todelete_sanggar)

        cloudinary.uploader.destroy(public_id)

    await collection.delete_one({"_id": object_id})

    return True

def extract_public_id(secure_url):
    pattern = r"/upload/(?:v\d+/)?(.+)\.\w+$"
    match = re.search(pattern, secure_url)
    if match:
        return match.group(1)
    else:
        return None

async def approval_sanggar_data(id: str, status: str):
    object_id = ObjectId(id)
    timestamps = time.time()
    status_name: str = None
    status_list = await get_status()
    if status_list:
        print(status_list)
        for status_data in status_list["status_list"]:
            if status_data.get("_id") == status:
                status_name = status_data.get("status", "")
                break    

    await collection.update_one({"_id": object_id}, {"$set": {"status_id": status, "updatedAt": timestamps}})

    return f"Data Gamelan Bali {status_name}"
