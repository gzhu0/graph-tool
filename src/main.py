from fastapi import FastAPI, Request, HTTPException
from fastapi.templating import Jinja2Templates
from pydantic import BaseModel

app = FastAPI()
templates = Jinja2Templates(directory="src\\templates")

@app.get("/")
def root(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})

@app.post("/algorithm-kcut")
def algorithm_kcut(data: list[list], k: int):
    '''
    Returns a list of each k
    '''
    print('asdf')


