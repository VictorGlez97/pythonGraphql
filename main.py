from fastapi import FastAPI
from strawberry.fastapi import GraphQLRouter
import strawberry
from typing import List
from sqlalchemy import Column, Integer, String, create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

DATABASE_URL = "sqlite:///C:/Users/vhgonzalez/test.db"
engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, index=True)
    email = Column(String, unique=True, index=True)

Base.metadata.create_all(bind=engine)

# Definir el esquema de Graphql
@strawberry.type
class UserType:
    id: int
    name: str
    email: str

@strawberry.type
class Query:
    @strawberry.field
    def users(self) -> List[UserType]:
        db = SessionLocal()
        users = db.query(User).all()
        result = [UserType(id=user.id, name=user.name, email=user.email) for user in users]
        db.close()
        return users
    
@strawberry.type
class Mutation:
    @strawberry.mutation
    def create_user(self, name: str, email: str) -> UserType:
        db = SessionLocal()
        user = User(name=name, email=email)
        db.add(user)
        db.commit()
        db.refresh(user)
        db.close()
        return user
    
    @strawberry.mutation
    def delete_user(self, id: int) -> bool:
        db = SessionLocal()
        user = db.query(User).filter(User.id == id).first()
        if user:
            db.delete(user)
            db.commit()
            db.close()
            return True
        db.close()
        return False
    
schema = strawberry.Schema(query=Query, mutation=Mutation)

app = FastAPI()

graphql_app = GraphQLRouter(schema)
app.include_router(graphql_app, prefix="/graphql")