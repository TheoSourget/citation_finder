import uvicorn
from fastapi import FastAPI,HTTPException,Body
from fastapi.encoders import jsonable_encoder
from fastapi.responses import JSONResponse
import requests
from doi2bib.crossref import get_json
import numpy as  np
import time

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
    print(pid)
    if not pid:
        raise HTTPException(status_code=500, detail="Error 500: DOI couldn't be convert to pubmed id. Please verify input")

    url = f"https://opencitations.net/index/poci/api/v1/citations/{pid}"
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



@app.get("/search_keywords/")
def search_keywords(params: dict = Body(...)):
    concepts = params["concepts"]
    year = params["year"]
    keywords = params["keywords"]
    timeout = params["timeout"]
    query_url = "https://api.openalex.org/works"
    filter_str = ""
    for c in concepts:
        filter_str += f"concepts.id:{c},"
    filter_str += f"publication_year:{year},has_abstract:true"
    next_page = True

    page_number = 1
    ret = {}
    id_paper = 1

    time_begin = time.time()
    while next_page:
        query_param = {
            'page':page_number,
            'filter':filter_str
        }
        r = requests.get(query_url,params=query_param)
        if r.status_code == 200:
            r_json = r.json()
            #If "results" field is empty we have reached the end for the current year
            if not r_json["results"]:
                next_page = False
            else:
                # For each paper in the current page
                for paper in r_json["results"]:
                    # Maximum size of the abstract, if the paper abstarct is longer it will be truncated
                    abstract = np.full(2500,"",dtype=object)
                    # The "abstract_inverted_index" field is a dictionnary with word as key and locations of this word in the abstract
                    # So we fill the abstarct variable above at the index of the word to reconstruct the abstract
                    for w in paper["abstract_inverted_index"]:
                        for indices in paper["abstract_inverted_index"][w]:
                            if indices < 2500:
                                abstract[indices] = ''.join(filter(str.isalnum, w)).lower()
                    # Remove empty location mostly due to a shorter abstract 
                    abstract = abstract[abstract != ""]
                    #Convert array to string
                    str_abstract = ' '.join(abstract)

                    #Get title and remove "," and "\n" that will create problem in the result csv 
                    title = paper["title"]
                    if title:
                        title = title.replace(",","")
                        title = title.replace("\n","")

                    # Search for keyword in the abstract
                    if keywords:
                        for k in keywords:
                            if k.lower() in str_abstract:
                                ret[id_paper] = {}
                                ret[id_paper]["Title"] = title
                                ret[id_paper]["DOI"] = paper["doi"]
                                ret[id_paper]["Year"] = paper["publication_year"]
                                ret[id_paper]["Abstract"] = str_abstract
                                id_paper += 1
                                break
                    else:
                        ret[id_paper] = {}
                        ret[id_paper]["Title"] = title
                        ret[id_paper]["DOI"] = paper["doi"]
                        ret[id_paper]["Year"] = paper["publication_year"]
                        ret[id_paper]["Abstract"] = str_abstract
                        id_paper += 1

                    if time.time() - time_begin > timeout:
                        next_page = False
                        break
                page_number += 1
        else:
            next_page=False

    json_response = jsonable_encoder(ret)
    return json_response