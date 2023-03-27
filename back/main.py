from fastapi import FastAPI,HTTPException
from fastapi.encoders import jsonable_encoder
from fastapi.responses import JSONResponse
import requests

app = FastAPI()



def doi_to_OpenAlexId(doi):
    base_url = f"https://api.openalex.org/works/doi:{doi}"
    r = requests.get(base_url)
    if r.status_code == 200:
        r_json = r.json()
        return r_json["id"]
    else:
        return None

@app.get("/get_citations/openalex/")
def request_OpenAlex(doi:str):

    openalex_id = doi_to_OpenAlexId(doi)
    print(openalex_id)
    if not openalex_id:
        raise HTTPException(status_code=500, detail="Error 500: DOI couldn't be convert to OpenAlexID. Please verify input")

    base_url = "https://api.openalex.org/works"
    ret = {}
    
    page_number = 1
    paper_id = 1
    next_page = True
    
    while  next_page:
        query_param = {
            "filter":f"cites:{openalex_id}",
            "page":page_number
        }
        request = requests.get(base_url,params=query_param)
        if request.status_code == 200:
            request_json = request.json()
            for res in request_json["results"]:
                title = res["title"]
                if title:
                    title = title.replace(",","")
                    title = title.replace("\n","")
                
                doi = res["doi"]
                
                year = res["publication_year"]
                
                ret[paper_id] = {}
                ret[paper_id]["Title"]=title
                ret[paper_id]["DOI"]=doi
                ret[paper_id]["Year"]=year

                paper_id += 1
            
            if not request_json["results"]:
                next_page = False
            else:
                page_number += 1
        else:
            raise HTTPException(status_code=request.status_code, detail="Error {request.status_code}: Please verify your input or try later")
    
    json_response = jsonable_encoder(ret)
    return JSONResponse(content=json_response)