import os
from fastapi import FastAPI
from pydantic import BaseModel, EmailStr, Field #, SecretStr
from pydantic_extra_types.phone_numbers import PhoneNumber
from sqlalchemy import create_engine, insert, text
from tabels import users_table, company_table 
import os
from dotenv import load_dotenv


description = """
"""
tags_metadata = [
    {
        "name": "version control"
    },
    {
        "name": "users",
        "description": "perations with users. The **login** logic is also here.",
    },
{
        "name": "Companies",
        "description": "all company side works will show up here.",
    },

]

backend_version = "0.0.1"
app = FastAPI(
    title="Test",
    description=description,
    version="0.0.1",
    openapi_tags=tags_metadata
)


load_dotenv()

# DB connection
db_usr_name = os.getenv("DB_USR_NAME")
db_usr_password = os.getenv("DB_USR_PASSWORD")
db_name = os.getenv("DB_NAME")
port = os.getenv("PORT")
host = os.getenv("HOST")


# making connection to MySQL database
def connect_to_db(db_usr_name: str, db_usr_password: str, db_name: str, host: str):
    eng = create_engine(f"""mysql+pymysql://{db_usr_name}:{db_usr_password}@{host}/{db_name}""", echo= True)
    print("Engine created successfully!")
    return eng


# SQL query
def SQL(query_str, commit=False):
    global conn
    conn = engine.connect()
    conn.execute(query_str)
    if commit is True:
        conn.commit()
        print(">>> query got committed")

    return conn.execute(query_str)


# Make sure to use MySQL database
engine = connect_to_db(db_usr_name, db_usr_password, db_name, host)

result = SQL(text('SELECT "Making connection..."'))
print(result)
print(">>>Connected to MySQL server.")



class UserIn(BaseModel):
    name: str = Field(min_length=2, max_length=32)
    l_name: str = Field(min_length=2, max_length=54)
    password: str = Field(min_length=8)  # pass should be in format SecretStr
    email: EmailStr


class UserOut(BaseModel):
    name: str
    l_name: str
    email: EmailStr


class UserInDB(BaseModel):
    name: str
    l_name: str
    password: str
    email: EmailStr



def fake_password_hasher(raw_password: str):
    return "supersecret" + raw_password


def save_user(user_in: UserIn):
    hashed_password = fake_password_hasher(user_in.password)
    # By using ** python will pass dictionary as key-value element
    user_in_db = UserInDB(**user_in.model_dump(), hashed_password=hashed_password)
    statement = insert(users_table).values(user_in_db.model_dump())
    SQL(statement, True)
    print("user saved")

    return user_in_db



@app.post("/sign-up", tags=["users"], response_model=UserOut)
async def register(user_in: UserIn):

    user_saved = save_user(user_in)
    print(user_saved)
    return "user registered and details got saved in DB. All done!"

