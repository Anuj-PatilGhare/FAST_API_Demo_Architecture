from fastapi import FastAPI, HTTPException, Depends
from sqlalchemy import create_engine, Column, Integer, String
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, Session
from pydantic import BaseModel

# App :
app = FastAPI(title="This is the Fast API")

# Database URL Connection :
DATABASE_URL = "postgresql://postgres:112233@localhost:5432/Test_Josh"

engine = create_engine(DATABASE_URL, echo=True)
SessionLocal = sessionmaker(bind=engine, autoflush=False, autocommit=False)
Base = declarative_base()


# DB Model :
class User(Base):
    __tablename__ = "users"

    user_id = Column(Integer, primary_key=True, index=True)
    user_name = Column(String(100), nullable=False)
    user_email = Column(String(100), nullable=False, unique=True)
    user_role = Column(String(100), nullable=False)

Base.metadata.create_all(bind=engine)


# Pydantic Models 
class UserCreate(BaseModel):
    name: str
    email: str
    role: str

class UserResponse(BaseModel):
    user_id: int
    user_name: str
    user_email: str
    user_role: str

    class Config:
        from_attributes = True

# Database Dependency
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# Routes : -----------------------------------------------


#Test Route:
@app.get("/")
def root():
    return {"msg": "FastAPI running successfully "}


#Get All Users :
@app.get("/users")
def get_all_users(db:Session = Depends(get_db)):
    all_users = db.query(User).all()
    return all_users


# Get specific user with Id : 
@app.get("/users/{user_id}", response_model=UserResponse)
def get_user(user_id: int, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.user_id == user_id).first()

    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    return user


# Create user with Post :
@app.post("/users/", response_model=UserResponse)
def create_user(user: UserCreate, db: Session = Depends(get_db)):
    existing_user = db.query(User).filter(User.user_email == user.email).first()
    if existing_user:
        raise HTTPException(status_code=409, detail="User already exists")

    new_user = User(
        user_name=user.name,
        user_email=user.email,
        user_role=user.role
    )

    db.add(new_user)
    db.commit()
    db.refresh(new_user)

    return new_user


# Update user with POST :
@app.put("/user/{user_id}", response_model=UserResponse)
def update_user( user_id: int,  user: UserCreate,db: Session = Depends(get_db)):
    
    current_user = db.query(User).filter(User.user_id == user_id).first()

    if not current_user:
        raise HTTPException( status_code=404, detail="User does not exist..!")

    for field, value in user.dict(exclude_unset=True).items():
        if   field == "name":
            current_user.user_name = value
        elif field == "email":
            current_user.user_email = value
        elif field == "role":
            current_user.user_email = value

    db.commit()
    db.refresh(current_user)

    return current_user


# Delete User :
app.delete("/users/{user_id}")
def delete_user(user_id:int, db:Session = Depends(get_db)):
    
    current_user = db.query(User).filter(User.id == user_id).first()
    
    if not current_user:
        raise HTTPException(status_code=404,detail="User does not Found..!!")
    
    db.delete(current_user)
    db.commit()
    db.refresh(current_user)
    return current_user
