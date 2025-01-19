from models.audiogamelanbali import *
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
import cloudinary
import cloudinary.uploader
from cloudinary.utils import cloudinary_url

uri = "mongodb://alexbramartha14:WCknO6oCCiM8r3qC@tagamelanbaliakhir-shard-00-00.zx7dr.mongodb.net:27017,tagamelanbaliakhir-shard-00-01.zx7dr.mongodb.net:27017,tagamelanbaliakhir-shard-00-02.zx7dr.mongodb.net:27017/?ssl=true&replicaSet=atlas-qfuxr3-shard-0&authSource=admin&retryWrites=true&w=majority&appName=TAGamelanBaliAkhir"
client = AsyncIOMotorClient(uri)

database = client["tugas-akhir-data"]

collection_desa_list = database["desa-list"]
collection_kecamatan_list = database["kecamatan-list"]
collection_kabupaten_list = database["kabupaten-list"]
collection_provinsi_list = database["provinsi-list"]

async def fetch_desa_data():
    desa = []

    document = collection_desa_list.find({})

    async for list in document:
        data_desa = {
            "_id": str(list["_id"]),
            "nama_desa": list["nama_desa"],
            "kecamatan_id": list["kecamatan_id"]
        }

        desa.append(data_desa)

    return {"desa-data": desa}

async def fetch_desa_data_by_kecamatan_id(id: str):
    desa = []

    document = collection_desa_list.find({"kecamatan_id": id})

    async for list in document:
        data_desa = {
            "_id": str(list["_id"]),
            "nama_desa": list["nama_desa"],
            "kecamatan_id": list["kecamatan_id"]
        }

        desa.append(data_desa)

    return {"desa-data": desa}


async def fetch_kecamatan_data():
    kecamatan = []

    document = collection_kecamatan_list.find({})

    async for list in document:
        data_kecamatan = {
            "_id": str(list["_id"]),
            "nama_kecamatan": list["nama_kecamatan"],
            "kabupaten_id": list["kabupaten_id"]
        }

        kecamatan.append(data_kecamatan)

    return {"kecamatan-data": kecamatan}

async def fetch_kecamatan_data_by_kabupaten_id(id: str):
    kecamatan = []

    document = collection_kecamatan_list.find({"kabupaten_id": id})

    async for list in document:
        data_kecamatan = {
            "_id": str(list["_id"]),
            "nama_kecamatan": list["nama_kecamatan"],
            "kabupaten_id": list["kabupaten_id"]
        }

        kecamatan.append(data_kecamatan)

    return {"kecamatan-data": kecamatan}


async def fetch_kabupaten_data():
    kabupaten = []

    document = collection_kabupaten_list.find({})

    async for list in document:
        data_kabupaten = {
            "_id": str(list["_id"]),
            "nama_kabupaten": list["nama_kabupaten"],
            "provinsi_id": list["provinsi_id"]
        }

        kabupaten.append(data_kabupaten)

    return {"kabupaten-data": kabupaten}

async def fetch_kabupaten_data_by_provinsi_id(id: str):
    kabupaten = []

    document = collection_kabupaten_list.find({"provinsi_id": id})

    async for list in document:
        data_kabupaten = {
            "_id": str(list["_id"]),
            "nama_kabupaten": list["nama_kabupaten"],
            "provinsi_id": list["provinsi_id"]
        }

        kabupaten.append(data_kabupaten)

    return {"kabupaten-data": kabupaten}

async def fetch_alamat_by_id_desa(id: str):
    objectId = ObjectId(id)
    desaListArray = []
    kecamatanListArray = []
    kabupatenListArray = []
    
    document = await collection_desa_list.find_one({"_id": objectId})

    if document:
        id_kec_in_desa = document["kecamatan_id"]

        documentDesa = collection_desa_list.find({"kecamatan_id": id_kec_in_desa})
        async for desaList in documentDesa:
            desaData = {
                "_id": str(desaList["_id"]),
                "nama_desa": desaList["nama_desa"],
                "kecamatan_id": desaList["kecamatan_id"]
            }

            desaListArray.append(desaData)

        objectKecId = ObjectId(id_kec_in_desa)
        documentKecamatan = await collection_kecamatan_list.find_one({"_id": objectKecId})

        id_kab_in_kec = documentKecamatan["kabupaten_id"]
        documentKecamatanList = collection_kecamatan_list.find({"kabupaten_id": id_kab_in_kec})
        async for kecamatanList in documentKecamatanList:
            kecamatanData = {
                "_id": str(kecamatanList["_id"]),
                "nama_kecamatan": kecamatanList["nama_kecamatan"],
                "kabupaten_id": kecamatanList["kabupaten_id"]
            }

            kecamatanListArray.append(kecamatanData)

        return {
            "desa_data": desaListArray,
            "kecamatan_data": kecamatanListArray,
            "kabupaten_id": id_kab_in_kec
        }
    
    return None

# async def fetch_nama_alamat_by_id_desa(id: list[str]):
#     listObjectId = []

#     for idDesa in id:
#         objectId = ObjectId(idDesa)
#         listObjectId.append(objectId)

#     namaDesa: str = ""
#     namaKecamatan: str = ""
#     namaKabupaten: str = ""
#     namaProvinsi: str = ""

#     datalistdocument = collection_desa_list.find({"_id": {"$in": listObjectId}})
#     if datalistdocument:
#         async for document in datalistdocument:
#             namaDesa = document["nama_desa"]
#             id_kec_in_desa = document["kecamatan_id"]
            
#             objectIdKec = ObjectId(id_kec_in_desa)
#             documentKec = await collection_kecamatan_list.find_one({"_id": objectIdKec})
#             if documentKec:
#                 namaKecamatan = documentKec["nama_kecamatan"]
#                 id_kab_in_kec = documentKec["kabupaten_id"]

#             objectIdKab = ObjectId(id_kab_in_kec)
#             documentKab = await collection_kabupaten_list.find_one({"_id": objectIdKab})
#             if documentKab:
#                 namaKabupaten = documentKab["nama_kabupaten"]
#                 id_prov_in_kab = documentKab["provinsi_id"]

#             objectIdProv = ObjectId(id_prov_in_kab)
#             documentProv = await collection_provinsi_list.find_one({"_id": objectIdProv})
#             if documentProv:
#                 namaProvinsi = documentProv["nama_provinsi"]

#             return {
#                 "nama_desa": namaDesa,
#                 "kecamatan_desa": namaKecamatan,
#                 "kabupaten_desa": namaKabupaten,
#                 "provinsi_nama": namaProvinsi
#             }
    
#     return None

async def fetch_nama_alamat_by_id_desa(id: List[str]):
    listObjectId = [ObjectId(desa_id) for desa_id in id]

    # Dictionary untuk menyimpan data dengan key adalah desa_id
    alamat_data = {}

    # Ambil data desa
    desa_documents = collection_desa_list.find({"_id": {"$in": listObjectId}})
    id_kecamatan_set = set()
    async for desa_doc in desa_documents:
        desa_id_str = str(desa_doc["_id"])
        alamat_data[desa_id_str] = {
            "nama_desa": desa_doc["nama_desa"],
            "kecamatan_id": desa_doc["kecamatan_id"]
        }
        id_kecamatan_set.add(ObjectId(desa_doc["kecamatan_id"]))

    # Ambil data kecamatan
    kecamatan_documents = collection_kecamatan_list.find({"_id": {"$in": list(id_kecamatan_set)}})
    id_kabupaten_set = set()
    kecamatan_map = {}
    async for kecamatan_doc in kecamatan_documents:
        kecamatan_map[str(kecamatan_doc["_id"])] = {
            "nama_kecamatan": kecamatan_doc["nama_kecamatan"],
            "kabupaten_id": kecamatan_doc["kabupaten_id"]
        }
        id_kabupaten_set.add(ObjectId(kecamatan_doc["kabupaten_id"]))

    # Ambil data kabupaten
    kabupaten_documents = collection_kabupaten_list.find({"_id": {"$in": list(id_kabupaten_set)}})
    id_provinsi_set = set()
    kabupaten_map = {}
    async for kabupaten_doc in kabupaten_documents:
        kabupaten_map[str(kabupaten_doc["_id"])] = {
            "nama_kabupaten": kabupaten_doc["nama_kabupaten"],
            "provinsi_id": kabupaten_doc["provinsi_id"]
        }
        id_provinsi_set.add(ObjectId(kabupaten_doc["provinsi_id"]))

    # Ambil data provinsi
    provinsi_documents = collection_provinsi_list.find({"_id": {"$in": list(id_provinsi_set)}})
    provinsi_map = {}
    async for provinsi_doc in provinsi_documents:
        provinsi_map[str(provinsi_doc["_id"])] = provinsi_doc["nama_provinsi"]

    # Gabungkan data ke dalam dictionary alamat_data
    for desa_id, desa_info in alamat_data.items():
        kecamatan_id = desa_info["kecamatan_id"]
        if kecamatan_id in kecamatan_map:
            kabupaten_id = kecamatan_map[kecamatan_id]["kabupaten_id"]
            provinsi_id = kabupaten_map[kabupaten_id]["provinsi_id"]

            desa_info.update({
                "kecamatan": kecamatan_map[kecamatan_id]["nama_kecamatan"],
                "kabupaten": kabupaten_map[kabupaten_id]["nama_kabupaten"],
                "provinsi": provinsi_map[provinsi_id]
            })

    print(alamat_data)

    return alamat_data


