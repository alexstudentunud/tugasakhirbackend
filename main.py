from fastapi import FastAPI, HTTPException, File, UploadFile, Depends, status, Header, Form, Body
from fastapi.middleware.cors import CORSMiddleware
from models.masyarakat import *
from models.gamelanbali import *
from models.instrumen import *
import os
from datetime import timedelta, datetime, timezone
from fastapi.security import OAuth2PasswordRequestForm, OAuth2PasswordBearer
from jose import jwt, JWTError
from passlib.context import CryptContext
import re
from typing import Annotated, List, Optional
from jwt.exceptions import InvalidTokenError, ExpiredSignatureError, PyJWTError
from typing import Annotated
import json
import uvicorn
import cloudinary
import cloudinary.uploader
from cloudinary.utils import cloudinary_url
import time

# Configuration       
cloudinary.config( 
    cloud_name = "dvbbtszph", 
    api_key = "694649632346865", 
    api_secret = "WR5DNfKt3IXFvpRIX_SqLgW_ksw",
    secure=True
)

from databases.masyarakatdatabase import (
    fetch_one_user, 
    fetch_all_user,
    create_user_data,
    update_user_data,
    delete_user_data,
    update_user_photo,
    fetch_all_user_with_name,
    fetch_user_specific,
    get_user,
    create_ahli_data,
    fetch_pengguna_by_filter,
    get_role,
)

from databases.sanggardatabase import (
    fetch_all_sanggar,
    create_sanggar_data,
    delete_sanggar_data,
    update_sanggar_data,
    fetch_one_sanggar,
    fetch_sanggar_specific,
    fetch_sanggar_specific_by_id_creator,
    approval_sanggar_data,
    fetch_sanggar_specific_by_id,
    fetch_sanggar_by_filter
)

from databases.instrumendatabase import (
    fetch_all_instrumen,
    create_instrumen_data,
    update_instrumen_data,
    fetch_one_instrumen,
    fetch_byname_instrumen,
    delete_instrument_bali,
    fetch_image_instrumen,
    fetch_tridi_instrumen,
    approval_instrunmen_data,
    fetch_instrumen_only_nama_id,
    fetch_instrument_by_filter
)

from databases.audiogamelandatabase import (
    create_audio_data,
    fetch_audio_by_gamelan_id,
    delete_audio_data,
    update_audio_data,
    fetch_audio_path,
    fetch_all_audio,
    delete_audio_gamelan_spesifik
)

from databases.gamelanbalidatabase import (
    fetch_all_gamelan,
    create_gamelan_data,
    delete_gamelan_bali,
    update_gamelan_data,
    fetch_specific_gamelan,
    fetch_byname_gamelan,
    approval_gamelan_data,
    fetch_all_instrument_by_gamelan_name,
    fetch_all_gamelan_by_instrument_id,
    fetch_specific_gamelan_by_golongan,
    fetch_list_gamelan_by_id,
    get_golongan,
    get_status,
    fetch_gamelan_by_filter
)

from databases.alamatdatabase import (
    fetch_desa_data,
    fetch_desa_data_by_kecamatan_id,
    fetch_kecamatan_data,
    fetch_kecamatan_data_by_kabupaten_id,
    fetch_kabupaten_data,
    fetch_kabupaten_data_by_provinsi_id,
    fetch_alamat_by_id_desa
)

from databases.audioinstrumendatabase import (
    create_audio_data_instrumen,
    fetch_audio_by_instrumen_id,
    delete_audio_instrumen_data,
    update_audio_instrumen_data,
    fetch_audio_path_instrumen,
    fetch_all_audio_instrumen,
    delete_audio_instrumen_spesifik_data,
    delete_audio_instrumen_by_id,
)

SECRET_KEY = "letsmekillyou"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 10000

app = FastAPI()

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

# origins = ['http://localhost:3000']

app.add_middleware(
    CORSMiddleware,
    allow_origins = ["*"],
    allow_credentials = True,
    allow_methods = ["*"],
    allow_headers = ["*"],
)

if __name__ == "__main__":
    port = int(os.getenv("PORT", 8000))  # Railway akan menyetujui PORT dari environment
    uvicorn.run("main:app", host="0.0.0.0", port=port)

def verify_password(plain_password, hashed_password):
    return pwd_context.verify(plain_password, hashed_password)

def get_password_hash(password):
    return pwd_context.hash(password)

async def authenticate_user(email: str, password: str):
    user = await get_user(email)
    if not user:
        return False
    if not verify_password(password, user.password):
        return False
    return user

def create_access_token(data: dict, expires_delta: timedelta | None = None):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.now(timezone.utc) + expires_delta
    else:
        expire = datetime.now(timezone.utc) + timedelta(minutes=15)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

async def get_current_user(token: str = Depends(oauth2_scheme)):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )

    user = None

    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        email: str = payload.get("sub")
        if email is None:
            raise credentials_exception
        token_data = TokenData(email=email)    
        user = await get_user(email=token_data.email)
        if user is None:
            raise credentials_exception
        
    except ExpiredSignatureError:
        raise HTTPException(status_code=400, detail="Token has expired, please login again!")
    except InvalidTokenError:
        raise HTTPException(status_code=400, detail="Token Invalid!")
    except JWTError:
        raise HTTPException(status_code=400, detail="Token Invalid!")
    except AttributeError:
        raise HTTPException(status_code=400, detail="Token has expired, please login again!")
    
    return user

async def get_current_active_user(
    current_user: Annotated[UserInDB, Depends(get_current_user)],
):
    if not current_user.email:
        raise HTTPException(status_code=400, detail="Inactive user")
    return current_user

@app.post("/token")
async def login_for_access_token(
    form_data: Annotated[OAuth2PasswordRequestForm, Depends()],
) -> Token:
    user = await authenticate_user(form_data.username, form_data.password)
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)

    access_token = create_access_token(
        data={
            "nama": str(user.nama),
            "sub": str(user.email),
            "foto_profile": str(user.foto_profile),
            "test": str(user.test),
            "status": str(user.status),
            "createdAtDate": str(user.createdAtDate),
            "createdAtTime": str(user.createdAtTime),
            "updatedAtTime": str(user.updatedAtTime),
            "updatedAtDate": str(user.updatedAtDate),
            "role": str(user.role)
            }, 
        expires_delta=access_token_expires
    )
    
    return Token(
        access_token=access_token, 
        user_id=user.test, 
        nama=user.nama,
        foto_profile=user.foto_profile,
        email=user.email,
        createdAtTime=user.createdAtTime,
        createdAtDate=user.createdAtDate,
        updatedAtDate=user.updatedAtDate,
        updatedAtTime=user.updatedAtTime,
        role=user.role,
        status=user.status,
        token_type="bearer"
    )

@app.get("/")
async def read_root():
    return {"message": "Hello, world!"}

@app.get("/api/userdata/getalluser")
async def get_all_users(current_user: UserInDB = Depends(get_current_user)):
    if current_user:
        response = await fetch_all_user()
        if response:
            return response
        raise HTTPException(404, "Empty Users Data")

@app.get("/api/userdata/getallbyname/{name}")
async def get_all_user_by_name(name: str, current_user: UserInDB = Depends(get_current_user)):
    if current_user:
        response = await fetch_all_user_with_name(name)
        if response:
            return response
        raise HTTPException(404, f"There is no user with this name {name}")

@app.get("/api/userdata/getspecific/{email}")
async def get_specific_by_email(email: str):
    valid = re.match(r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$', email)

    if valid:
        response = await fetch_user_specific(email)
        if response == None:
            return response
        raise HTTPException(404, f"Email already exists")
    raise HTTPException(404, f"Email not Valid!")

@app.get("/api/userdata/getuserbyid/{id}")
async def get_user_by_id(id: str, current_user: UserInDB = Depends(get_current_user)):
    if current_user:
        response = await fetch_one_user(id)
        if response:
            return response
        raise HTTPException(404, f"There is no user with this name {id}")

@app.post("/api/userdata/registeruser")
async def create_data_user(nama: Annotated[str, Form()], email: Annotated[str, Form()], password: Annotated[str, Form()], role_input: Annotated[str, Form()]):
    await get_specific_by_email(email)
    
    password_hashed = get_password_hash(password)

    response = await create_user_data(nama, email, password_hashed, role_input)
    if response:
        return response
    raise HTTPException(400, "Something went wrong!")

@app.post("/api/userdata/fetchbyfilter")
async def fetch_pengguna_by_filter_role_status(roleId: Annotated[List[str], Form()], statusId: Annotated[List[str], Form()], current_user: UserInDB = Depends(get_current_user)):
    if current_user:
        response = await fetch_pengguna_by_filter(roleId, statusId)
        if response:
            return response
        raise HTTPException(404, "Empty Pengguna Data")

@app.post("/api/userdata/registerahli")
async def create_data_ahli(nama: Annotated[str, Form()], email: Annotated[str, Form()], password: Annotated[str, Form()]):
    await get_specific_by_email(email)
    
    password_hashed = get_password_hash(password)

    response = await create_ahli_data(nama, email, password_hashed)
    if response:
        return response
    raise HTTPException(400, "Something went wrong!")

@app.put("/api/userdata/updateprofile/{id}")
async def update_data_user(id: str, email: Annotated[str, Form()] = None, nama: Annotated[str, Form()] = None, current_user: UserInDB = Depends(get_current_user)):
    if current_user:
        if email:
            await get_specific_by_email(email)

        response = await update_user_data(id, email, nama)
        if response:
            return response
        raise HTTPException(404, f"There is no user with this name {id}")

@app.post("/api/files/uploadphotoprofile/{id}")
async def upload_photo_profile_pengguna(id: str, files: list[UploadFile], current_user: UserInDB = Depends(get_current_user)):
    if current_user:
        # if os.path.exists(current_user.foto_profile):
        #     os.remove(current_user.foto_profile)
        #     print(f"The file {current_user.foto_profile} has been deleted.")
        # else:
        #     print(f"The file {current_user.foto_profile} does not exist.")


        try:
            if current_user.foto_profile != "none":
                url_link = current_user.foto_profile

                public_id = extract_public_id(url_link)

                response = cloudinary.uploader.destroy(public_id)

            uploaded_files = []

            for file in files:
                file_content = await file.read()
                response = cloudinary.uploader.upload(file_content)
                uploaded_files.append(response["secure_url"])

                await update_photo_user(id, response["secure_url"])

            timestamps = time.time()

            return {"message": "Files saved successfully", "files": uploaded_files, "updatedAt": timestamps}

        except Exception as e:
            return {"message": f"Error occurred: {str(e)}"}

def extract_public_id(secure_url):
    pattern = r"/upload/(?:v\d+/)?(.+)\.\w+$"
    match = re.search(pattern, secure_url)
    if match:
        return match.group(1)
    else:
        return None
    
async def update_photo_user(id: str, foto: str):
    response = await update_user_photo(id, foto)
    if response:
        return response
    raise HTTPException(404, f"There is no user with this name {id}")

@app.delete("/api/userdata/deleteuser/{id}")
async def delete_data_user(id: str, current_user: UserInDB = Depends(get_current_user)):
    if current_user:
        response = await delete_user_data(id)
        if response == True:
            return "Successfully deleted user!"
        raise HTTPException(404, f"There is no user with this name {id}")

@app.post("/api/sanggardata/fetch/byfilter/{id}")
async def get_sanggar_data_by_filter(id: str, statusId: Annotated[List[str], Form()], current_user: UserInDB = Depends(get_current_user)):
    if current_user:
        response = await fetch_sanggar_by_filter(id, statusId)
        if response:
            return response
        raise HTTPException(404, "There is no data Sanggar")

@app.post("/api/sanggardata/create")
async def create_sanggar(files: list[UploadFile], gamelan_id: Annotated[List[str], Form()], id_desa: Annotated[str, Form()], nama_sanggar: Annotated[str, Form()], no_telepon: Annotated[str, Form()], nama_jalan: Annotated[str, Form()], kode_pos: Annotated[str, Form()], deskripsi: Annotated[str, Form()], current_user: UserInDB = Depends(get_current_user)):

    if current_user:
        print(current_user)
        id_creator = current_user.test
        
        try: 
            saved_files = []

            for file in files:
                file_content = await file.read()
                response = cloudinary.uploader.upload(file_content)
                saved_files.append(response["secure_url"])

            path = saved_files[0]
            
            response = await create_sanggar_data(path, nama_sanggar, nama_jalan, kode_pos, no_telepon, deskripsi, gamelan_id, id_desa, id_creator)

            return {"message": "Data saved successfully", "response": response}
            
        except Exception as e:
            return {"message": f"Error occurred: {str(e)}"}

@app.get("/api/sanggardata/getone/{id}")
async def get_sanggar_by_id(id: str):
    response = await fetch_one_sanggar(id)
    if response:
        return response
    raise HTTPException(404, "There is no sanggar with this id!")

@app.get("/api/sanggardata/get")
async def get_all_sanggar(current_user: UserInDB = Depends(get_current_user)):
    if current_user:
        response = await fetch_all_sanggar()
        if response:
            return response
        raise HTTPException(404, "There is no sanggar data!")

@app.put("/api/sanggardata/update/{id}")
async def update_data_sanggar(id: str, files: list[UploadFile] = None, gamelan_id: Annotated[List[str], Form()] = None, id_desa: Annotated[str, Form()] = None, nama_sanggar: Annotated[str, Form()] = None, no_telepon: Annotated[str, Form()] = None, nama_jalan: Annotated[str, Form()] = None, kode_pos: Annotated[str, Form()] = None, deskripsi: Annotated[str, Form()] = None, current_user: UserInDB = Depends(get_current_user)):
    if current_user:
        path = ""
        if files and files[0].filename:
            image = await get_sanggar_by_id(id)

            if image:
                public_id = extract_public_id(image)

                response = cloudinary.uploader.destroy(public_id)

            try: 
                saved_files = []

                for file in files:
                    file_content = await file.read()
                    response = cloudinary.uploader.upload(file_content)
                    saved_files.append(response["secure_url"])

                path = saved_files[0]

            except Exception as e:
                return {"message": f"Error occurred: {str(e)}"}
                
        responseUpdate = await update_sanggar_data(id, path, nama_sanggar, nama_jalan, kode_pos, no_telepon, deskripsi, gamelan_id, id_desa)
        if responseUpdate:
            return responseUpdate
        raise HTTPException(404, f"There is no user with this name {id}")


@app.put("/api/sanggardata/approval/{id}")
async def update_data_approval_sanggar_data(id: str, status: Annotated[str, Form()],  current_user: UserInDB = Depends(get_current_user)):
    if current_user:
        response = await approval_sanggar_data(id, status)

        if response: 
            return response
        raise HTTPException(404, f"There is no sanggar data with id {id}")

@app.delete("/api/sanggardata/delete/{id}")
async def delete_data_sanggar(id: str, current_user: UserInDB = Depends(get_current_user)):
    if current_user:
        response = await delete_sanggar_data(id)
        if response == True:
            return "Successfully deleted sanggar!"
        raise HTTPException(404, f"There is no user with this name {id}")

@app.get("/api/sanggardata/getbyname/{name}")
async def get_specific_by_name_sanggar(name: str, current_user: UserInDB = Depends(get_current_user)):
    if current_user:
        response = await fetch_sanggar_specific(name)
        if response:
            return response
        raise HTTPException(404, f"There is no sanggar data with name {name}")

@app.get("/api/sanggardata/getbyid/{id}")
async def fetch_sanggar_by_id(id: str, current_user: UserInDB = Depends(get_current_user)):
    if current_user:
        response = await fetch_sanggar_specific_by_id(id)
        if response:
            return response
        raise HTTPException(404, f"There is no sanggar data with name {id}")

@app.get("/api/sanggardata/getbyidcreator/{id}")
async def get_specific_sanggar_by_id_creator(id: str, current_user: UserInDB = Depends(get_current_user)):
    if current_user:
        response = await fetch_sanggar_specific_by_id_creator(id)
        if response:
            return response
        raise HTTPException(404, f"There is no sanggar data with id ccreator: {id}")

@app.get("/api/instrumendata/getspecificbyname/{nama_instrument}")
async def fetch_instrumen_by_name(nama_instrument: str, current_user: UserInDB = Depends(get_current_user)):
    if current_user:
        response = await fetch_byname_instrumen(nama_instrument)

        if response:
            return response
        raise HTTPException(404, f"There is no instrument data with name {nama_instrument}")

@app.get("/api/instrumendata/getall")
async def fetch_all_data_instrumen(current_user: UserInDB = Depends(get_current_user)):
    if current_user:
        response = await fetch_all_instrumen()

        if response:
            return response
        raise HTTPException(404, "There is no instrument data!")

@app.post("/api/instrumendata/fetch/byfilter")
async def get_instrumen_data_by_filter(statusId: Annotated[List[str], Form()], current_user: UserInDB = Depends(get_current_user)):
    if current_user:
        response = await fetch_instrument_by_filter(statusId)
        if response:
            return response
        raise HTTPException(404, "There is no data Instrument Gamelan")

@app.post("/api/instrumendata/create")
async def create_data_instrumen(nama: Annotated[str, Form()], desc: Annotated[str, Form()], fungsi: Annotated[str, Form()], files_image: list[UploadFile], files_tridi: list[UploadFile], bahan: Annotated[List[str], Form()], current_user: UserInDB = Depends(get_current_user)):
    if current_user:
        try: 
            saved_files_image = []

            for file in files_image:
                file_content = await file.read()
                response = cloudinary.uploader.upload(file_content)
                saved_files_image.append(response["secure_url"])

            saved_files_tridi = []

            if saved_files_image:
                for file in files_tridi:
                    file_content = await file.read()
                    response = cloudinary.uploader.upload(file_content)
                    saved_files_tridi.append(response["secure_url"])

                tridi_path = saved_files_tridi[0]


            response = await create_instrumen_data(nama, desc, tridi_path, fungsi, saved_files_image, bahan)

            if response:
                return {"message": "Data saved successfully", "response": response}
            raise HTTPException(400, "Something went wrong!")
            
        except Exception as e:
            return {"message": f"Error occurred: {str(e)}"}

@app.put("/api/instrumendata/approval/{id}")
async def update_data_approval_instrumen_data(id: str, status: Annotated[str, Form()],  current_user: UserInDB = Depends(get_current_user)):
    if current_user:
        response = await approval_instrunmen_data(id, status)

        if response: 
            return response
        raise HTTPException(404, f"There is no instrument data with id {id}")

# saved_files_tridi = []
# file_paths_tridi = []

# for file_tridi in files_tridi:
#     file_path = os.path.join(r"/fastapi-learn/files/images/instrumentridi", file_tridi.filename)
    
#     with open(file_path, "wb") as f:
#         f.write(file_tridi.file.read())
    
#     saved_files_tridi.append(file_tridi.filename)
#     file_paths_tridi.append(str(file_path))

# tridi_path = file_paths_tridi[0]

@app.put("/api/instrumendata/update/{id}")
async def update_data_instrumen(id: str, flagImage: Annotated[str, Form()] = None, nama: Annotated[str, Form()] = None, desc: Annotated[str, Form()] = None, fungsi: Annotated[str, Form()] = None, files_image: list[UploadFile] = None, files_tridi: list[UploadFile] = None, bahan: Annotated[List[str], Form()] = None, current_user: UserInDB = Depends(get_current_user)):
    if current_user:
        try:
            
            saved_files_image = []
            tridi_path = None

            if files_image:
                if files_image[0].filename or files_image[1].filename:
                    image_past = await get_instrumen_image_by_id(id)
                    print("Entry the first")
                    if image_past:
                        if flagImage == "0":
                            if image_past[0]:
                                public_id = extract_public_id(image_past[0])
                                response = cloudinary.uploader.destroy(public_id)

                            for file in files_image:
                                file_content = await file.read()
                                response = cloudinary.uploader.upload(file_content)
                                saved_files_image.insert(0, response["secure_url"])
                                saved_files_image.insert(1, image_past[1])   

                        if flagImage == "1":
                            if image_past[1]:
                                print(image_past[1])
                                public_id = extract_public_id(image_past[1])
                                response = cloudinary.uploader.destroy(public_id)

                            for file in files_image:
                                file_content = await file.read()
                                response = cloudinary.uploader.upload(file_content)
                                saved_files_image.insert(0, image_past[0])
                                saved_files_image.insert(1, response["secure_url"])   

                        if flagImage == "2":
                            if image_past:
                                for imageurl in image_past:
                                    public_id = extract_public_id(imageurl)
                                    response = cloudinary.uploader.destroy(public_id)

                            for file in files_image:
                                file_content = await file.read()
                                response = cloudinary.uploader.upload(file_content)
                                saved_files_image.append(response["secure_url"])

            if files_tridi and files_tridi[0].filename:
                tridi_past = await get_instrumen_tridi_by_id(id)

                if tridi_past:
                    public_id = extract_public_id(tridi_past)

                    response = cloudinary.uploader.destroy(public_id)

                saved_files_tridi = []

                for file in files_tridi:
                    file_content = await file.read()
                    response = cloudinary.uploader.upload(file_content)
                    saved_files_tridi.append(response["secure_url"])

                tridi_path = saved_files_tridi[0]

            if not saved_files_image:
                saved_files_image = None

            if not tridi_path: 
                tridi_path = None

            print(saved_files_image)
            response = await update_instrumen_data(id, nama, desc, fungsi, tridi_path, saved_files_image, bahan)
            
            if response:
                return response
            raise HTTPException(400, "Something went wrong!")
            
        except Exception as e:
            return {"message": f"Error occurred: {str(e)}"}

@app.get("/api/instrumendata/getone/{id}")
async def get_instrumen_by_id(id: str, current_user: UserInDB = Depends(get_current_user)):
    if current_user:
        response = await fetch_one_instrumen(id)
        if response:
            return response
        raise HTTPException(404, f"There is no instrument data with this id {id}!")

async def get_instrumen_image_by_id(id: str, current_user: UserInDB = Depends(get_current_user)):
    if current_user:
        response = await fetch_image_instrumen(id)
        if response:
            return response
        raise HTTPException(404, f"There is no instrument data with this id {id}!")

async def get_instrumen_tridi_by_id(id: str, current_user: UserInDB = Depends(get_current_user)):
    if current_user:
        response = await fetch_tridi_instrumen(id)
        if response:
            return response
        raise HTTPException(404, f"There is no instrument data with this id {id}!")

@app.delete("/api/instrumendata/delete/{id}")
async def delete_data_instrumen(id: str, current_user: UserInDB = Depends(get_current_user)):
    if current_user:
        response = await delete_instrument_bali(id)
        if response == True:
            return "Successfully deleted instrument!"
        raise HTTPException(404, f"There is no instrument data with this name {id}")

@app.get("/api/gamelanbali/fetchall")
async def get_all_gamelan_bali(current_user: UserInDB = Depends(get_current_user)):
    if current_user:
        response = await fetch_all_gamelan()
        if response:
            return response
        raise HTTPException(404, "There is no data Gamelan Bali")

@app.get("/api/gamelanbali/fetch/specific/{id}")
async def get_specific_gamelan_bali_id(id: str, current_user: UserInDB = Depends(get_current_user)):
    if current_user:
        response = await fetch_specific_gamelan(id)
        if response:
            return response
        raise HTTPException(404, "There is no data Gamelan Bali")

@app.post("/api/gamelanbali/fetch/byfilter")
async def get_gamelan_data_by_filter(statusId: Annotated[List[str], Form()], golonganId: Annotated[List[str], Form()], current_user: UserInDB = Depends(get_current_user)):
    if current_user:
        response = await fetch_gamelan_by_filter(statusId, golonganId)
        if response:
            return response
        raise HTTPException(404, "There is no data Gamelan Bali")

@app.get("/api/gamelanbali/fetch/byname/{nama_gamelan}")
async def get_specific_gamelan_bali_name(nama_gamelan: str, current_user: UserInDB = Depends(get_current_user)):
    if current_user:
        response = await fetch_byname_gamelan(nama_gamelan)
        if response:
            return response
        raise HTTPException(404, "There is no data Gamelan Bali")

@app.post("/api/gamelanbali/createdata")
async def create_gamelan_bali(nama_gamelan: Annotated[str, Form()], golongan: Annotated[str, Form()], description: Annotated[str, Form()], upacara: Annotated[List[str], Form()], instrument_id: Annotated[List[str], Form()], current_user: UserInDB = Depends(get_current_user)):
    if current_user:
        response = await create_gamelan_data(nama_gamelan, golongan, description, upacara, instrument_id)

        if response:
            return response
        raise HTTPException(400, "Something went wrong!")

@app.post("/api/gamelandata/uploadaudio")
async def upload_audio_data(id_gamelan: Annotated[str, Form()], deskripsi: Annotated[str, Form()], nama_audio: Annotated[str, Form()], files: list[UploadFile]):
    try: 
        saved_files_audio = []

        for file in files:
            file_content = await file.read()
            response = cloudinary.uploader.upload(file_content, resource_type = "auto")
            saved_files_audio.append(response["secure_url"])

        audio_path = saved_files_audio[0]

        response = await create_audio_data(nama_audio, audio_path, id_gamelan, deskripsi)
        
        if response:
            return response
    
    except Exception as e:
        return {"message": f"Error occurred: {str(e)}"}

@app.put("/api/audiogamelanbali/updateaudio/{id}")
async def update_data_audio(id: str, nama_audio: Annotated[str, Form()] = None, deskripsi: Annotated[str, Form()] = None, files: list[UploadFile] = None):
    try: 
        audio_path = None

        if files and files[0].filename:
            audioPast = await get_audio_path_by_id(id)

            if audioPast:
                public_id = extract_public_id(audioPast)

                result = cloudinary.uploader.destroy(
                    public_id,
                    resource_type="video",
                    type="upload",
                    invalidate=True
                )

                print(result)

            saved_files_audio = []

            for file in files:
                file_content = await file.read()
                response = cloudinary.uploader.upload(file_content, resource_type = "auto")
                saved_files_audio.append(response["secure_url"])

            audio_path = saved_files_audio[0]

        response = await update_audio_data(id, nama_audio, audio_path, deskripsi)
        
        if response:
            return response
        
    except Exception as e:
        return {"message": f"Error occurred: {str(e)}"}

@app.get("/api/audiogamelanbali/fetchall/")
async def fetch_audio_all_data(current_user: UserInDB = Depends(get_current_user)):
    if current_user:
        response = await fetch_all_audio()
        if response:
            return response
        raise HTTPException(404, f"There is no audio data with this id {id}!")

async def get_audio_path_by_id(id: str, current_user: UserInDB = Depends(get_current_user)):
    if current_user:
        response = await fetch_audio_path(id)
        if response:
            return response
        raise HTTPException(404, f"There is no audio data with this id {id}!")

@app.get("/api/audiogamelanbali/fetch/bygamelanid/{id}")
async def get_audio_by_gamelan_id(id: str, current_user: UserInDB = Depends(get_current_user)):
    if current_user:
        response = await fetch_audio_by_gamelan_id(id)
        if response:
            return response
        raise HTTPException(404, "There is no data audio Gamelan Bali")

@app.delete("/api/audiogamelanbali/deletedata/{id}")
async def delete_data_audio_gamelan_by_id(id: str, current_user: UserInDB = Depends(get_current_user)):
    if current_user:
        response = await delete_audio_data(id)
        if response == True:
            return "Successfully deleted audio data!"
        raise HTTPException(404, f"There is no audio data with id {id}")

@app.delete("/api/audiogamelanbali/deletedataspesifik/{id}")
async def delete_data_audio_gamelanspesifik_by_id(id: str, current_user: UserInDB = Depends(get_current_user)):
    if current_user:
        response = await delete_audio_gamelan_spesifik(id)
        if response == True:
            return "Successfully deleted audio data!"
        raise HTTPException(404, f"There is no audio data with id {id}")

@app.delete("/api/gamelandata/deletedata/{id}")
async def delete_data_gamelan_bali(id: str, current_user: UserInDB = Depends(get_current_user)):
    if current_user:
        response = await delete_gamelan_bali(id)
        if response == True:
            return {"Message":"Successfully deleted gamelan data!", "_idGamelan": id}
        raise HTTPException(404, f"There is no gamelan bali data with id {id}")

@app.put("/api/gamelandata/updatedata/{id}")
async def update_data_gamelan_bali(id: str, nama_gamelan: Annotated[str, Form()] = None, golongan: Annotated[str, Form()] = None, description: Annotated[str, Form()] = None, upacara: Annotated[List[str], Form()] = None, instrument_id: Annotated[List[str], Form()] = None,  current_user: UserInDB = Depends(get_current_user)):
    if current_user:
        response = await update_gamelan_data(id, nama_gamelan, golongan, description, instrument_id, upacara)

        if response:
            return response
        raise HTTPException(404, f"There is no gamelan data with id {id}")

@app.put("/api/gamelandata/approval/{id}")
async def update_data_approval_gamelan_bali(id: str, status: Annotated[str, Form()],  current_user: UserInDB = Depends(get_current_user)):
    if current_user:
        response = await approval_gamelan_data(id, status)

        if response: 
            return response
        raise HTTPException(404, f"There is no gamelan data with id {id}")

@app.get("/api/gamelandata/instrumentid/{nama_gamelan}")
async def get_gamelan_data_with_instrument_attach(nama_gamelan: str, current_user: UserInDB = Depends(get_current_user)):
    if current_user:
        response = await fetch_all_instrument_by_gamelan_name(nama_gamelan)

        if response:
            return response
        raise HTTPException(404, f"There is no Gamelan Data with name {nama_gamelan}")
    
@app.get("/api/gamelandata/gamelanbyinstrumentid/{id}")
async def get_gamelan_data_with_instrument_id(id: str, current_user: UserInDB = Depends(get_current_user)):
    if current_user:
        response = await fetch_all_gamelan_by_instrument_id(id)

        if response:
            return response
        raise HTTPException(404, f"There is no Gamelan Data with id {id}")
    
@app.get("/api/gamelandata/gamelanbygolongan/{golongan}")
async def get_gamelan_data_with_golongan(golongan: str, current_user: UserInDB = Depends(get_current_user)):
    if current_user:
        response = await fetch_specific_gamelan_by_golongan(golongan)

        if response:
            return response
        raise HTTPException(404, f"There is no Gamelan Data with golongan {golongan}")

@app.post("/api/gamelandata/gamelanlistbyid")
async def get_gamelan_data_with_id_list(id: Annotated[List[str], Form()], current_user: UserInDB = Depends(get_current_user)):
    if current_user:
        response = await fetch_list_gamelan_by_id(id)

        if response:
            return response
        raise HTTPException(404, f"There is no Gamelan Data")

@app.get("/api/getdesa/all")
async def fetch_all_desa(current_user: UserInDB = Depends(get_current_user)):
    if current_user:
        response = await fetch_desa_data()

        if response:
            return response
        raise HTTPException(404, "There is no desa data!")
    
@app.get("/api/getdesa/bykecamatanid/{id}")
async def fetch_all_desaby_kecamatan(id: str, current_user: UserInDB = Depends(get_current_user)):
    if current_user:
        response = await fetch_desa_data_by_kecamatan_id(id)

        if response:
            return response
        raise HTTPException(404, "There is no desa data!")

@app.get("/api/getkecamatan/all")
async def fetch_all_kecamatan(current_user: UserInDB = Depends(get_current_user)):
    if current_user:
        response = await fetch_kecamatan_data()

        if response:
            return response
        raise HTTPException(404, "There is no kecamatan data!")
    
@app.get("/api/getkecamatan/bykabupatenid/{id}")
async def fetch_all_kecamatanby_kabupaten(id: str, current_user: UserInDB = Depends(get_current_user)):
    if current_user:
        response = await fetch_kecamatan_data_by_kabupaten_id(id)

        if response:
            return response
        raise HTTPException(404, "There is no kecamatan data!")

@app.get("/api/getkabupaten/all")
async def fetch_all_kabupaten(current_user: UserInDB = Depends(get_current_user)):
    if current_user:
        response = await fetch_kabupaten_data()

        if response:
            return response
        raise HTTPException(404, "There is no kabupaten data!")
    
@app.get("/api/getkabupaten/byprovinsiid/{id}")
async def fetch_all_kabupatenby_provinsi(id: str, current_user: UserInDB = Depends(get_current_user)):
    if current_user:
        response = await fetch_kabupaten_data_by_provinsi_id(id)

        if response:
            return response
        raise HTTPException(404, "There is no kabupaten data!")
    
@app.get("/api/getallalamat/bydesaid/{id}")
async def fetch_all_alamat_by_desa_id(id: str, current_user: UserInDB = Depends(get_current_user)):
    if current_user:
        response = await fetch_alamat_by_id_desa(id)

        if response:
            return response
        raise HTTPException(404, "There is no alamat data!")

@app.post("/api/audioinstrumen/uploadaudio")
async def upload_audio_instrumen_data(instrument_id: Annotated[str, Form()], nama_audio: Annotated[str, Form()], files: list[UploadFile]):
    try: 
        saved_files_audio = []

        for file in files:
            file_content = await file.read()
            print(file.filename)
            response = cloudinary.uploader.upload(file_content, resource_type = "auto")
            saved_files_audio.append(response["secure_url"])

        audio_path = saved_files_audio[0]

        response = await create_audio_data_instrumen(nama_audio, audio_path, instrument_id)
        
        if response:
            return response
    
    except Exception as e:
        return {"message": f"Error occurred: {str(e)}"}

@app.put("/api/audioinstrumen/updateaudio/{id}")
async def update_data_audio_instrumen(id: str, nama_audio: Annotated[str, Form()] = None, files: list[UploadFile] = None):
    try: 
        audio_path = None

        if files and files[0].filename:
            audioPast = await get_audio_instrumen_path_by_id(id)

            if audioPast:
                public_id = extract_public_id(audioPast)

                result = cloudinary.uploader.destroy(
                    public_id,
                    resource_type="video",
                    type="upload",
                    invalidate=True
                )

                print(result)

            saved_files_audio = []

            for file in files:
                file_content = await file.read()
                response = cloudinary.uploader.upload(file_content, resource_type = "auto")
                saved_files_audio.append(response["secure_url"])

            audio_path = saved_files_audio[0]

        response = await update_audio_instrumen_data(id, nama_audio, audio_path)
        
        if response:
            return response
        
    except Exception as e:
        return {"message": f"Error occurred: {str(e)}"}

@app.get("/api/audioinstrumen/fetchallaudio")
async def fetch_audio_instrumen_all_data(current_user: UserInDB = Depends(get_current_user)):
    if current_user:
        response = await fetch_all_audio_instrumen()
        if response:
            return response
        raise HTTPException(404, "There is no audio data with this!")

async def get_audio_instrumen_path_by_id(id: str, current_user: UserInDB = Depends(get_current_user)):
    if current_user:
        response = await fetch_audio_path_instrumen(id)
        if response:
            return response
        raise HTTPException(404, f"There is no audio data with this id {id}!")

@app.get("/api/audioinstrumen/fetch/byinstrumenid/{id}")
async def get_audio_by_instrumen_id(id: str, current_user: UserInDB = Depends(get_current_user)):
    if current_user:
        response = await fetch_audio_by_instrumen_id(id)
        if response:
            return response
        raise HTTPException(404, "There is no data audio Instrumen")

@app.delete("/api/audioinstrumen/deletedataaudio/")
async def delete_data_audio_instrumen_by_id(id: Annotated[List[str], Form()], current_user: UserInDB = Depends(get_current_user)):
    if current_user:
        response = await delete_audio_instrumen_data(id)
        if response == True:
            return "Successfully deleted audio data!"
        raise HTTPException(404, f"There is no audio data with id {id}")

@app.delete("/api/audioinstrumen/deletedataaudiobyid/{id}")
async def delete_audio_instrumen_by_its_id(id: str, current_user: UserInDB = Depends(get_current_user)):
    if current_user:
        response = await delete_audio_instrumen_by_id(id)
        if response == True:
            return "Successfully deleted audio data!"
        raise HTTPException(404, f"There is no audio data with id {id}")
    
@app.post("/api/audioinstrumen/deleteaudioinstrument/manyid")
async def delete_audio_instrumen_by_many_id(id: Annotated[List[str], Form()], current_user: UserInDB = Depends(get_current_user)):
    if current_user:
        response = await delete_audio_instrumen_spesifik_data(id)
        if response == True:
            return "Successfully deleted audio data!"
        raise HTTPException(404, f"There is no audio data with id {id}")

@app.get("/api/getallrole/listrole")
async def get_role_list_data():
    response = await get_role()
    if response:
        return response
    raise HTTPException(404, f"There is no data role!")

@app.get("/api/getallgolongan/listgolongan")
async def get_golongan_list_data():
    response = await get_golongan()
    if response:
        return response
    raise HTTPException(404, f"There is no data golongan!")

@app.get("/api/getallstatus/liststatus")
async def get_status_list_data():
    response = await get_status()
    if response:
        return response
    raise HTTPException(404, f"There is no data status!")

@app.get("/api/fetchinstrument/onlynameandid")
async def fetch_instrument_name_id(current_user: UserInDB = Depends(get_current_user)):
    if current_user:
        response = await fetch_instrumen_only_nama_id()
        if response:
            return response
        raise HTTPException(404, f"There is no instrument data")