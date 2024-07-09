from pydantic import BaseModel


class FolderBase(BaseModel):
    foldername: str
    description: str | None = None


class FolderCreate(FolderBase):
    pass


class Folder(FolderBase):
    id: int
    owner_id: int

    class Config:
        orm_mode = True


class UserBase(BaseModel):
    email: str


class UserCreate(UserBase):
    password: str


class User(UserBase):
    id: int
    is_active: bool
    password: str
    folders: list['Folder'] = []
    files: list['File'] = []

    class Config:
        orm_mode = True


class FileBase(BaseModel):
    filename: str


class FileCreate(FileBase):
    pass


class File(FileBase):
    id: int
    owner_id: int

    class Config:
        orm_mode = True

