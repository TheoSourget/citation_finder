from fastapi import FastAPI,HTTPException
from fastapi.encoders import jsonable_encoder
from fastapi.responses import JSONResponse
import requests
from doi2bib.crossref import get_json

app = FastAPI()

def doi_to_OpenAlexId(doi):
    base_url = f"https://api.openalex.org/works/doi:{doi}"
    r = requests.get(base_url)
    if r.status_code == 200:
        r_json = r.json()
        return r_json["id"]
    else:
        return None

def doi_to_pubmedID(doi):
    base_url_pubmed = "https://www.ncbi.nlm.nih.gov/pmc/utils/idconv/v1.0/?tool=ddsa-theo&email=theo.sourget@univ-rouen.fr&format=json&ids="
    r = requests.get(base_url_pubmed + doi)
    pid = None
    if "error" not in str(r.content):
        r_json = r.json()
        pid = r_json["records"][0]["pmid"]
    return pid

def pubmedid_to_doi(pid):
    base_url_pubmed = "https://www.ncbi.nlm.nih.gov/pmc/utils/idconv/v1.0/?tool=ddsa-theo&email=theo.sourget@univ-rouen.fr&format=json&ids="
    r = requests.get(base_url_pubmed + pid)
    doi = None
    if "error" not in str(r.content):
        r_json = r.json()
        doi = r_json["records"][0]["doi"]
    return doi

@app.get("/get_citations/openalex/")
def request_OpenAlex(doi:str):

    openalex_id = doi_to_OpenAlexId(doi)
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


@app.get("/get_citations/coci/")
def request_coci(doi:str):

    doi = doi.replace("https://doi.org/","")
    url = f"https://opencitations.net/index/coci/api/v1/citations/{doi}"
    ret = {}
    paper_id = 1    
    request = requests.get(url)
    if request.status_code == 200:
        req_json = request.json()
        for cite in req_json:
            doi = cite["citing"]
            
            #Try to get the title with the DOI
            try:
                title = get_json(doi)[1]["message"]["title"][0]
                title = title.replace(",","")
                title = title.replace("\n","")
            # If error with the library, set the title to None
            except ValueError: 
                title = None

            year = cite["creation"][:4]
                
            ret[paper_id] = {}
            ret[paper_id]["Title"]=title
            ret[paper_id]["DOI"]=doi
            ret[paper_id]["Year"]=year

            paper_id += 1

    else:
        raise HTTPException(status_code=request.status_code, detail="Error {request.status_code}: Please verify your input or try later")
    
    json_response = jsonable_encoder(ret)
    return JSONResponse(content=json_response)


@app.get("/get_citations/poci/")
def request_poci(doi:str):

    doi = doi.replace("https://doi.org/","")
    pid = doi_to_pubmedID(doi)
    if not pid:
        raise HTTPException(status_code=500, detail="Error 500: DOI couldn't be convert to pubmed id. Please verify input")

    url = f"https://opencitations.net/index/poci/api/v1/citations/{doi}"
    ret = {}
    paper_id = 1    
    request = requests.get(url)
    if request.status_code == 200:
        req_json = request.json()
        for cite in req_json:
            id_to_convert = cite["citing"][5:]
            doi = doi_to_pubmedID(id_to_convert)
                           
            #Try to get the title with the DOI
            try:
                title = get_json(doi)[1]["message"]["title"][0]
                title = title.replace(",","")
                title = title.replace("\n","")
            # If error with the library, set the title to None
            except ValueError: 
                title = None

            year = cite["creation"][:4]
                
            ret[paper_id] = {}
            ret[paper_id]["Title"]=title
            ret[paper_id]["DOI"]=doi
            ret[paper_id]["Year"]=year

            paper_id += 1

    else:
        raise HTTPException(status_code=request.status_code, detail=f"Error {request.status_code}: Please verify your input or try later")
    
    json_response = jsonable_encoder(ret)
    return JSONResponse(content=json_response)