# citation_finder
Query free API to find paper citing another paper

## Principle Used Tools
* Front: [Streamlit](https://streamlit.io/) 
* Dataviz: [Plotly](https://plotly.com/python/)
* Back: [FastAPI](https://fastapi.tiangolo.com/)
* References: [OpenAlex](https://openalex.org/),[OpenCitation](opencitations.net/)
## Installation
1. clone the project 
```console
git clone https://github.com/TheoSourget/citation_finder.git
```
2. install requirements
```console
cd citation_finder
pip3 install -r requirements.txt
```

---

## Launch

### For the front:
```console
    cd front
    streamlit run main.py 
```

###
```console
    cd back
    uvicorn main:app --reload
```

You have access to the website at: http://localhost:8501/

## Usage

