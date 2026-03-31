from fastapi import FastAPI, Request, HTTPException
from fastapi.templating import Jinja2Templates
from pydantic import BaseModel
import src.graph_algorithms
from fastapi.staticfiles import StaticFiles

app = FastAPI()
app.mount("/static", StaticFiles(directory="src/static"), name="static")
templates = Jinja2Templates(directory="src/templates")

class k_algorithm(BaseModel):
    data: list[list[int]] 
    k: int

@app.get("/")
def root(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})

@app.post("/algorithm-kcut")
def algorithm_kcut(request: k_algorithm):
    '''
    Returns a list of each k-cut
    '''
    return src.graph_algorithms.k_cut(request.data,request.k)

@app.post("/algorithm-kcomponents")
def algorithm_kcomponents(request: k_algorithm):
    '''
    returns a list of k-edge connected conpomentnss
    '''
    return src.graph_algorithms.k_edge_connected_components(request.data, request.k)

@app.post("/algorithm-stc")
def algorithm_kstc(request: k_algorithm):
    '''
    returns 
    '''
    


