from fileinput import filename
from glob import escape
from re import L, T
from tkinter.tix import Tree
from typing import List
from fastapi import FastAPI, Query
from fastapi.middleware.cors import CORSMiddleware
from database.session import SessionLocal
from database.schemas import Voice, user_Login, new_Project, Scene_Rscs, save_Info, save_Image, play_Dict,voice_Update, voice_Request, SnsType, UserRegister,Voice, UserDelete, UserUpdate
from database.models import User, Project
from fastapi import Depends, HTTPException, BackgroundTasks, Body, UploadFile
from fastapi.responses import FileResponse, StreamingResponse
from metadata.get_Metadata import get_Metadata_doi
from sqlalchemy.orm import Session
import urllib.request
import requests
from PIL import Image
from mutagen.mp3 import MP3
import os
import logging

from gtts import gTTS
from moviepy.editor import *
import bcrypt
from auth.auth_handler import decodeJWT, signJWT
from auth.auth_bearer import JWTBearer
import random
import string
from typing import Optional
import pdfminer
from pdfminer.high_level import extract_text
import shutil
from scenes.Scene_Manager import scene_Creator
import datetime
import time
import json

app = FastAPI(title="Medcon Editor", 
              description="논문 요약 및 프레젠테이션 생성 툴", 
              version="V1", 
              contact={"name" : "James Kim", "email" : "james@catbellcompany.com"})

origins = [
    "*"
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
    expose_headers= ["*"]
)

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
def is_email_exist(email: str, db : Session = Depends(get_db)):
    user = db.query(User).filter(email == email).first()
    if user != None:
        return True
    return False

def is_key_exist(key : str, db : Session = Depends(get_db)):
    user = db.query(User).filter(key == key).first()
    if user:
        return True
    return False
description = """
    /user/register/{sns_type}
    
    Input
    SnsType
    {facebook: str = "facebook"
    google: str = "google"}
    
    UserRegister
    user_id : str = None
    user_pw : str = None
    picture : str = None
    locale : str = None
    
    Output
    {"success" : False, "code" : "000", "message" : "이메일과 비밀번호를 반드시 입력해 주시기 바랍니다."}
    {"success" : False, "code" : "001", "message" : "이미 존재하는 이메일 주소"}
    {"success" : False, "code" : "002", "message" : "지원하지 않는 플랫폼"}
    
    {"success" : True, "message" : "회원가입 성공", "data" : token}
    

"""
@app.post("/user/register/{sns_type}", status_code=200, tags=["User"], description = description)
async def register_user(sns_type : SnsType, reg_info: UserRegister, db : Session = Depends(get_db)):
    if sns_type == SnsType.google or sns_type == SnsType.facebook:
        user = db.query(User).filter(User.email == reg_info.user_id).first()

        if not reg_info.user_id or not reg_info.user_pw:
            raise HTTPException(status_code=400, detail={"success" : False, "code" : "000", "message" : "이메일과 비밀번호를 반드시 입력해 주시기 바랍니다."})
        if user:
            raise HTTPException(status_code=400, detail={"success" : False, "code" : "001", "message" : "이미 존재하는 이메일 주소"})
        hash_pw = bcrypt.hashpw(reg_info.user_pw.encode("utf-8"), bcrypt.gensalt())
        
        key = ''.join(random.choice(string.ascii_uppercase + string.digits) for _ in range(10))
        user = db.query(User).filter(User.key == key).first()
        
        while user != None:
            key = ''.join(random.choice(string.ascii_uppercase + string.digits) for _ in range(10))
            user = db.query(User).filter(User.key == key).first()
        
        new_user = User(user_id = reg_info.user_id, user_pw = hash_pw, email = reg_info.user_id, key = key, locale = reg_info.locale, picture = reg_info.picture, create_dt = datetime.datetime.now(), last_mod_dt = datetime.datetime.now())
        db.add(new_user)
        db.commit()
        
        project_dir = os.getcwd().replace("\\", "/") + "/projects/" + key
        
        if not os.path.exists(project_dir):
            os.mkdir(project_dir)
        new_token = signJWT(reg_info.user_id)
        token = new_token['access_token']
        
        return HTTPException(status_code = 200, detail={"success" : True, "message" : "회원가입 성공", "data" : token})
    
    return HTTPException(status_code=400, detail={"success" : False, "code" : "002", "message" : "지원하지 않는 플랫폼"})

description = """
    /user/delete
    Input
    {Authorization : 'token'}
    
    Output
    {"success" : False, "code" : "00", "message" : "아이디가 일치하는 계정이 없습니다."}
    {"success" : True, "message" : "계정삭제 완료"}
"""
@app.post("/user/delete",tags=["User"], description = description)
async def delete_user(bearer: JWTBearer = Depends(JWTBearer()), db:Session = Depends(get_db)):
    user = db.query(User).filter(User.user_id == decodeJWT(bearer)['user_id']).first()
    if user == None:
        raise HTTPException(status_code = 200, detail={"success" : False, "code" : "00", "message" : "아이디가 일치하는 계정이 없습니다."})
    
    project_dir_origin = os.getcwd().replace("\\", "/") + "/projects/" + user.key
    projects = os.listdir(project_dir_origin)
    
    for project in projects:
        project_dir = project_dir_origin + "/" + project
        img_dir = project_dir + "/sources/images"
        voice_dir = project_dir + "/voices"
        if os.path.exists(img_dir):
            imgs = os.listdir(img_dir)
            for img in imgs:
                print(img_dir + "/" + img)
                os.remove(img_dir + "/" + img)
            os.rmdir(img_dir)    
            os.rmdir(project_dir + "/sources") 
        if os.path.exists(voice_dir):
            voices = os.listdir(voice_dir)
            for voice in voices:
                os.remove(voice_dir + "/" + voice)
            os.rmdir(voice_dir)
        os.rmdir(project_dir)
    os.rmdir(project_dir_origin)
    

    projects_from_db = db.query(Project).filter(Project.user_key == user.key).all()
    if projects_from_db == [] or projects_from_db == None:
        pass
    else:
        for project in projects_from_db:
            pr = db.get(Project, project.id)
            db.delete(pr)
            db.commit()
            
    user = db.get(User, user.id)
    
    db.delete(user)
    
    db.commit()
    raise HTTPException(status_code = 200, detail={"success" : True, "message" : "계정삭제 완료"})
description ="""
    /user/update
    
    Input
    user_name : str
    picture : str
    locale : str
    {Authorization : 'token'}
    
    Output
    {"success" : False, "code" : "00", "message" : "아이디가 일치하는 계정이 없습니다."}
    {"success" : True, "message" : "저장 성공", "save_time" : ""}
"""
@app.post("/user/update",tags=["User"], description = description)
async def update_user(update_info : UserUpdate, bearer: JWTBearer = Depends(JWTBearer()), db:Session = Depends(get_db)):
    user = db.query(User).filter(User.user_id == decodeJWT(bearer)['user_id']).first()
    if user == None:
        raise HTTPException(status_code  =200, detail={"success" : False, "code" : "00", "message" : "아이디가 일치하는 계정이 없습니다."})
    user.user_name = update_info.user_name
    user.picture = update_info.picture
    user.locale = update_info.locale
    user.doi_bag ="|".join(update_info.doi_list) 
    user.last_mod_dt = datetime.datetime.now()
    
    db.commit()
    raise HTTPException(status_code =200, detail={"success" : True, "message" : "저장 성공", "save_time" : str(datetime.datetime.now())})

## 유저 로그인 
description = """
    Login API

    Input :
    User_Login
    {user_id, user_pw}

    Output:
    
    로그인 성공 시
    {"success" : True, "message" : "로그인 되었습니다.", "token" : token, "user_key" : ""} -> 로그인 성공

    로그인 실패 시
    {"success" : False, "code" : "00", "message" : "아이디가 일치하는 계정이 없습니다."} -> 아이디가 일치하지 않을때
    {"success" : False, "code" : "01", "message" : "비밀번호가 일치하지 않습니다."} -> 비밀번호가 일치하지 않을때

"""
@app.post("/user/login", tags=["User"], description=description)
async def user_login(user: user_Login, db : Session = Depends(get_db)):
    user_log = db.query(User).filter(User.user_id == user.user_id).first()
    
    if user_log == None:
        raise HTTPException(status_code  =200, detail={"success" : False, "code" : "00", "message" : "아이디가 일치하는 계정이 없습니다."})
    else:
        pass
    
    user_log = db.query(User).filter(User.user_id == user.user_id).first().__dict__
    
    if not bcrypt.checkpw(user.user_pw.encode('utf-8'), user_log['user_pw'].encode('utf-8')):
        raise HTTPException(status_code = 200, detail={"success" : False, "code" : "01", "message" : "비밀번호가 일치하지 않습니다."})
    
    else:
        new_token = signJWT(user_log['user_id'])
        token = new_token['access_token']
        raise HTTPException(status_code= 200, detail = {"success" : True, "message" : "로그인 되었습니다.", "token" : token, "user_key" : user_log['key']})
description = """
    /user/get

    Input : -H(헤더) Authorization: Bearer
    {Authorization : 'token'} 

    Output:
    승인 : {"success" : True,  "message" : "승인됨", "data" : user_data}
    토큰 만료 : {"success" : False, "code" : "01", "message" : "토큰이 만료되었습니다."}
    미승인 : {"success" : False, "code" : "00", "message" : "해당 계정이 존재하지 않습니다."}
"""
@app.get("/user/get", tags=["User"], description = description)
async def get_user(bearer: JWTBearer = Depends(JWTBearer()), db : Session = Depends(get_db)):
    if decodeJWT(bearer) == None:
        raise HTTPException(status_code = 200, detail={"success" : False, "code" : "01", "message" : "토큰이 만료되었습니다."})
    
    user = db.query(User).filter(User.user_id == decodeJWT(bearer)['user_id']).first()
    if user == None:
        raise HTTPException(status_code = 200, detail={"success" : False, "code" : "00", "message" : "해당 계정이 존재하지 않습니다."})
    else: 
        user_dict = user.__dict__
        doi_list = user_dict['doi_bag']
        if doi_list == None:
            doi_list = ""
        user_data = {
            "email" : user_dict['user_id'],
            "picture" : user_dict['picture'],
            "locale" : user_dict['locale'],
            "user_name" : user_dict['user_name'],
            "doi_list" : doi_list.split("|")
        }
        raise HTTPException(status_code = 200, detail={"success" : True,  "message" : "승인됨", "data" : user_data})

description = """
    User Authorization API

    Input : -H(헤더) Authorization: Bearer
    {Authorization : 'token'} 

    Output:
    승인 : {"success" : True, "message" : "승인됨"}"}
    토큰 만료 : {"success" : False, "code" : "01", "message" : "토큰이 만료되었습니다."}
    미승인 : {"success" : False, "code" : "00", "message" : "해당 계정이 존재하지 않습니다."}
"""
@app.get("/user/me", tags=["User"], description=description)
async def user_me(bearer: JWTBearer = Depends(JWTBearer()), db : Session = Depends(get_db)):
    if decodeJWT(bearer) == None:
        raise HTTPException(status_code = 200, detail={"success" : False, "code" : "01", "message" : "토큰이 만료되었습니다."})
    
    user = db.query(User).filter(User.user_id == decodeJWT(bearer)['user_id']).first()
    if user == None:
        raise HTTPException(status_code = 200, detail={"success" : False, "code" : "00", "message" : "해당 계정이 존재하지 않습니다."})
    else: 
        user_dict = user.__dict__

        raise HTTPException(status_code = 200, detail={"success" : True,  "message" : "승인됨", "user_key" : user_dict["key"]})

#project_key = ''.join(random.choice(string.ascii_lowercase + string.digits) for _ in range(10))
description = """
    /project/create
    
    Input
    {
    project_name : str
    doi : str
    author_image : str
    template_type : int
    }
    
    Output
    {"success" : False, "code" : "00", "message" : "해당 계정이 존재하지 않습니다."}
    {"success" : False, "code" : "03", "message" : "메타데이터를 불러올 수 없습니다."}
    {"success" : False, "code" : "04", "message" : "이미지가 비어있습니다."}
    {"success" : False, "code" : "02", "message" : "프로젝트 이름 중복"}
    
    {"success" : True, "message" : "프로젝트 생성 완료", "data" : data}
"""
@app.post("/project/create", tags=["Project"], description = description) # 프로젝트 생성
def project_create(project : new_Project, bearer : JWTBearer = Depends(JWTBearer()), db : Session = Depends(get_db)):
    
    user = db.query(User).filter(User.user_id == decodeJWT(bearer)['user_id']).first()
    if user == None:
        raise HTTPException(status_code = 200, detail={"success" : False, "code" : "00", "message" : "해당 계정이 존재하지 않습니다."})
    else:
        projects = db.query(Project).filter(Project.user_key == user.key).all()
        
        if len(projects) == 0: # 첫 프로젝트 생성
            project_key = ""
            while True: # 중복되지 않는 프로젝트 키 생성
                
                # 새 프로젝트 키 생성
                new_project_key = ''.join(random.choice(string.ascii_lowercase + string.digits) for _ in range(10)) 
                
                #프로젝트 중복 확인
                project_ = db.query(Project).filter(Project.project_key == new_project_key).first()
                if project_ == None: # 중복되지 않을경우
                    project_key = new_project_key
                    break
            
                else: # 중복될 경우 다시 생성
                    pass
            new_project = Project(project_name = project.project_name, project_key = project_key, user_key = user.key, json = None, doi = project.doi, author_img = project.author_image)
            
            #작업공간 생성
            image_path = ""
            project_dir = os.getcwd().replace("\\", "/") + "/projects" + "/" + user.key + "/" + project_key
            
            if not os.path.exists(project_dir):
                os.mkdir(project_dir)
            if not os.path.exists(project_dir + "/sources"):
                os.mkdir(project_dir + "/sources")     
            if not os.path.exists(project_dir + "/sources/images"):
                os.mkdir(project_dir + "/sources/images")
            metadata = {}
            try:
                metadata = get_Metadata_doi(project.doi)
                if metadata == None:
                    raise HTTPException(status_code = 200, detail={"success" : False, "code" : "03", "message" : "메타데이터를 불러올 수 없습니다."})
            except:
                raise HTTPException(status_code = 200, detail={"success" : False, "code" : "01", "message" : "주소가 잘못 됬거나 적용되지 않은 DOI 입니다."})
            
            i = 0
            img_result = []
            img_src_path = project_dir + "/sources/images/"
            if metadata['images'] == None:
                raise HTTPException(status_code = 200, detail={"success" : False, "code" : "04", "message" : "이미지가 비어있습니다."})
            if metadata['images'] != [] or metadata['images'] != None:
                for img in metadata['images']:
                    if i > 9:
                        name = "source_img" + str(i) +".png"
                        file_name = img_src_path + name
                    elif i < 10:
                        name = "source_img0" + str(i) +".png"
                        file_name = img_src_path + name
                    
                    urllib.request.urlretrieve(img, file_name)
                    image = Image.open(file_name)
                    ratio = image.width / image.height
                    image = image.convert('RGB')
                    image = image.resize((int(580 * ratio), 580), Image.LANCZOS)
                    img_width = int(580 * ratio)
                    
                    if img_width > 1560:
                        ratio = 1 / ratio
                        img_width = 1560
                        image = image.resize((1560, int(ratio*1560)), Image.LANCZOS)
                    image.save(file_name)
                    image.close()
                    
                    img_result.append(["http://218.52.115.188:7000/source/image/{}/{}".format(project_key, name), img_width])
                    
                    i += 1
            else:
                pass
            authors = ",".join(metadata['authors'])
            print(authors)
            scene_resources = Scene_Rscs(user_key=user.key, project_name=project.project_name, project_key=project_key, template_type = project.template_type, article_title=metadata['article_title'], correspond=metadata['correspondence'], authors = authors, doi=metadata['doi'], copyright=metadata['copyright'], image_url_list = img_result, abstract=metadata['abstract'], keywords=metadata['keywords'], author_img=project.author_image)
            scene_maker = scene_Creator(scene_info = scene_resources, path=image_path)

            json_ = scene_maker.creat_json()
            json_ = json_.replace("'", '\"').replace('\a', "").replace("\t", "").replace("\r", "").replace("\b", "").replace("\f", "").replace('\xa0',' ')
            db.add(new_project)
            db.commit()
            project = db.query(Project).filter(Project.project_key == project_key).first()
            
            project.json = json_
            project.create_dt = datetime.datetime.now()
            project.last_mod_dt = datetime.datetime.now()
            
            db.commit()
            
            
        else: # 기존 프로젝트가 존재할 시
            for pr in projects:
                if project.project_name == pr.project_name:
                    raise HTTPException(status_code = 200, detail={"success" : False, "code" : "02", "message" : "프로젝트 이름 중복"})
                else:
                    pass
                
            project_key = ""
            while True: # 중복되지 않는 프로젝트 키 생성
                # 새 프로젝트 키 생성
                new_project_key = ''.join(random.choice(string.ascii_lowercase + string.digits) for _ in range(10)) 
                
                #프로젝트 중복 확인
                project_ = db.query(Project).filter(Project.project_key == new_project_key).first()
                if project_ == None: # 중복되지 않을경우
                    project_key = new_project_key
                    break
                
                else: # 중복될 경우 다시 생성
                    pass
            new_project = Project(project_name = project.project_name, project_key = project_key, user_key = user.key, json = None, doi = project.doi, author_img = project.author_image)
            
            
            
            #작업공간 생성
            image_path = ""
            project_dir = os.getcwd().replace("\\", "/") + "/projects" + "/" + user.key + "/" + project_key
            if not os.path.exists(project_dir):
                os.mkdir(project_dir)
            if not os.path.exists(project_dir + "/sources"):
                os.mkdir(project_dir + "/sources")     
            if not os.path.exists(project_dir + "/sources/images"):
                os.mkdir(project_dir + "/sources/images")
            
            metadata = {}
            try:
                metadata = get_Metadata_doi(project.doi)
                if metadata == None:
                    raise HTTPException(status_code = 200, detail={"success" : False, "code" : "03", "message" : "메타데이터를 불러올 수 없습니다."})
            except:
                raise HTTPException(status_code = 200, detail={"success" : False, "code" : "01", "message" : "주소가 잘못 됬거나 적용되지 않은 DOI 입니다."})
            
            i = 0
            img_result = []
            img_src_path = project_dir + "/sources/images/"
            
            if metadata['images'] == None:
                raise HTTPException(status_code = 200, detail={"success" : False, "code" : "04", "message" : "이미지가 비어있습니다."})
            if metadata['images'] != [] or metadata['images'] != None:
                for img in metadata['images']:
                    if i > 9:
                        name = "source_img" + str(i) +".png"
                        file_name = img_src_path + name
                    elif i < 10:
                        name = "source_img0" + str(i) +".png"
                        file_name = img_src_path + name
                    
                    urllib.request.urlretrieve(img, file_name)
                    
                    image = Image.open(file_name)
                    ratio = image.width / image.height
                    
                    image = image.resize((int(580 * ratio), 580), Image.LANCZOS)
                    resized_width = int(580 * ratio)
                    image = image.convert('RGB')
                    if resized_width > 1560:
                        ratio = 1 / ratio
                        resized_width = 1560
                        image = image.resize((1560, int(ratio*1560)), Image.LANCZOS)
                    
                    image.save(file_name)
                    image.close()
                    
                    img_result.append(["http://218.52.115.188:7000/source/image/{}/{}".format(project_key, name), resized_width])
                    
                    i += 1
            else:
                pass
            authors = ", ".join(metadata['authors'])
            
            scene_resources = Scene_Rscs(user_key=user.key, project_name = project.project_name, author_img=project.author_image, template_type = project.template_type, project_key=project_key, article_title=metadata['article_title'], correspond=metadata['correspondence'], authors = authors, doi=metadata['doi'], copyright=metadata['copyright'], image_url_list=img_result, abstract=metadata['abstract'], keywords= metadata['keywords'])
            scene_maker = scene_Creator(scene_info = scene_resources, path=image_path)

            json_ = scene_maker.creat_json()
            json_ = json_.replace("'", '\"').replace('\a', "").replace("\t", "").replace("\r", "").replace("\b", "").replace("\f", "").replace('\xa0',' ')
            
            db.add(new_project)
            db.commit()

            project = db.query(Project).filter(Project.project_key == project_key).first()
            project.json = json_
            project.create_dt = datetime.datetime.now()
            project.last_mod_dt = datetime.datetime.now()
            
            db.commit()
            
        
        project = db.query(Project).filter(Project.project_key == project_key).first()
        
        data = {"project_name" : project.project_name, "project_key" : project_key, "json" : json.loads(project.json.replace('{"id": "Image_centerImg", "name": "StaticImage", "stroke": null, "strokeWidth": 0, "left": 510.0, "top": 210, "width": 900, "height": 620, "opacity": 1, "originY": "top", "scaleX": 1, "scaleY": 1, "type": "StaticImage", "visible": true, "src": "", "cropX": 0, "cropY": 0, "metadata": {}},', '')), "create_dt" : str(project.create_dt)}
        
        raise HTTPException(status_code=200, detail={"success" : True, "message" : "프로젝트 생성 완료", "data" : data})

description = """
    /project/get
    Input
    -H(헤더) Authorization: Bearer
    {Authorization : 'token'}
    
    Output
    {"success" : False, "message" : "프로젝트가 비어있습니다."}
    {"success" : True, "message" : "프로젝트 불러오기 성공", "data" : result}
    
"""
@app.get("/project/get", tags=["Project"], description = description) #모든 프로젝트 불러오기
def project_get_all(bearer : JWTBearer = Depends(JWTBearer()), db : Session = Depends(get_db)):
    user = db.query(User).filter(User.user_id == decodeJWT(bearer)['user_id']).first()
    projects = db.query(Project).filter(Project.user_key == user.key).all()
    if len(projects) == 0:
        raise HTTPException(status_code = 200, detail={"success" : False, "message" : "프로젝트가 비어있습니다."})
    else:
        result = []
        for project in projects:
            project_dict = project.__dict__
            
            result.append({"project_key" : project_dict["project_key"], "project_name" : project_dict["project_name"], "doi" : project_dict["doi"],"thumbnail" : project_dict['thumbnail'], "create_dt" : str(project_dict['create_dt']), "last_mod_dt" : str(project_dict["last_mod_dt"])})
        raise HTTPException(status_code = 200, detail={"success" : True, "message" : "프로젝트 불러오기 성공", "data" : result}) 

description = """
    /project/get/{project_key}
    Input
    project_key : str
    {Authorization : 'token'}
    
    Output
    {"success" : False, "message" : "해당 프로젝트가 존재하지 않습니다."}
    {"success" : True, "message" : "프로젝트 불러오기 성공", "data" : result}
"""
@app.get("/project/get/{project_key}", tags=["Project"], description = description) #특정 프로젝트 불러오기
def project_get(project_key : str, bearer : JWTBearer = Depends(JWTBearer()), db : Session = Depends(get_db)):
    user = db.query(User).filter(User.user_id == decodeJWT(bearer)['user_id']).first()
    project = db.query(Project).filter(Project.project_key == project_key and Project.user_key == user.key).first()
    if project ==None:
        raise HTTPException(status_code = 200, detail={"success" : False, "message" : "해당 프로젝트가 존재하지 않습니다."})
    else:
        project_dict = project.__dict__
        
        if project_dict['voices'] == None or project_dict['voices'] == "":
            voices = []
        else:
            voices = project.voices.split("|")
            if voices == [] or voices[0] == '':
                voices = []
            else:
                tmp = []
                for voice in voices:
                    tmp.append(json.loads(voice))
                voices = tmp

        result = {"project_key" : project_dict["project_key"], "project_name" : project_dict["project_name"], "user_key" : project_dict["user_key"], "json_txt" : json.loads(project_dict["json"].replace('{"id": "Image_centerImg", "name": "StaticImage", "stroke": null, "strokeWidth": 0, "left": 510.0, "top": 210, "width": 900, "height": 620, "opacity": 1, "originY": "top", "scaleX": 1, "scaleY": 1, "type": "StaticImage", "visible": true, "src": "", "cropX": 0, "cropY": 0, "metadata": {}},', '')), "doi" : project_dict["doi"], "author_image": project_dict['author_img'],"thumbnail" : project.thumbnail, "voices" : voices, "create_dt" : str(project_dict['create_dt']), "last_mod_dt" : str(project_dict['last_mod_dt'])}
        raise HTTPException(status_code = 200, detail={"success" : True, "message" : "프로젝트 불러오기 성공", "data" : result})

description = """
    데이터 저장
    /project/update
    input : 
        user_key : str 
        project_key : str
        json_txt : str
        voices : list -> 음성 URL 리스트를 넣어주세요
    
    output :
        {"success" : False, "message" : "프로젝트가 존재하지 않습니다."}
        {"success" : False, "message" : "데이터가 비어있습니다."}
        {"success" : True, "message" : "데이터 저장 완료", "data" : project_dict['json']}
"""
@app.post("/project/update", tags=["Project"], description = description) ## 프로젝트 저장
def update_project(saving : save_Info, bearer : JWTBearer = Depends(JWTBearer()), db : Session = Depends(get_db)):
    user = db.query(User).filter(User.user_id == decodeJWT(bearer)['user_id']).first()

    project = db.query(Project).filter(Project.project_key == saving.project_key and Project.user_key == user.key).first()
    if project == None:
        raise HTTPException(status_code = 200, detail={"success" : False, "message" : "프로젝트가 존재하지 않습니다."})
    else:
        if saving.json_input == None or saving.json_input == {}:
            raise HTTPException(status_code = 200, detail={"success" : False, "message" : "json 정보가 비어있습니다."})
        else:
            json_text = json.dumps(saving.json_input)
            project.json = json_text.replace('"Unknown Type: null"', "null")

            tmp = []
            
            for voice in saving.voices:
                tmp.append(json.dumps(dict(voice)))    
            
            project.voices = "|".join(tmp)
            project.last_mod_dt = datetime.datetime.now()
            project.thumbnail = saving.thumbnail
            db.commit()
            
            project = db.query(Project).filter(Project.project_key == saving.project_key).first()
            project_dict = project.__dict__
            voices = project.voices.split("|")
            print(voices)
            if voices == [] or voices[0] == '':
                voices = []
                
            else:
                tmp = []
                for voice in voices:
                    tmp.append(json.loads(voice))
                voices = tmp
            
            
            raise HTTPException(status_code = 200, detail={"success" : True, "message" : "데이터 저장 완료", "data" : json.loads(project_dict['json'].replace('{"id": "Image_centerImg", "name": "StaticImage", "stroke": null, "strokeWidth": 0, "left": 510.0, "top": 210, "width": 900, "height": 620, "opacity": 1, "originY": "top", "scaleX": 1, "scaleY": 1, "type": "StaticImage", "visible": true, "src": "", "cropX": 0, "cropY": 0, "metadata": {}},', '')), "thumbnail" : project_dict['thumbnail'], "voices" : voices, "last_mod_dt" : str(project_dict['last_mod_dt'])})

description = """
    /project/delete/{project_key}
    
    Input
    project_key : str
    {Authorization : 'token'}
    
    Output
    {"success" : False, "message" : "프로젝트가 존재하지 않습니다."}
    {"success" : True, "message" : "프로젝트 삭제 성공"}
"""
@app.delete("/project/delete/{project_key}", tags=["Project"], description = description) # 프로젝트 삭제
def delete_project( project_key : str, bearer : JWTBearer = Depends(JWTBearer()), db : Session = Depends(get_db)):
    user = db.query(User).filter(User.user_id == decodeJWT(bearer)['user_id']).first()

    project = db.query(Project).filter(Project.user_key == user.key).filter(Project.project_key == project_key).first()
    if project == None:
        raise HTTPException(status_code = 200, detail={"success" : False, "message" : "프로젝트가 존재하지 않습니다."})
    else:
        project_dict = project.__dict__
        
        path = os.getcwd().replace("\\","/") + "/projects/" + user.key + "/" + project_key + "/sources/" + "voices"
        if os.path.exists(path=path):
            files = os.listdir(path=path)
            for file in files:
                os.remove(path + "\\" + file) 
            os.rmdir(path=path)
        
        path = os.getcwd().replace("\\","/") + "/projects/" + user.key + "/" + project_key + "/sources/" + "images"
        if os.path.exists(path=path):
            files = os.listdir(path=path)
            for file in files:
                os.remove(path + "\\" + file) 
            os.rmdir(path=path)
        if os.path.exists(os.getcwd().replace("\\","/") + "/projects/" + user.key + "/" + project_key + "/sources"):
            os.rmdir(os.getcwd().replace("\\","/") + "/projects/" + user.key + "/" + project_key + "/sources")
        
        path = os.getcwd().replace("\\","/") + "/projects/" + user.key + "/" + project_key
        if os.path.exists(path=path):
            os.rmdir(os.getcwd().replace("\\","/") + "/projects/" + user.key + "/" + project_key)
        
        pr = db.get(Project, project_dict['id'])
        db.delete(pr)
        db.commit()
        raise HTTPException(status_code = 200, detail={"success" : True, "message" : "프로젝트 삭제 성공"})

description = """
    플레이 정보 저장
    input : 
        project_key : string 
        play : list
    
    output :
        
        False
        {"success" : False, "code" : "00", "message" : "해당 프로젝트가 존재하지 않습니다."}
        {"success" : False, "code" : "01", "message" : "플레이 정보 저장 실패"}
        
        True
        {"success" : True, "message" : "플레이 정보 저장 성공"}

"""
@app.post("/project/play/update", tags=["Project"], description=description)
def post_project_Play(play_info : play_Dict, bearer : JWTBearer = Depends(JWTBearer()), db : Session = Depends(get_db)):
    user = db.query(User).filter(User.user_id == decodeJWT(bearer)['user_id']).first()
    project = db.query(Project).filter(Project.project_key == play_info.project_key and Project.user_key == user.key).first()
    if project == None:
        raise HTTPException(status_code=200, detail={"success" : False, "code" : "00", "message" : "해당 프로젝트가 존재하지 않습니다."})
    else:
        pass
    tmp = []
    for play_json in play_info.project_play:
        tmp.append(json.dumps(dict(play_json)))
    
    project.play = "|".join(tmp) 
    project.frame = json.dumps(dict(play_info.project_frame))
    
    db.commit()
    project = db.query(Project).filter(Project.project_key == play_info.project_key).first()
    plays = project.play.split("|")
    tmp = []
    for p in plays:
        tmp.append(json.loads(p))

    raise HTTPException(status_code=200, detail={"success" : True, "message" : "플레이 정보 저장 성공", "data" : {"play" : tmp, "project_frame" : dict(play_info.project_frame)}})

description = """
    플레이 정보 불러오기
    input : 
        project_key : string 
    
    output :
        
        False
        {"success" : False, "message" : "해당 프로젝트가 존재하지 않습니다."}
        
        True
        {"success" : True, "code" : "00", "message" : "빈 플레이 정보", "data" : []}
        {"success" : True, "code" : "01",  "message" : "플레이 정보 불러오기 성공", "data" : play}

"""
@app.get("/project/play/get/{project_key}", tags=["Project"], description = description)
def get_project_Play(project_key : str, bearer : JWTBearer = Depends(JWTBearer()), db : Session = Depends(get_db)):
    user = db.query(User).filter(User.user_id == decodeJWT(bearer)['user_id']).first()

    project = db.query(Project).filter(Project.project_key == project_key and Project.user_key == user.key).first()
    if project == None:
        raise HTTPException(status_code=200, detail={"success" : False, "code" : "00", "message" : "해당 프로젝트가 존재하지 않습니다."})
    else:
        pass
    tmp = []
    if project.play == None:
        play = []
    else:
        play = project.play.split("|")
        
        for p in play:
            tmp.append(json.loads(p))
        play =tmp
    frame = json.loads(project.frame)
    
    if play == []:
        raise HTTPException(status_code=200, detail={"success" : True, "code" : "00", "message" : "빈 플레이 정보", "data" : []})
    else:
        raise HTTPException(status_code=200, detail={"success" : True, "code" : "01", "message" : "플레이 정보 불러오기 성공", "data" : {"play" : play, "project_frame" : frame}})
    
description = """
    DOI 메타데이터 불러오기

    Input :
    DOI 주소 : Sring

    Output:
        "metadata["journal_title"]" : "Journal Title", 
        "article_title" : "Article Title", 
        "keywords" : [], 
        "correspondence" : "Correspond to",
        "copyright" : "Copyright", 
        "doi" : "doi",
        "authors" : [],
        "abstract" : [], 
        "italics" : [], 
        "images" : [],
        "published" : "Published"
    
    ERROR CODE : 
        {"success" : False, "code" : "01", "message" : "주소가 잘못 됬거나 적용되지 않은 DOI 입니다."}
        {"success" : False, "code" : "02", "message" : "데이터를 불러올 수 없습니다."}
    SUCCESS:
        {"success" : True, "message" : "데이터 불러오기 성공", "data" : result}

"""
@app.get("/metadata/doi", tags=["Metadata"], description=description)
def get_metadata_doi(doi : str):
    try:
        metadata = get_Metadata_doi(doi)
    except:
        raise HTTPException(status_code = 200, detail={"success" : False, "code" : "01", "message" : "주소가 잘못 됬거나 적용되지 않은 DOI 입니다."})
    
    try:
        result = {"journal_title" : metadata["journal_title"], "article_title" : metadata["article_title"], "keywords" : metadata["keywords"].replace("\xa0", " ").replace('\\', ""), "correspondence" : metadata["correspondence"], "copyright" : metadata["copyright"], "doi" : metadata["doi"], "authors" :  ";".join(metadata["authors"]), "abstract" : metadata["abstract"],  "images" : metadata["images"], "published" : metadata["published"]}
    except:
        raise HTTPException(status_code = 200, detail={"success" : False, "code" : "02", "message" : "데이터를 불러올 수 없습니다."})
    
    raise HTTPException(status_code = 200, detail={"success" : True, "message" : "데이터 불러오기 성공", "data" : result})

@app.post("/metadata/pdf",  tags=["Metadata"])
def get_metadata_pdf(pdf : UploadFile):
    with open(pdf.filename, "wb") as buffer:
        shutil.copyfileobj(pdf.file, buffer)
    txt = extract_text(pdf.filename)
    
    doi = txt[txt.find("http"):]
    doi = doi[ : doi.find("\n")]
    doi = doi.replace("dx.", "").replace("http","https")
    
    if "https" not in doi:
        doi = "https://" + doi
        
    doi = doi.replace("httpss", "https")

    try:
        print(doi)
        metadata = get_Metadata_doi(doi)
    except:
        os.remove(pdf.filename)
        raise HTTPException(status_code = 200, detail={"success" : False, "code" : "01", "message" : "주소가 잘못 됬거나 적용되지 않은 DOI 입니다."})
    
    try:

        result = {"journal_title" : metadata["journal_title"], "article_title" : metadata["article_title"], "keywords" : metadata["keywords"].replace("\xa0", " ").replace('\\', ""), "correspondence" : metadata["correspondence"], "copyright" : metadata["copyright"], "doi" : metadata["doi"], "authors" :  ";".join(metadata["authors"]), "abstract" : metadata["abstract"],  "images" : metadata["images"], "published" : metadata["published"]}
        print(result)
    except:
        os.remove(pdf.filename)
        raise HTTPException(status_code = 200, detail={"success" : False, "code" : "02", "message" : "데이터를 불러올 수 없습니다."})
    
    os.remove(pdf.filename)
    
    raise HTTPException(status_code = 200, detail={"success" : True, "message" : "데이터 불러오기 성공", "data" : result})



def mk_voices(dir : str, project_id : str, texts : List[Voice]):
    for text in texts:
        tts = gTTS(text = text.text, lang="en")
        if text.id < 10:
            filename = dir + "/" + project_id + "_voice_0" + str(text.id) + ".mp3"
        else:
            filename = dir + "/" + project_id + "_voice_" + str(text.id) + ".mp3"
        tts.save(filename)
description = """
    [POST]
    /voice/create
    
    Input
    project_key : str
    text_list : List[Voice]
    
    Voice
    { id : int
      text : str
    }
    
    {Authorization : 'token'}
    
    Output
    {"success" : False, "code" : "00", "message" : "해당 계정이 존재하지 않습니다."}
    {"success" : False, "code" : "01", "message" : "해당 프로젝트가 존재하지 않습니다."}
"""
@app.post("/voice/create", tags = ['Voices'], description = description)
def create_voices(voice_req : voice_Request, background_task : BackgroundTasks, bearer : JWTBearer = Depends(JWTBearer()), db : Session = Depends(get_db) ):
    user = db.query(User).filter(User.user_id == decodeJWT(bearer)['user_id']).first()
    if user == None:
        raise HTTPException(status_code = 200, detail={"success" : False, "code" : "00", "message" : "해당 계정이 존재하지 않습니다."})
    
    project = db.query(Project).filter(Project.project_key == voice_req.project_key).first()
    
    if project == None:
        raise HTTPException(status_code=200, detail={"success" : False, "code" : "01", "message" : "해당 프로젝트가 존재하지 않습니다."})
    
    voices_dir = os.getcwd().replace("\\", "/") + "/projects/" + user.key + "/" + voice_req.project_key +"/sources/voices"
    if not os.path.exists(voices_dir):
        os.mkdir(voices_dir)
    else:
        audio_list = os.listdir(voices_dir)
        if audio_list != []:
            for audio in audio_list:
                os.remove(voices_dir + "/" + audio)
    
    project.voices = ""
    tmp = []
    for voice_json in voice_req.text_list:
        new_json = {
            "id" : voice_json.id,
            "url" : "",
            "text" : voice_json.text,
            "duration" : 0
        }
        tmp.append(json.dumps(dict(new_json)))
    print("|".join(tmp))
    project.voices = "|".join(tmp)
    db.commit()
    seq_f = open(voices_dir + "/" + "seq.txt", "w")
    seq_f.write(str(len(voice_req.text_list)))
    seq_f.close()

    background_task.add_task(mk_voices, voices_dir, voice_req.project_key, voice_req.text_list)
    
description = """
    [get]
    /voice/get/{project_key}
    Authorization

    Failed
    {"success" : False, "code" : "00", "message" : "해당 계정이 존재하지 않습니다."}
    {"success" : False, "code" : "01", "message" : "해당 프로젝트가 존재하지 않습니다."}
    {"success" : False, "code" : "02", "message" : "음성 제작 요청 필요"}
    {"success" : False, "code" : "03", "message" : "음성 제작중"}

    Success
    {"success" : True, "message" : "음성 제작 완료", "data" : filelist}
"""

@app.get("/voice/get/{project_key}", tags = ['Voices'], description = description)
def get_voices(project_key : str, bearer : JWTBearer = Depends(JWTBearer()), db : Session = Depends(get_db)):
    user = db.query(User).filter(User.user_id == decodeJWT(bearer)['user_id']).first()
    if user == None:
        raise HTTPException(status_code = 200, detail={"success" : False, "code" : "00", "message" : "해당 계정이 존재하지 않습니다."})
    project = db.query(Project).filter(Project.project_key == project_key).first()
    if project == None:
        raise HTTPException(status_code=200, detail={"success" : False, "code" : "01", "message" : "해당 프로젝트가 존재하지 않습니다."})
    voices_dir = os.getcwd().replace("\\", "/") + "/projects/" + user.key + "/" + project_key +"/sources/voices"
    if not os.path.exists(voices_dir):
        raise HTTPException(status_code=200, detail={"success" : False, "code" : "02", "message" : "음성 제작 요청 필요"})
    
    log_path = voices_dir + "/seq.txt"
    log_file = open(log_path, "r")
    length = log_file.read()
    log_file.close()
    filelist = os.listdir(voices_dir)
    voice_files = []
    for file in filelist:
        if "voice" in file:
            voice_files.append(file)

    if len(voice_files) != int(length):
        raise HTTPException(status_code=200, detail={"success" : False, "code" : "03", "message" : "음성 제작 중"})
    else:
        tmp = []
        filelist = []
        voice_objs = project.voices.split("|")
        for voice in voice_objs:
            voice_dict = json.loads(voice)
            if voice_dict['id'] > 9:
                filename = project_key + "_voice_"+  str(voice_dict['id'])+".mp3"
            else:
                filename = project_key + "_voice_0"+  str(voice_dict['id'])+".mp3"
            audio = MP3(os.getcwd().replace("\\", "/") +"/projects/" + user.key + "/" + project_key +"/sources/voices/" + filename)
            url= "/voice/{}/{}".format(project_key, filename)
            voice_dict['url'] = url
            voice_dict['duration'] = audio.info.length * 1000
            
            filelist.append(voice_dict)
            tmp.append(json.dumps(dict(voice_dict)))
        project.voices = "|".join(tmp)
        db.commit()
        raise HTTPException(status_code=200, detail={"success" : True, "message" : "음성 제작 완료", "data" : filelist})

@app.get("/voice/{project_key}/{filename}", tags = ['Voices'])
def voice_file(project_key : str, filename : str, db : Session = Depends(get_db)):
    project = db.query(Project).filter(Project.project_key == project_key).first()
    user_key = project.user_key
    file_path = os.getcwd().replace("\\", "/") + "/projects/" + user_key + "/" + project_key +"/sources/voices/" + filename
    
    return FileResponse(path=file_path, filename=filename)

description = """
    탬플릿 이미지 가져오기
    탬플릿 크기 : 1920 X 1080(FHD)
    형식 : IMAGE
    
    이미지 URL LIST
    http://218.52.115.188:7000/TempImage/default_tmp.png
"""

@app.get("/TempImage/{filename}", tags=["Image"], description=description)
def get_Template_Image(filename :  str):
    filepath = os.getcwd().replace("\\", "/") + "/sources/images/background/" + filename
    return FileResponse(filename=filename, path=filepath)

description = """
    커버 이미지 가져오기
    크기 : 230 X 307
    형식 : IMAGE
    
    이미지 URL 예시
    http://218.52.115.188:7000/CoverImage/wjmh.PNG
"""
@app.get("/CoverImage/{filename}", tags=["Image"], description=description)
def get_Cover_Image(filename : str):
    filepath = os.getcwd().replace("\\", "/") + "/sources/images/cover/" + filename
    
    return FileResponse(filename=filename, path=filepath)

description = """
    로고이미지 불러오기
    형식 : IMAGE

    로고이미지는 아래 6가지 이미지가 전부 
    http://218.52.115.188:7000/LogoImage/ESCI_logo_t.png/
    http://218.52.115.188:7000/LogoImage/kci.png/
    http://218.52.115.188:7000/LogoImage/Medline.png/
    http://218.52.115.188:7000/LogoImage/PMC.png/
    http://218.52.115.188:7000/LogoImage/SCIE.png/
    http://218.52.115.188:7000/LogoImage/Scopus.png/
"""

@app.get("/LogoImage/{filename}", tags=["Image"], description=description)
def get_Logo_Image(filename : str):
    
    filepath = os.getcwd().replace("\\", "/")+ "/sources/images/logo/" + filename
    
    return FileResponse(filename=filename, path=filepath)

description = """
    /source/image/{project_key}/{filename}
    로걸 저장소에 저장된 파일을 불러옵니다.

    input:
    project_key : str
    filename : list

    output :
    File Response

"""
@app.get("/source/image/{project_key}/{filename}",tags = ['Image'], description = description)
def get_source_img(project_key : str, filename : str, db : Session = Depends(get_db)):
    project = db.query(Project).filter(Project.project_key == project_key).first()
    project_dict = project.__dict__
    filepath = os.getcwd().replace("\\", "/") + "/projects/" + project_dict['user_key'] + "/" + project_key + "/sources/images/" + filename
    return FileResponse(filepath)

description = """
    /source/image/{project_key}
    로걸 저장소에 저장된 파일리스트를 불러옵니다.

    input:
    project_key : str
    Authorization Header
    
    

    output :
    {"success" : False, "code" : "00", "message" : "해당 프로젝트가 존재하지 않습니다."}
    {"success" : False, "code" : "01", "message" : "이미지가 비어있습니다."}
    {"success" : True, "message" : "이미지 리스트 불러오기 성공" , "data" : []}
"""
@app.get("/source/image/{project_key}", tags = ["Image"], description=description)
def get_source_img_list(project_key : str, bearer : JWTBearer = Depends(JWTBearer()), db : Session = Depends(get_db)):
    user = db.query(User).filter(User.user_id == decodeJWT(bearer)['user_id']).first()
    project = db.query(Project).filter(Project.project_key == project_key).first()
    
    if project == None:
        raise HTTPException(status_code=200, detail={"success" : False, "code" : "00", "message" : "해당 프로젝트가 존재하지 않습니다."})
    else:
        pass
        
    img_dir = os.getcwd().replace("\\", "/") + "/" +"projects/" + user.key + "/" + project_key + "/sources/images"
    img_list = os.listdir(img_dir)
    if img_list == []:
        raise HTTPException(status_code=200, detail={"success" : False, "code" : "01", "message" : "이미지가 비어있습니다."})
    
    tmp = []
    for img in img_list:
        tmp.append("http://218.52.115.188:7000" + "/source/image/" + project_key + "/" + img)
        
    raise HTTPException(status_code=200, detail={"success" : True, "message" : "이미지 리스트 불러오기 성공" , "data" : tmp})
