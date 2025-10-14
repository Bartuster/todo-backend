from pydantic import BaseModel

class TodoCreate(BaseModel):
    title: str

class TodoRead(BaseModel):
    id: int
    title: str
    completed: bool

    class Config:
        from_attributes = True  # dla Pydantic v2
