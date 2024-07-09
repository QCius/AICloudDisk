from fastapi import Depends, FastAPI, HTTPException, UploadFile, status, File
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from fastapi.responses import StreamingResponse,FileResponse
from io import BytesIO
import wave
import tempfile
from sqlalchemy.orm import Session
from typing import List
from openai import OpenAI

from .AImodels import sparkAI
from . import crud, models, schemas
from .database import SessionLocal, engine

models.Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="网盘助手",
    description="This is a custom API for managing Cloud service.",
    version="1.0.2",
)

# Dependency
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

async def get_current_user(token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)):
    dbuser = crud.get_user_by_email(db, token)
    if not dbuser:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authentication credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )
    return dbuser


async def get_current_active_user(current_user: models.User = Depends(get_current_user)):
    if current_user==None:
        raise HTTPException(status_code=400, detail="Inactive user")
    return current_user

# 
# 用户管理API
# 

@app.post("/token", summary="登入", description="验证登录", tags=["用户管理"])
async def login(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    dbuser = crud.get_user_by_email(db, form_data.username)
    if not dbuser:
        raise HTTPException(status_code=400, detail="Incorrect username or password")
    fpwd=form_data.password
    if not fpwd == dbuser.password:
        raise HTTPException(status_code=400, detail="Incorrect username or password")

    return {"access_token": dbuser.email, "token_type": "bearer"}


@app.get("/users/me", summary="读取本人信息(需要已登录)", description="", tags=["用户管理"])
async def read_users_me(current_user: models.User = Depends(get_current_active_user)):
    return current_user

@app.post("/users/", response_model=schemas.User, summary="注册", tags=["用户管理"])
def create_user(user: schemas.UserCreate, db: Session = Depends(get_db)):
    db_user = crud.get_user_by_email(db, email=user.email)
    if db_user:
        raise HTTPException(status_code=400, detail="Email already registered")
    return crud.create_user(db=db, user=user)


@app.get("/users/", response_model=list[schemas.User], summary="读取用户列表", tags=["用户管理"])
def read_users(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    users = crud.get_users(db, skip=skip, limit=limit)
    return users

@app.put("/users/{id}", response_model=schemas.User, summary="修改用户", description="修改用户", tags=["用户管理"])
def update_users(id:int, newuser:schemas.User,skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    users = crud.modify_user(db, newuser)
    return users


@app.get("/users/{user_id}", response_model=schemas.User, summary="通过用户账户查询用户信息", tags=["用户管理"])
def read_user(user_id: int, db: Session = Depends(get_db)):
    db_user = crud.get_user(db, user_id=user_id)
    if db_user is None:
        raise HTTPException(status_code=404, detail="User not found")
    return db_user


@app.post("/users/{user_id}/folders/", response_model=schemas.Folder, summary="为用户创建文件夹", tags=["用户管理"])
def create_folder_for_user(
    user_id: int, folder: schemas.FolderCreate, db: Session = Depends(get_db)
):
    return crud.create_user_folder(db=db, folder=folder, user_id=user_id)


@app.get("/folders/", response_model=list[schemas.Folder], summary="读取表项", tags=["用户管理"])
def read_folders(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    folders = crud.get_folders(db, skip=skip, limit=limit)
    return folders

#
# 网盘管理API
# 

@app.post("/uploadfile/", summary="上传文件", tags=["网盘管理"])
async def create_upload_file(file: UploadFile = File(...), current_user: models.User = Depends(get_current_active_user), db: Session = Depends(get_db)):
    content = await file.read()
    db_file = models.File(filename=file.filename, content=content, owner_id=current_user.id)
    db.add(db_file)
    db.commit()
    db.refresh(db_file)
    return {"filename": file.filename}



@app.get("/downloadfile/{file_id}", summary="下载文件", tags=["网盘管理"])
async def download_file(file_id: int, current_user: models.User = Depends(get_current_active_user),db: Session = Depends(get_db)):
    db_file = crud.get_file(db,current_user.id,file_id)
    if db_file is None:
        raise HTTPException(status_code=404, detail="File not found")
    
    file_like = BytesIO(db_file.content)
    return StreamingResponse(file_like, media_type="application/octet-stream", headers={"Content-Disposition": f"attachment;filename={db_file.filename}"})


@app.get("/uploadfile/list", response_model=List[schemas.File], summary="列出文件", tags=["网盘管理"])
async def list_files(skip: int = 0, limit: int = 100, db: Session = Depends(get_db),current_user: models.User = Depends(get_current_active_user)):
    files = crud.get_files(db, skip=skip, limit=limit,user_id=current_user.id)
    return files


@app.delete("/uploadfile/delete/{file_id}", summary="删除文件", tags=["网盘管理"])
async def delete_file(file_id: int, db: Session = Depends(get_db),current_user: models.User = Depends(get_current_active_user)):
    success = crud.delete_file(db, current_user.id,file_id)
    if not success:
        raise HTTPException(status_code=404, detail="File not found")
    return {"message": "File deleted successfully"}


@app.post("/createfolder/", summary="创建文件夹", tags=["网盘管理"])
async def create_folder():
    # 实际应用中需要实现创建文件夹的逻辑
    return {"message": "Folder created successfully"}


@app.delete("/deletefolder/{folder_id}", summary="删除文件夹", tags=["网盘管理"])
async def delete_folder(folder_id: int):
    # 实际应用中需要实现删除文件夹的逻辑
    return {"message": "Folder deleted successfully"}

#
# AI API
# MoonShot AI(Kimi) 
# Spark AI(讯飞星火)
#

client = OpenAI(
    api_key = "sk-j6n00tElc97ogd5bn93YlpuFulTpyUOTtilKOGFxo4WhOM7C",
    base_url = "https://api.moonshot.cn/v1",
)
history = [
    {"role": "system", "content": "你是 网盘助手懒子哥,你更擅长中文和英文的对话。你会为用户提供安全,有帮助,准确的回答。Moonshot AI 为专有名词，不可翻译成其他语言。"}
]

# 多轮对话API调用
@app.get("/AI/chat/mul", summary="多轮对话", tags=["AI助手"])
async def ai_chat(query,model = "spark"):
    if model == "moonshot":
        history.append({
            "role": "user", 
            "content": query
        })
        completion = client.chat.completions.create(
            model="moonshot-v1-8k",
            messages=history,
            temperature=0.3,
        )
        result = completion.choices[0].message.content
        history.append({
            "role": "assistant",
            "content": result
        })
        return result
    
    elif model == "spark":
        spark = sparkAI.SparkAIModel()
        result = spark.spark_mul_chat(query)
        return result

    else:
        raise HTTPException(status_code=402, detail="No such model")


#  单轮对话API调用
@app.get("/AI/chat/single", summary="单轮对话", tags=["AI助手"])
async def ai_chat(query):
    request = [
        {"role": "system", "content": "你是 网盘助手懒子哥,你更擅长中文和英文的对话。你会为用户提供安全,有帮助,准确的回答。Moonshot AI 为专有名词，不可翻译成其他语言。"}
    ]
    request.append({
        "role": "user", 
        "content": query
    })
    completion = client.chat.completions.create(
        model="moonshot-v1-8k",
        messages=request,
        temperature=0.3,
    )
    result = completion.choices[0].message.content
    return result

# AI文件总结
@app.get("/AI/fileconclude", summary="总结文件内容", tags=["AI助手"])
async def ai_file_conclude(
    file_id: int,
    additional_message: str = None,
    current_user: models.User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    db_file = crud.get_file(db, current_user.id, file_id)
    if db_file is None:
        raise HTTPException(status_code=404, detail="File not found")
    
    # 创建文件对象
    file_object = client.files.create(file=(db_file.filename, BytesIO(db_file.content)), purpose="file-extract")
    
    # 获取提取的文件内容
    extracted_content = client.files.content(file_id=file_object.id).text
    
    messages = [
        {
            "role": "system",
            "content": "你是 网盘助手懒子哥,你更擅长中文和英文的对话。你会为用户提供安全,有帮助,准确的回答。Moonshot AI 为专有名词，不可翻译成其他语言。",
        },
        {
            "role": "system",
            "content": extracted_content,
        },
        {   
            "role": "user",
            "content": "请简单介绍上传的文件的内容"
        },
    ]
    
    if additional_message:
        messages.append({
            "role": "user",
            "content": additional_message,
        })
    
    # 然后调用 chat-completion, 获取 Kimi 的回答
    completion = client.chat.completions.create(
        model="moonshot-v1-32k",
        messages=messages,
        temperature=0.3,
    )
    
    result = completion.choices[0].message
    return result

#  AI语音API调用
@app.get("/AI/voice", summary="AI文字转语音", tags=["AI助手"])
async def ai_voice(text: str):
    spark = sparkAI.SparkAIModel()
    audio_data = spark.spark_AI_voice(text)

    # 创建临时文件来保存音频数据
    with tempfile.NamedTemporaryFile(delete=False, suffix=".wav") as temp_audio_file:
        # 写入PCM数据到临时文件
        with wave.open(temp_audio_file, 'wb') as wave_file:
            wave_file.setnchannels(1)  # 设置单声道
            wave_file.setsampwidth(2)  # 设置每个样本的字节数（16位）
            wave_file.setframerate(16000)  # 设置采样率
            wave_file.writeframes(audio_data)

        temp_audio_file_path = temp_audio_file.name

    # 返回生成的WAV文件
    return FileResponse(temp_audio_file_path, media_type='audio/wav', filename='output.wav')