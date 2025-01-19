from models.gamelanbali import *
from motor.motor_asyncio import AsyncIOMotorClient
from pymongo.mongo_client import MongoClient
from pymongo.server_api import ServerApi
from bson import ObjectId
from pydantic import BaseModel
from fastapi.encoders import jsonable_encoder
import json
from fastapi import FastAPI, HTTPException
import re
import time
from datetime import datetime
from typing import List

uri = "mongodb://alexbramartha14:WCknO6oCCiM8r3qC@tagamelanbaliakhir-shard-00-00.zx7dr.mongodb.net:27017,tagamelanbaliakhir-shard-00-01.zx7dr.mongodb.net:27017,tagamelanbaliakhir-shard-00-02.zx7dr.mongodb.net:27017/?ssl=true&replicaSet=atlas-qfuxr3-shard-0&authSource=admin&retryWrites=true&w=majority&appName=TAGamelanBaliAkhir"
client = AsyncIOMotorClient(uri)

database = client["tugas-akhir-data"]

collection = database["gamelan-bali"]
collection_instrumen = database["instrumen-gamelan"]
collection_audio_gamelan = database["audio-gamelan"]
collection_status = database["status"]
collection_golongan = database["golongan"]

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

async def get_golongan():
    golongan = []

    response = collection_golongan.find({})
    
    async for response_golongan in response:
        golongan_data = {
            "_id": str(response_golongan["_id"]),
            "golongan": response_golongan["golongan"],
            "deskripsi": response_golongan["deskripsi"]
        }
        golongan.append(golongan_data)

    return {"golongan_list": golongan}

async def get_golongan_by_id(golongan_id: str):
    objectId = ObjectId(golongan_id)

    response = await collection_golongan.find_one({"_id": objectId})
    
    golongan_data = {
        "_id": str(response["_id"]),
        "golongan": response["golongan"],
        "deskripsi": response["deskripsi"]
    }

    return golongan_data

async def fetch_audio_gamelan_by_gamelan_id(id: List[str]):
    audio_data = []
    
    audio_gamelan = collection_audio_gamelan.find({"id_gamelan": {"$in": id}})

    async for audio_gamelan_data in audio_gamelan:
        audio_data_gamelan = {
            "_id": str(audio_gamelan_data["_id"]),
            "id_gamelan": audio_gamelan_data["id_gamelan"],
            "audio_name": audio_gamelan_data["audio_name"],
            "audio_path": audio_gamelan_data["audio_path"],
            "deskripsi": audio_gamelan_data["deskripsi"]
        }

        audio_data.append(audio_data_gamelan)

    return audio_data

async def fetch_all_gamelan_by_instrument_id(id: str):
    
    gamelan_specific = collection.find({"instrument_id": id})

    gamelan_data_spec = []
    gamelan_id_list = []

    async for instrument in gamelan_specific:
        ts = instrument["createdAt"]
        dt = datetime.fromtimestamp(ts)
        tanggal = dt.date()
        waktu = dt.time()

        updateTs = instrument["updatedAt"]
        updateDt = datetime.fromtimestamp(updateTs)
        updateTanggal = updateDt.date()
        updateWaktu = updateDt.time()

        golongan_name = await get_golongan_by_id(instrument["golongan_id"])

        gamelan_data = {
            "_id": str(instrument["_id"]),
            "nama_gamelan": instrument["nama_gamelan"],
            "golongan_id": instrument["golongan_id"],
            "golongan": golongan_name["golongan"],
            "description": instrument["description"],
            "upacara": instrument["upacara"],
            "instrument_id": instrument["instrument_id"],
            "status_id": instrument["status_id"],
            "createdAt": dt,
            "createdDate": tanggal,
            "createdTime": waktu,
            "updatedAt": updateDt,
            "updatedDate": updateTanggal,
            "updateTime": updateWaktu,
            "audio_data": []
        }
    
        gamelan_data_spec.append(gamelan_data)

        gamelan_id_list.append(str(instrument["_id"]))

    audio_data = await fetch_audio_gamelan_by_gamelan_id(gamelan_id_list)
    full_data_with_audio = []
    for gamelan_data_full_with_audio in gamelan_data_spec:
        gamelan_data_full_with_audio["audio_data"] = [audio for audio in audio_data if audio["id_gamelan"] == gamelan_data_full_with_audio["_id"]]
        full_data_with_audio.append(gamelan_data_full_with_audio)

    if full_data_with_audio:
        return {
            "gamelan_data": full_data_with_audio
        }
    
    return f"There is no data gamelan with this id {id}"

async def fetch_all_instrument_by_gamelan_name(name: str):
    
    gamelan_specific = collection.find({"nama_gamelan": {"$regex": f"(?i){name}"}})

    gamelan_data_spec = []

    instrument_id = []

    gamelan_id_list = []

    async for instrument in gamelan_specific:
        ts = instrument["createdAt"]
        dt = datetime.fromtimestamp(ts)
        tanggal = dt.date()
        waktu = dt.time()

        updateTs = instrument["updatedAt"]
        updateDt = datetime.fromtimestamp(updateTs)
        updateTanggal = updateDt.date()
        updateWaktu = updateDt.time()

        golongan_name = await get_golongan_by_id(instrument["golongan_id"])

        gamelan_data = {
            "_id": str(instrument["_id"]),
            "nama_gamelan": instrument["nama_gamelan"],
            "golongan_id": instrument["golongan_id"],
            "golongan": golongan_name["golongan"],
            "description": instrument["description"],
            "upacara": instrument["upacara"],
            "instrument_id": instrument["instrument_id"],
            "status_id": instrument["status_id"],
            "createdAt": dt,
            "createdDate": tanggal,
            "createdTime": waktu,
            "updatedAt": updateDt,
            "updatedDate": updateTanggal,
            "updateTime": updateWaktu
        }
        
        instrument_data_id = {
            "instrument_id": instrument["instrument_id"]
        }
        
        gamelan_id_list.append(str(instrument["_id"]))

        gamelan_data_spec.append(gamelan_data)
        instrument_id.append(instrument_data_id)

    print(instrument_id)

    array_id = []
    
    for id in instrument_id:
        for item in id["instrument_id"]:
            object_ids = ObjectId(item)
            array_id.append(object_ids)

    print(array_id)

    instrumen = collection_instrumen.find({"_id": {"$in": array_id}})
    
    data_instrumen = []
    
    async for dataInstrument in instrumen:
        instrumen_data = {
            "_id": str(dataInstrument["_id"]),
            "nama_instrument": dataInstrument["nama_instrument"],
            "description": dataInstrument["description"],
            "trid_image": dataInstrument["trid_image"],
            "fungsi": dataInstrument["fungsi"],
            "image_instrumen": dataInstrument["image_instrumen"],
            "bahan": dataInstrument["bahan"]
        }

        data_instrumen.append(instrumen_data)

    audio_data = await fetch_audio_gamelan_by_gamelan_id(gamelan_id_list)
    full_data_with_audio = []

    for gamelan_data_with_audio in gamelan_data_spec:
        gamelan_data_with_audio['audio_gamelan'] = [
            audio for audio in audio_data if gamelan_data_with_audio['_id'] == audio['id_gamelan']
        ] 

        full_data_with_audio.append(gamelan_data_with_audio)

    if gamelan_data_spec:
        return {
            "gamelan_data": full_data_with_audio,
            "instrument_data": data_instrumen,
        }

    return {
            "gamelan_data": f"There is no data gamelan with this name {name}",
            "instrument_data": f"There is no data instrument with this name {name}",
        }

async def fetch_gamelan_by_filter(statusId: List[str], golonganId: List[str]):
    gamelan = []

    if statusId:
        statusId = [re.sub(r'^"|"$', '', status) for status in statusId]

    if golonganId:
        golonganId = [re.sub(r'^"|"$', '', golongan) for golongan in golonganId]

    document = collection.find({"golongan_id": {"$in": golonganId}, "status_id": {"$in": statusId}})

    async for data in document:
        ts = data["createdAt"]

        dt = datetime.fromtimestamp(ts)
        tanggal = dt.date()
        waktu = dt.time()

        updateTs = data["updatedAt"]
        updateDt = datetime.fromtimestamp(updateTs)
        updateTanggal = updateDt.date()
        updateWaktu = updateDt.time()

        golongan_name = await get_golongan_by_id(data["golongan_id"])

        gamelan_data = {
            "_id": str(data["_id"]),
            "nama_gamelan": data["nama_gamelan"],
            "golongan_id": data["golongan_id"],
            "golongan": golongan_name["golongan"],
            "description": data["description"],
            "upacara": data["upacara"],
            "instrument_id": data["instrument_id"],
            "status_id": data["status_id"],
            "createdAt": dt,
            "createdDate": tanggal,
            "createdTime": waktu,
            "updatedAt": updateDt,
            "updatedDate": updateTanggal,
            "updateTime": updateWaktu
        }

        gamelan.append(gamelan_data)

    return {
        "gamelan_data": gamelan
    }

async def fetch_all_gamelan():
    gamelan = []

    document = collection.find({})

    gamelan_id_list = []

    async for data in document:
        ts = data["createdAt"]

        dt = datetime.fromtimestamp(ts)
        tanggal = dt.date()
        waktu = dt.time()

        updateTs = data["updatedAt"]
        updateDt = datetime.fromtimestamp(updateTs)
        updateTanggal = updateDt.date()
        updateWaktu = updateDt.time()

        golongan_name = await get_golongan_by_id(data["golongan_id"])

        gamelan_data = {
            "_id": str(data["_id"]),
            "nama_gamelan": data["nama_gamelan"],
            "golongan_id": data["golongan_id"],
            "golongan": golongan_name["golongan"],
            "description": data["description"],
            "upacara": data["upacara"],
            "instrument_id": data["instrument_id"],
            "status_id": data["status_id"],
            "createdAt": dt,
            "createdDate": tanggal,
            "createdTime": waktu,
            "updatedAt": updateDt,
            "updatedDate": updateTanggal,
            "updateTime": updateWaktu
        }

        gamelan.append(gamelan_data)
        gamelan_id_list.append(str(data["_id"]))

    audio_data = await fetch_audio_gamelan_by_gamelan_id(gamelan_id_list)

    full_data_with_audio = []

    for gamelan_data_with_audio in gamelan:
        gamelan_data_with_audio['audio_gamelan'] = [
            audio for audio in audio_data if gamelan_data_with_audio['_id'] == audio['id_gamelan']
        ] 

        full_data_with_audio.append(gamelan_data_with_audio)

    return {
        "gamelan_data": full_data_with_audio
    }

async def fetch_list_gamelan_by_id(id: List[str]):
    object_id_list = []

    for idItem in id:
        object_id_list.append(ObjectId(idItem))

    gamelan = []

    document = collection.find({"_id": {"$in": object_id_list}})

    async for data in document:
        ts = data["createdAt"]
        
        dt = datetime.fromtimestamp(ts)
        tanggal = dt.date()
        waktu = dt.time()

        updateTs = data["updatedAt"]
        updateDt = datetime.fromtimestamp(updateTs)
        updateTanggal = updateDt.date()
        updateWaktu = updateDt.time()
        
        golongan_name = await get_golongan_by_id(data["golongan_id"])

        gamelan_data = {
            "_id": str(data["_id"]),
            "nama_gamelan": data["nama_gamelan"],
            "golongan_id": data["golongan_id"],
            "golongan": golongan_name["golongan"],
            "description": data["description"],
            "upacara": data["upacara"],
            "instrument_id": data["instrument_id"],
            "status_id": data["status_id"],
            "createdAt": dt,
            "createdDate": tanggal,
            "createdTime": waktu,
            "updatedAt": updateDt,
            "updatedDate": updateTanggal,
            "updateTime": updateWaktu
        }

        gamelan.append(gamelan_data)

    return {
        "gamelan_data": gamelan
    }

async def fetch_specific_gamelan(id: str):
    object_id = ObjectId(id)
    gamelan = []
    instrument = []

    document = collection.find({"_id": object_id})

    gamelan_id_list = []
    instrument_id_list = []

    async for data in document:
        ts = data["createdAt"]
        
        dt = datetime.fromtimestamp(ts)
        tanggal = dt.date()
        waktu = dt.time()

        updateTs = data["updatedAt"]
        updateDt = datetime.fromtimestamp(updateTs)
        updateTanggal = updateDt.date()
        updateWaktu = updateDt.time()
        
        golongan_name = await get_golongan_by_id(data["golongan_id"])

        gamelan_data = {
            "_id": str(data["_id"]),
            "nama_gamelan": data["nama_gamelan"],
            "golongan_id": data["golongan_id"],
            "golongan": golongan_name["golongan"],
            "description": data["description"],
            "upacara": data["upacara"],
            "instrument_id": data["instrument_id"],
            "status_id": data["status_id"],
            "createdAt": dt,
            "createdDate": tanggal,
            "createdTime": waktu,
            "updatedAt": updateDt,
            "updatedDate": updateTanggal,
            "updateTime": updateWaktu
        }
        
        instrument_data_id = {
            "instrument_id": data["instrument_id"]
        }
        
        gamelan.append(gamelan_data)
        gamelan_id_list.append(str(data["_id"]))
        instrument_id_list.append(instrument_data_id)

    instrument_id_object = []

    for instrument_id_string in instrument_id_list:
        for item in instrument_id_string["instrument_id"]:
            object_id_instrument = ObjectId(item)
            instrument_id_object.append(object_id_instrument)

    instrument_collection = collection_instrumen.find({"_id": {"$in": instrument_id_object}})

    async for dataInstrument in instrument_collection:
        instrumen_data = {
            "_id": str(dataInstrument["_id"]),
            "nama_instrument": dataInstrument["nama_instrument"],
            "description": dataInstrument["description"],
            "trid_image": dataInstrument["trid_image"],
            "fungsi": dataInstrument["fungsi"],
            "image_instrumen": dataInstrument["image_instrumen"],
            "bahan": dataInstrument["bahan"]
        }

        instrument.append(instrumen_data)

    audio_data = await fetch_audio_gamelan_by_gamelan_id(gamelan_id_list)
    full_data_with_audio = []

    audio_list = []
    for gamelan_data_with_audio in gamelan:
        gamelan_data_with_audio['audio_gamelan'] = [
            audio for audio in audio_data if gamelan_data_with_audio['_id'] == audio['id_gamelan']
        ] 

        full_data_with_audio.append(gamelan_data_with_audio)

    return {
        "gamelan_data": full_data_with_audio,
        "instrument_data": instrument,
    }

async def fetch_specific_gamelan_by_golongan(golongan: str):
    gamelan = []
    document = collection.find({"golongan_id": {"$regex": f"(?i){golongan}"}})

    gamelan_id_list = []

    async for data in document:
        ts = data["createdAt"]
        
        dt = datetime.fromtimestamp(ts)
        tanggal = dt.date()
        waktu = dt.time()

        updateTs = data["updatedAt"]
        updateDt = datetime.fromtimestamp(updateTs)
        updateTanggal = updateDt.date()
        updateWaktu = updateDt.time()

        golongan_name = await get_golongan_by_id(data["golongan_id"])

        gamelan_data = {
            "_id": str(data["_id"]),
            "nama_gamelan": data["nama_gamelan"],
            "golongan_id": data["golongan_id"],
            "golongan": golongan_name["golongan"],
            "description": data["description"],
            "upacara": data["upacara"],
            "instrument_id": data["instrument_id"],
            "status_id": data["status_id"],
            "createdAt": dt,
            "createdDate": tanggal,
            "createdTime": waktu,
            "updatedAt": updateDt,
            "updatedDate": updateTanggal,
            "updateTime": updateWaktu
        }

        gamelan.append(gamelan_data)
        gamelan_id_list.append(str(data["_id"]))

    audio_data = await fetch_audio_gamelan_by_gamelan_id(gamelan_id_list)

    full_data_with_audio = []

    for gamelan_data_with_audio in gamelan:
        gamelan_data_with_audio['audio_gamelan'] = [
            audio for audio in audio_data if gamelan_data_with_audio['_id'] == audio['id_gamelan']
        ] 

        full_data_with_audio.append(gamelan_data_with_audio)

    return {
        "gamelan_data": full_data_with_audio
    }

async def fetch_byname_gamelan(nama_gamelan: str):
    gamelan = []

    cursor = collection.find({"nama_gamelan": {"$regex": f"(?i){nama_gamelan}"}})

    gamelan_id_list = []

    async for data in cursor:

        ts = data["createdAt"]
        
        dt = datetime.fromtimestamp(ts)
        tanggal = dt.date()
        waktu = dt.time()

        updateTs = data["updatedAt"]
        updateDt = datetime.fromtimestamp(updateTs)
        updateTanggal = updateDt.date()
        updateWaktu = updateDt.time()
        golongan_name = await get_golongan_by_id(data["golongan_id"])

        gamelan_data = {
            "_id": str(data["_id"]),
            "nama_gamelan": data["nama_gamelan"],
            "golongan_id": data["golongan_id"],
            "golongan": golongan_name["golongan"],
            "description": data["description"],
            "upacara": data["upacara"],
            "instrument_id": data["instrument_id"],
            "status_id": data["status_id"],
            "createdAt": dt,
            "createdDate": tanggal,
            "createdTime": waktu,
            "updatedAt": updateDt,
            "updatedDate": updateTanggal,
            "updateTime": updateWaktu
        }

        gamelan.append(gamelan_data)        
        gamelan_id_list.append(str(data["_id"]))

    audio_data = await fetch_audio_gamelan_by_gamelan_id(gamelan_id_list)

    full_data_with_audio = []

    for gamelan_data_with_audio in gamelan:
        gamelan_data_with_audio['audio_gamelan'] = [
            audio for audio in audio_data if gamelan_data_with_audio['_id'] == audio['id_gamelan']
        ] 

        full_data_with_audio.append(gamelan_data_with_audio)

    return {
        "gamelan_data": full_data_with_audio
    }

async def create_gamelan_data(nama_gamelan: str, golongan: str, description: str, upacara: List[str], instrument_id: List[str]):
    status = await get_status()
    status_id: str = ""

    if status:
        for status_list in status["status_list"]:
            if status_list.get("status") == "Pending":
                status_id = status_list.get("_id", "")
                break       

    timestamps = time.time()

    upacara = [re.sub(r'"', '', data) for data in upacara]
    instrument_id = [re.sub(r'"', '', data) for data in instrument_id]

    gamelan_data = {
        "nama_gamelan": nama_gamelan,
        "golongan_id": golongan,
        "description": description,
        "upacara": upacara,
        "instrument_id": instrument_id,
        "status_id": status_id,
        "createdAt": timestamps,
        "updatedAt": timestamps
    }
    
    response = await collection.insert_one(gamelan_data)

    return {"_id": str(response.inserted_id), "nama_gamelan": nama_gamelan, "message": "Data created successfully"}

async def approval_gamelan_data(id: str, status: str):
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

    return f"Data Gamelan Bali {status_name}"

async def update_gamelan_data(id: str, nama_gamelan: str = None, golongan: str = None, description: str = None, instrument_id: List[str] = None, upacara: List[str] = None):
    object_id = ObjectId(id)
    updated_data = {}
    
    if instrument_id:
        instrument_id = [data for data in instrument_id if data and data != "string"]

    if not instrument_id:
        instrument_id = None  

    if upacara:
        upacara = [data for data in upacara if data and data != "string"]
    
    if not upacara:
        upacara = None

    if nama_gamelan:
        updated_data["nama_gamelan"] = nama_gamelan

    if golongan:
        updated_data["golongan_id"] = golongan

    if description:
        updated_data["description"] = description
    
    if upacara:
        upacara = [re.sub(r'"', '', data) for data in upacara]
        updated_data["upacara"] = upacara

    if instrument_id:
        instrument_id = [re.sub(r'"', '', data) for data in instrument_id]
        updated_data["instrument_id"] = instrument_id

    print(updated_data)

    timestamps = time.time()

    if updated_data:
        updated_data["updatedAt"] = timestamps

    await collection.update_one(
        {"_id": object_id}, 
        {"$set": updated_data}
    )
    
    return {"message": "Data updated successfully", "updated_data": updated_data}
 
async def delete_gamelan_bali(id: str):
    object_id = ObjectId(id)

    await collection.delete_one({"_id": object_id})

    return True
