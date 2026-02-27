from fastapi import FastAPI, Request, HTTPException
from fastapi.templating import Jinja2Templates
from pydantic import BaseModel
import src.graph_algorithms

app = FastAPI()
templates = Jinja2Templates(directory="src\\templates")

class algorithm_kcut_req(BaseModel):
    data: list[list[int]] 
    k: int

@app.get("/")
def root(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})

@app.post("/algorithm-kcut")
def algorithm_kcut(request: algorithm_kcut_req):
    '''
    Returns a list of each k-cut
    '''
    return src.graph_algorithms.k_cut(request.data,request.k)

    


