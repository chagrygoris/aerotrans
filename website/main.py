import logging
from fastapi import FastAPI, Request, Form, Depends
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from pydantic import BaseModel
from databaza import session, User, already_registered


logging.basicConfig(filename='logs', filemode='w')
logging.getLogger().setLevel(logging.INFO)


app = FastAPI()
templates = Jinja2Templates(directory="templates")
class UserRequest(BaseModel):
    name: str
    age: int

@app.get('/')
async def home(request: Request):
    return templates.TemplateResponse("home.html", {"request" : request})

@app.get("/sign_up", response_class=HTMLResponse)
async def sign_up(request: Request):
    return templates.TemplateResponse("form.html", {
        "request": request
    })

@app.post("/success/", response_class=HTMLResponse)
async def create_user(request: Request, name = Form(), email=Form()):
    user = User(name=name, email=email)
    if already_registered(name, email):
        return HTMLResponse(status_code=404, content="Bad Request")
    session.add(user)
    session.commit()
    logging.info(f"User {name} with email adress {email} has signed up")
    return templates.TemplateResponse("result.html", {
        "request": request
    })
