from fastapi import FastAPI, HTTPException, Depends
from sqlmodel import Session, SQLModel, create_engine, select, Relationship, Field
from typing import List
from fastapi.middleware.cors import CORSMiddleware
import uvicorn

app = FastAPI()

origins = [
    "http://localhost:3000",
    "http://localhost:8080",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

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

def get_session():
    with Session(engine) as session:
        yield session

# Routes for User CRUD operations
@app.post("/users/", response_model=User)
def create_user(user: User, session: Session = Depends(get_session)):
    session.add(user)
    session.commit()
    session.refresh(user)
    return user

@app.get("/users/", response_model=List[User])
def read_users(session: Session = Depends(get_session)):
    users = session.exec(select(User)).all()
    return users

@app.get("/users/{user_id}", response_model=User)
def read_user(user_id: int, session: Session = Depends(get_session)):
    user = session.get(User, user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return user

@app.put("/users/{user_id}", response_model=User)
def update_user(user_id: int, user: User, session: Session = Depends(get_session)):
    db_user = session.get(User, user_id)
    if not db_user:
        raise HTTPException(status_code=404, detail="User not found")
    db_user.name = user.name
    db_user.email = user.email
    session.add(db_user)
    session.commit()
    session.refresh(db_user)
    return db_user

@app.delete("/users/{user_id}", response_model=User)
def delete_user(user_id: int, session: Session = Depends(get_session)):
    db_user = session.get(User, user_id)
    if not db_user:
        raise HTTPException(status_code=404, detail="User not found")
    session.delete(db_user)
    session.commit()
    return db_user

# Routes for Todo CRUD operations
@app.post("/users/{user_id}/todos/", response_model=Todo)
def create_todo_for_user(user_id: int, todo: Todo, session: Session = Depends(get_session)):
    db_user = session.get(User, user_id)
    if not db_user:
        raise HTTPException(status_code=404, detail="User not found")
    todo.owner_id = user_id
    session.add(todo)
    session.commit()
    session.refresh(todo)
    return todo

@app.get("/users/{user_id}/todos/", response_model=List[Todo])
def read_todos_for_user(user_id: int, session: Session = Depends(get_session)):
    db_user = session.get(User, user_id)
    if not db_user:
        raise HTTPException(status_code=404, detail="User not found")
    todos = session.exec(select(Todo).filter_by(owner_id=user_id)).all()
    return todos

@app.get("/todos/", response_model=List[Todo])
def read_all_todos(session: Session = Depends(get_session)):
    todos = session.exec(select(Todo)).all()
    return todos

@app.get("/todos/{todo_id}", response_model=Todo)
def read_todo(todo_id: int, session: Session = Depends(get_session)):
    todo = session.get(Todo, todo_id)
    if not todo:
        raise HTTPException(status_code=404, detail="Todo not found")
    return todo

@app.put("/todos/{todo_id}", response_model=Todo)
def update_todo(todo_id: int, todo: Todo, session: Session = Depends(get_session)):
    db_todo = session.get(Todo, todo_id)
    if not db_todo:
        raise HTTPException(status_code=404, detail="Todo not found")
    db_todo.title = todo.title
    db_todo.description = todo.description
    session.add(db_todo)
    session.commit()
    session.refresh(db_todo)
    return db_todo

@app.delete("/todos/{todo_id}", response_model=Todo)
def delete_todo(todo_id: int, session: Session = Depends(get_session)):
    db_todo = session.get(Todo, todo_id)
    if not db_todo:
        raise HTTPException(status_code=404, detail="Todo not found")
    session.delete(db_todo)
    session.commit()
    return db_todo

def start():
  uvicorn.run("todos_app.main:app", host="127.0.0.1", port=8000, reload=True)
