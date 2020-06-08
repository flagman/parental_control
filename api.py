from db import DB, keys
from fastapi import FastAPI, Response, Request, HTTPException
from pydantic import BaseModel
from typing import List
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://192.168.31.122", "http://localhost:8080"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

db = DB('db.sql', 'defaults.yml')

ok_reponse = {"code": 0}


class Status(BaseModel):
    allowed_time_daily: int
    daily_time_spent: float
    parent_control: bool
    internet_on: bool
    mac_addresses: List[str]


def check_auth(request):
    if 'auth' not in request.cookies or request.cookies['auth'] not in ['parent', 'child']:
        raise HTTPException(status_code=401)

    return request.cookies['auth']


@app.post("/login")
async def login(password: str, response: Response):
    if password == db[keys.child_password]:
        response.set_cookie(key='auth', value='child',
                            max_age=999999, expires=999999)
        return {'code': 0}
    if password == db[keys.parent_password]:
        response.set_cookie(key='auth', value='parent',
                            max_age=999999, expires=999999)
        return {'code': 0}
    return {'code': 401}


@app.post("/logout")
async def logout(response: Response):
    response.delete_cookie(key='auth')
    return {'code': 0}


@app.get("/status", response_model=Status)
async def status(request: Request):
    check_auth(request)
    return Status(
        allowed_time_daily=db[keys.allowed_time_daily],
        daily_time_spent=db[keys.daily_time_spent],
        parent_control=db[keys.is_parental_control],
        internet_on=db[keys.is_internet_on],
        mac_addresses=db[keys.mac_addresses]
    )


@app.put("/internet")
async def internet(state: bool, request: Request):
    check_auth(request)
    is_quota_drained = db[keys.daily_time_spent] >= db[keys.allowed_time_daily] * 60
    if state and is_quota_drained:
        return ok_reponse
    db[keys.is_internet_on] = state
    return ok_reponse


@app.put("/parental_control")
async def parental_control(state: bool, request: Request):
    role = check_auth(request)
    if role != 'parent':
        raise HTTPException(status_code=401)
    db[keys.is_parental_control] = state
    return ok_reponse


@app.put("/daily_time")
async def daily_time(minutes: int, request: Request):
    role = check_auth(request)
    if role != 'parent':
        raise HTTPException(status_code=401)
    db[keys.allowed_time_daily] = minutes
    return ok_reponse
