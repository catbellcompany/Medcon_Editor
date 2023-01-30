from time import strftime
from typing import List
from pydantic import BaseModel
from pydantic import Required
from fastapi import Query
from enum import Enum
from pydantic.networks import EmailStr

class user_Register(BaseModel):
    user_id : str = Query(default = Required, title = "User ID", description= "유저 아이디")
    user_pw : str = Query(default = Required, title = "User PW", description= "유저 패스워드")
    user_name : str = Query(default = Required, title = "Nickname", description= "닉네임")
    email : str = Query(default = Required, title = "e-Mail", description= "이메일")
    projects : str= Query(default = [], title = "Projects", description= "프로젝트")
    socials : list
    
    class Config:
        schema_extra = {
            "example": {
                "user_id" : "tester2",
                "user_pw" : "tester2",
                "user_name" : "tester2",
                "email" : "0@gmail.com",
                "projects" : []
            }    
        }
class user_Login(BaseModel):
    user_id : str = Query(default = Required, title = "User ID",description= "유저 아이디")
    user_pw : str = Query(default = Required, title = "User Password", description= "유저 패스워드")

    class Config:
        schema_extra = {
            "example": {
                "user_id" : "tester2",
                "user_pw" : "tester2"
            }
        }
class Voice(BaseModel):
    txt : str = Query(default = Required, title = "텍스트", description= "생성할 음성")
    tld : str = Query(default = "com", title = "발음", description= "발음(Default : 미국식 영어)")
    lang : str = Query(default = "en", title = "언어", description= "언어(Default : 영어)")
    index : int = Query(default= 0, title = "음성 인덱스", description="파일위치를 특정하기 위한 인덱스")
    class Config:
        schema_extra = {
        "example": {
            "txt" : "sample", 
            "tld" : "com", 
            "lang" : "en",
            "index" : 0
        }    
    } 
    
class Metadata(BaseModel):
     journal_title : str 
     article_title : str 
     keywords : list 
     correspondence : str 
     copyright : str 
     doi : str
     authors : list
     abstract : list 
     images : list
     published : str
     
     class Config:
            schema_extra = {
            "example": {
                "journal_title" : "Journal Title", 
                "article_title" : "Article Title", 
                "keywords" : [], 
                "correspondence" : "Correspond to",
                "copyright" : "Copyright", 
                "doi" : "doi",
                "authors" : [],
                "abstract" : [], 
                "images" : [],
                "published" : "Published"
            }    
        } 
class new_Project(BaseModel):
    project_name : str
    #user_key : str
    doi : str
    author_image : str
    template_type : int
    
    class Config:
            schema_extra = {
            "example": {
                "project_name" : "Journal Title", 
                
                "doi" : "",
                "author_image" : "",
                "template_type" : 0
            }    
        } 
class layer_Json(BaseModel):
    id: str
    name: str
    angle: int
    stroke: None
    strokeWidth: int
    left: int
    top: float
    width: int
    height: float
    opacity: int
    originX: str
    originY: str
    scaleX: int
    scaleY: int
    type: str
    flipX: bool
    flipY: bool
    skewX: int
    skewY: int
    visible: bool
    shadow: None
    charSpacing: int
    fill: str
    fontFamily: str
    fontSize: int
    lineHeight: float
    text: str
    textAlign: str
    fontURL: str
    metadata : dict
    cropX: int
    cropY: int
    path: list
    fill: str
    
    
    
class scene_json(BaseModel):
    id: str = Query(title="Scen_ID", default=Required)
    name: str = Query(title="Scene_Name", default=Required) 
    duration: int =Query(title="duration", default=5000)
    layers : List[layer_Json]
    
class page_json(BaseModel):
    id : str = Query(title ="Page ID",default = Required)
    name : str =  Query(title ="Page Name", default = Required)
    type : str = Query(title = "type", default = "PRESENTATION") 
    frame : dict = Query(title ="frame", default= { "width": 1920, "height": 1080 })
    
    scenes : List[scene_json]
    metadata: dict = Query(title="metadata", default={}) 
    preview: str = Query(title = "preview", default="")
    


class save_Image(BaseModel):
    project_key : str
    
    img_list : list
    
    class Config:
        schema_extra = {
            "example": {
                "project_key" : "", 
                "img_list" : []
                
            }    
        } 

class Scene_Rscs(BaseModel):
    project_name : str
    user_key : str
    project_key : str
    article_title : str
    correspond : str
    authors : str
    doi : str
    template_type : int
    copyright : str
    keywords : str
    abstract : list
    author_img : str
    
    image_url_list : list

class play_Page(BaseModel):
    id : str
    duration : int = Query(default = None, title = "Audio", description= "Duration 정보")
    preview : str
    audio : str = Query(default = None, title = "Audio", description= "오디오 정보")
    
    class Config:
        schema_extra = {
            "example": {
                "id" : "", 
                "duration" : 0,
                "preview" : "",
                "audio" : ""
            }    
        } 
class project_Frame(BaseModel):
    width : int
    height : int
    
class play_Dict(BaseModel):
    project_key : str
    project_frame : project_Frame
    project_play : List[play_Page]

class Voice(BaseModel):
    id : int
    text : str
    
class voice_Request(BaseModel):
    project_key : str
    text_list : List[Voice]
    
class voice_Update(BaseModel):
    id : int
    text : str
    
class SnsType(str, Enum):
    facebook: str = "facebook"
    google: str = "google"

class UserRegister(BaseModel):
    # pip install 'pydantic[email]'
    user_id : str = None
    user_pw : str = None
    picture : str = None
    locale : str = None
    

class UserDelete(BaseModel):
    user_id : str

class UserUpdate(BaseModel):
    user_name : str
    picture : str
    locale : str 
    doi_list : list
    
    
class save_Info(BaseModel):
    #user_key : str 
    project_key : str
    thumbnail : str
    json_input : dict
    voices : List[voice_Update]