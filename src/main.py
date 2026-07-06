from fastapi import FastAPI, Request, HTTPException
from fastapi.templating import Jinja2Templates
from pydantic import BaseModel
import src.graph_algorithms
import src.cactus
from fastapi.staticfiles import StaticFiles

app = FastAPI()
app.mount("/static", StaticFiles(directory="src/static"), name="static")
templates = Jinja2Templates(directory="src/templates")

class k_algorithm(BaseModel):
    data: list[list[int]] 
    k: int

class edge_list(BaseModel):
    data: list[list[int]] 

class include_exclude_list(BaseModel):
    data: list
    includeEdges: list[tuple[int, int]] = []
    excludeEdges: list[tuple[int, int]] = []

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
def algorithm_kstc(request: edge_list):
    '''
    returns 
    '''
    return src.graph_algorithms.algorithm_stc(request.data)

@app.post("/algorithm-cactus")
def algorithm_cactus(request: edge_list):
    '''
    returns 
    '''
    return src.cactus.create_cactus(request.data)


@app.post("/algorithm-allstc")
def algorithm_allstc(request: include_exclude_list):
    '''
    returns list of all spanning trees of min congestion with exclude and include, or
    -1: no graph matching the target congestion found
    -2: no spanning tree matches the include/exclude constraints
    '''
    return src.graph_algorithms.getMinSTCIncludeExlcude(
        request.data,
        request.includeEdges,
        request.excludeEdges
    )
    
    


