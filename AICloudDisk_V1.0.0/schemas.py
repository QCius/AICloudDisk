from pydantic import BaseModel


class ItemBase(BaseModel):
    title: str
    description: str | None = None


class ItemCreate(ItemBase):
    pass


class Item(ItemBase):
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
    items: list[Item] = []
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


User.update_forward_refs()