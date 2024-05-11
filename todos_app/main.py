from fastapi import FastAPI
from sqlmodel import Field, SQLModel, create_engine, Relationship, Session
import uvicorn

app = FastAPI()

class User(SQLModel, table=True):
  id: int = Field(default=None, primary_key=True)
  name: str
  email: str
  todos: list["Todo"] = Relationship(back_populates="owner")

class Todo(SQLModel, table=True):
  id: int = Field(primary_key=True)
  title: str
  description: str
  owner_id: int = Field(foreign_key="user.id")
  owner: User = Relationship(back_populates="todos")

connection_url = "postgresql://postgres.tklxexsdzslwwuosvhvh:91022630Mtayyab@aws-0-ap-south-1.pooler.supabase.com:5432/postgres"

engine = create_engine(connection_url)

SQLModel.metadata.create_all(engine)

@app.get('/getUsers')
def getUsers():
  with Session(connnection) as session:
    statement = select(Users)
    result = session.execute(statement)
    users = result.fetchall()
    return users

def start():
  uvicorn.run("todos_app.main:app", host="127.0.0.1", port=8000, reload=True)
