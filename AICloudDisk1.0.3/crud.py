from sqlalchemy.orm import Session

from . import models, schemas

# 对用户的增删改查

def get_user(db: Session, user_id: int):
    return db.query(models.User).filter(models.User.id == user_id).first()


def get_user_by_email(db: Session, email: str):
    return db.query(models.User).filter(models.User.email == email).first()


def get_users(db: Session, skip: int = 0, limit: int = 100):
    return db.query(models.User).offset(skip).limit(limit).all()


def create_user(db: Session, user: schemas.UserCreate):
    db_user = models.User(email=user.email, password=user.password)
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user

def modify_user(db: Session, user: schemas.User):
    db_user = db.query(models.User).filter(models.User.id == user.id).first()
    db_user.email = user.email
    db_user.password = user.password
    db_user.is_active = user.is_active
    db_user.items = user.items
    db.commit()
    db.refresh(db_user)
    return db_user



def get_folders(db: Session, skip: int = 0, limit: int = 100):
    return db.query(models.Folder).offset(skip).limit(limit).all()


def create_user_folder(db: Session, folder: schemas.FolderCreate, user_id: int):
    db_folder = models.Folder(**folder.dict(), owner_id=user_id)
    db.add(db_folder)
    db.commit()
    db.refresh(db_folder)
    return db_folder

# 对网盘文件的操作

def create_file(db: Session, file: schemas.FileCreate, content: bytes, user_id: int):
    db_file = models.File(**file.dict(), content=content, owner_id=user_id)
    db.add(db_file)
    db.commit()
    db.refresh(db_file)
    return db_file


def get_files(db: Session, user_id: int, skip: int = 0, limit: int = 100):
    return db.query(models.File).filter(models.File.owner_id == user_id).offset(skip).limit(limit).all()


def get_file(db: Session, user_id: int, file_id: int):
    return db.query(models.File).filter(models.File.id == file_id, models.File.owner_id == user_id).first()


def delete_file(db: Session, user_id: int, file_id: int):
    db_file = db.query(models.File).filter(models.File.id == file_id, models.File.owner_id == user_id).first()
    if db_file:
        db.delete(db_file)
        db.commit()
        return True
    return False