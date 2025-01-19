from models.instrumen import *
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

collection = database["instrumen-gamelan"]
collection_status = database["status"]
collection_audio_instrumen = database["audio-instrumen"]

async def fetch_audio_instrumen_by_instrumen_id(id: List[str]):
    audio_data = []
    
    audio_instrumen = collection_audio_instrumen.find({"instrument_id": {"$in": id}})

    async for audio_instrumen_data in audio_instrumen:
        audio_data_instrumen = {
            "_id": str(audio_instrumen_data["_id"]),
            "instrument_id": audio_instrumen_data["instrument_id"],
            "audio_name": audio_instrumen_data["audio_name"],
            "audio_path": audio_instrumen_data["audio_path"]
        }

        audio_data.append(audio_data_instrumen)

    return audio_data

async def fetch_byname_instrumen(name: str):
    instrument = []
    instrument_id_list = []

    cursor = collection.find({"nama_instrument": {"$regex": f"(?i){name}"}})
    
    async for document in cursor:
        ts = document["createdAt"]
        dt = datetime.fromtimestamp(ts)
        tanggal = dt.date()
        waktu = dt.time()

        updateTs = document["updatedAt"]
        updateDt = datetime.fromtimestamp(updateTs)
        updateTanggal = updateDt.date()
        updateWaktu = updateDt.time()

        instrumen_data = {
            "_id": str(document["_id"]),
            "nama_instrument": document["nama_instrument"],
            "description": document["description"],
            "trid_image": document["trid_image"],
            "fungsi": document["fungsi"],
            "image_instrumen": document["image_instrumen"],
            "status": document["status"],
            "bahan": document["bahan"],
            "createdAt": dt,
            "createdDate": tanggal,
            "createdTime": waktu,
            "updatedAt": updateDt,
            "updatedDate": updateTanggal,
            "updateTime": updateWaktu
        }
        instrument_id_list.append(str(document["_id"]))
        instrument.append(instrumen_data)

    audio_data = await fetch_audio_instrumen_by_instrumen_id(instrument_id_list)

    full_data_with_audio = []
    for instrumen_data in instrument:
        instrumen_data["audio_data"] = [audio for audio in audio_data if audio["instrument_id"] == instrumen_data["_id"]]
        full_data_with_audio.append(instrumen_data)

    if full_data_with_audio:
        return {
            "instrument_data": full_data_with_audio
        }

async def fetch_instrument_by_filter(statusId: List[str]):
    instrument = []

    if statusId:
        statusId = [re.sub(r'^"|"$', '', status) for status in statusId]

    cursor = collection.find({"status": {"$in": statusId}})

    async for document in cursor:
        ts = document["createdAt"]
        dt = datetime.fromtimestamp(ts)
        tanggal = dt.date()
        waktu = dt.time()

        updateTs = document["updatedAt"]
        updateDt = datetime.fromtimestamp(updateTs)
        updateTanggal = updateDt.date()
        updateWaktu = updateDt.time()

        instrumen_data = {
            "_id": str(document["_id"]),
            "nama_instrument": document["nama_instrument"],
            "description": document["description"],
            "trid_image": document["trid_image"],
            "fungsi": document["fungsi"],
            "image_instrumen": document["image_instrumen"],
            "status": document["status"],
            "bahan": document["bahan"],
            "createdAt": dt,
            "createdDate": tanggal,
            "createdTime": waktu,
            "updatedAt": updateDt,
            "updatedDate": updateTanggal,
            "updateTime": updateWaktu
        }

        instrument.append(instrumen_data)

    return {
        "instrument_data": instrument
    }

async def fetch_all_instrumen():
    instrument = []
    instrument_id_list = []
    cursor = collection.find({})

    async for document in cursor:
        ts = document["createdAt"]
        dt = datetime.fromtimestamp(ts)
        tanggal = dt.date()
        waktu = dt.time()

        updateTs = document["updatedAt"]
        updateDt = datetime.fromtimestamp(updateTs)
        updateTanggal = updateDt.date()
        updateWaktu = updateDt.time()

        instrumen_data = {
            "_id": str(document["_id"]),
            "nama_instrument": document["nama_instrument"],
            "description": document["description"],
            "trid_image": document["trid_image"],
            "fungsi": document["fungsi"],
            "image_instrumen": document["image_instrumen"],
            "status": document["status"],
            "bahan": document["bahan"],
            "createdAt": dt,
            "createdDate": tanggal,
            "createdTime": waktu,
            "updatedAt": updateDt,
            "updatedDate": updateTanggal,
            "updateTime": updateWaktu
        }

        instrument_id_list.append(str(document["_id"]))
        instrument.append(instrumen_data)

    audio_data = await fetch_audio_instrumen_by_instrumen_id(instrument_id_list)

    full_data_with_audio = []
    for instrumen_data in instrument:
        instrumen_data["audio_data"] = [audio for audio in audio_data if audio["instrument_id"] == instrumen_data["_id"]]
        full_data_with_audio.append(instrumen_data)

    if full_data_with_audio:
        return {
            "instrument_data": full_data_with_audio
        }

async def fetch_instrumen_only_nama_id():
    instrument = []
    cursor = collection.find({}, {"nama_instrument": 1})

    async for document in cursor:
        instrumen_data = {
            "_id": str(document["_id"]),
            "nama_instrument": document["nama_instrument"],
        }

        instrument.append(instrumen_data)

    return {
        "instrument_data": instrument
    }

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

async def create_instrumen_data(nama: str, desc: str, tridi: str, fungsi: str, image_instrumen: List[str], bahan: List[str]):
    data: InstrumenData

    status = await get_status()
    status_id: str = ""

    if status:
        for status_list in status["status_list"]:
            if status_list.get("status") == "Pending":
                status_id = status_list.get("_id", "")
                break      

    for bahanData in bahan:
        if bahanData:
            print(bahanData)

    timestamps = time.time()

    nama = re.sub(r'"', '', nama)
    desc = re.sub(r'^"|"$', '', desc)
    fungsi = re.sub(r'^"|"$', '', fungsi)
    bahan = [re.sub(r'^"|"$', '', bahanData) for bahanData in bahan]

    data = {
        "nama_instrument": nama,
        "description": desc,
        "trid_image": tridi,
        "fungsi": fungsi,
        "image_instrumen": image_instrumen,
        "status": status_id,
        "bahan": bahan,
        "createdAt": timestamps,
        "updatedAt": timestamps
    }

    document = await collection.insert_one(data)

    return {"_id": str(document.inserted_id), "nama_instrument": nama, "message": "Data created successfully"}

async def update_instrumen_data(id: str, nama: str = None, desc: str = None, fungsi: str = None, tridi: str = None, image_instrumen: list[str] = None, bahan: list[str] = None):
    objectId = ObjectId(id)
    
    data_updated = {}

    if bahan != None:
        bahan = [data for data in bahan if data and data != "string"]
    
    if image_instrumen != None:
        image_instrumen = [data for data in image_instrumen if data and data != "string"]
    
    if bahan:
        bahan = [re.sub(r'^"|"$', '', bahanData) for bahanData in bahan]
        data_updated["bahan"] = bahan

    if nama:
        nama = re.sub(r'"', '', nama)
        data_updated["nama_instrument"] = nama

    if desc:
        desc = re.sub(r'^"|"$', '', desc)
        data_updated["description"] = desc

    if fungsi:
        fungsi = re.sub(r'^"|"$', '', fungsi)
        data_updated["fungsi"] = fungsi

    if tridi:
        data_updated["trid_image"] = tridi

    if image_instrumen:
        data_updated["image_instrumen"] = image_instrumen

    timestamps = time.time()
    
    if data_updated:
        data_updated["updatedAt"] = timestamps

    await collection.update_one(
        {"_id": objectId},
        {"$set": data_updated},
    )

    return {"message": "Data updated successfully", "Updated_data": data_updated}

async def fetch_one_instrumen(id: str):
    object_id = ObjectId(id) 
    instrument = []
    instrument_id_list = []

    document = await collection.find_one({"_id": object_id})
    
    ts = document["createdAt"]
    dt = datetime.fromtimestamp(ts)
    tanggal = dt.date()
    waktu = dt.time()

    updateTs = document["updatedAt"]
    updateDt = datetime.fromtimestamp(updateTs)
    updateTanggal = updateDt.date()
    updateWaktu = updateDt.time()

    instrumen_data = {
        "_id": str(document["_id"]),
        "nama_instrument": document["nama_instrument"],
        "description": document["description"],
        "trid_image": document["trid_image"],
        "fungsi": document["fungsi"],
        "image_instrumen": document["image_instrumen"],
        "status": document["status"],
        "bahan": document["bahan"],
        "createdAt": dt,
        "createdDate": tanggal,
        "createdTime": waktu,
        "updatedAt": updateDt,
        "updatedDate": updateTanggal,
        "updateTime": updateWaktu
    }

    instrument_id_list.append(str(document["_id"]))
    instrument.append(instrumen_data)

    audio_data = await fetch_audio_instrumen_by_instrumen_id(instrument_id_list)

    full_data_with_audio = []
    for instrumen_data in instrument:
        instrumen_data["audio_data"] = [audio for audio in audio_data if audio["instrument_id"] == instrumen_data["_id"]]
        full_data_with_audio.append(instrumen_data)

    if full_data_with_audio:
        return {
            "instrument_data": full_data_with_audio
        }

async def fetch_tridi_instrumen(id: str):
    object_id = ObjectId(id)
    document = await collection.find_one({"_id": object_id})
    tridi_path = document.get("trid_image")
    return tridi_path

async def fetch_image_instrumen(id: str):
    object_id = ObjectId(id)
    document = await collection.find_one({"_id": object_id})
    image_path = document.get("image_instrumen")
    return image_path

async def delete_instrument_bali(id: str):
    object_id = ObjectId(id)

    instrumen_image = []
    instrumen_tridi = []

    cursor = collection.find({"_id": object_id})

    async for document in cursor:
        instrumen_tridi.append(document["trid_image"])
        instrumen_image.append(document["image_instrumen"])

    for path_todelete_tridi in instrumen_tridi:
        public_id = extract_public_id(path_todelete_tridi)
        print(public_id)
        cloudinary.uploader.destroy(public_id)

    for path_todelete_image in instrumen_image:
        for path in path_todelete_image:
            public_id = extract_public_id(path)

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

async def approval_instrunmen_data(id: str, status: str):
    object_id = ObjectId(id)
    status_name: str = None
    timestamps = time.time()
    status_list = await get_status()
    if status_list:
        for status_data in status_list["status_list"]:
            if status_data.get("_id") == status:
                status_name = status_data.get("status", "")
                break    

    await collection.update_one({"_id": object_id}, {"$set": {"status_id": status, "updatedAt": timestamps}})

    return f"Data Instrumen Gamelan Bali {status_name}"
