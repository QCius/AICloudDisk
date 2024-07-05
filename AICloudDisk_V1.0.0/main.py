from fastapi import Depends, FastAPI, HTTPException, UploadFile, status, File
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from fastapi.responses import StreamingResponse
from io import BytesIO
from sqlalchemy.orm import Session
from typing import List
import base64

from . import crud, models, schemas
from .database import SessionLocal, engine

models.Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="网盘助手",
    description="This is a custom API for managing Cloud service.",
    version="1.0.0",
    
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


# 用户管理API

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


@app.post("/users/{user_id}/items/", response_model=schemas.Item, summary="为用户创建表项", tags=["用户管理"])
def create_item_for_user(
    user_id: int, item: schemas.ItemCreate, db: Session = Depends(get_db)
):
    return crud.create_user_item(db=db, item=item, user_id=user_id)


@app.get("/items/", response_model=list[schemas.Item], summary="读取表项", tags=["用户管理"])
def read_items(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    items = crud.get_items(db, skip=skip, limit=limit)
    return items


# 网盘管理API

@app.post("/uploadfile/", summary="上传文件", tags=["网盘管理"])
async def create_upload_file(file: UploadFile = File(...), current_user: models.User = Depends(get_current_active_user), db: Session = Depends(get_db)):
    content = await file.read()
    db_file = models.File(filename=file.filename, content=content, owner_id=current_user.id)
    db.add(db_file)
    db.commit()
    db.refresh(db_file)
    return {"filename": file.filename}



@app.get("/downloadfile/{file_id}", summary="下载文件", tags=["网盘管理"])
async def download_file(file_id: int, db: Session = Depends(get_db)):
    db_file = crud.get_file(db, file_id)
    if db_file is None:
        raise HTTPException(status_code=404, detail="File not found")
    
    file_like = BytesIO(db_file.content)
    return StreamingResponse(file_like, media_type="application/octet-stream", headers={"Content-Disposition": f"attachment;filename={db_file.filename}"})


@app.get("/uploadfile/list", response_model=List[schemas.File], summary="列出文件", tags=["网盘管理"])
async def list_files(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    files = crud.get_files(db, skip=skip, limit=limit)
    return files


@app.delete("/uploadfile/delete/{file_id}", summary="删除文件", tags=["网盘管理"])
async def delete_file(file_id: int, db: Session = Depends(get_db)):
    success = crud.delete_file(db, file_id)
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

# AI调用API

@app.get("/AI/conclude", summary="总结文件内容", tags=["AI助手"])
async def ai_conclude(file_id: int, db: Session = Depends(get_db)):
    db_file = crud.get_file(db, file_id)
    if db_file is None:
        raise HTTPException(status_code=404, detail="File not found")
    content = db_file.content
    # 假设我们有一个函数 summarize_content 实现 AI 总结功能
    summary = summarize_content(content)
    return {"summary": summary}

def summarize_content(content: bytes) -> str:
    # 简单示例，实际应用中需要更复杂的逻辑
    return "Summary of the content"