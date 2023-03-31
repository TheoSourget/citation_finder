# citation_finder
Query free API to find paper citing another paper

## Main Tools Used
* Front: [Streamlit](https://streamlit.io/) 
* Dataviz: [Plotly](https://plotly.com/python/)
* Back: [FastAPI](https://fastapi.tiangolo.com/)
* References: [OpenAlex](https://openalex.org/),[OpenCitation](opencitations.net/)
## Installation

### Prerequisite:
You'll we need to have docker: 
[See how to install docker here](https://docs.docker.com/get-docker/)

You'll also need docker-compose:
```console
sudo apt install docker-compose
```

### Install and lauch the website:
1. clone the project 
```console
git clone https://github.com/TheoSourget/citation_finder.git
```
2. launch with docker
```console
cd citation_finder
docker-compose up -d --build
```
3. To stop the website
```console
docker-compose down
```
---

## How to use it ?
You have access to the website at: http://localhost:8501/

Then you can fill the DOI of the paper and choose the source from which we will search for citation of this paper.

![](./resources/input_options.png)


Once the information are set click on the search button to compute the citation extraction, it can be long depending on the source and the number of citations. When the extraction is complete the list is displayed as shown below and you can download the result as a CSV file with the button below the list.

![](./resources/dataframe_result.png)

You can also see some informations about the citations below the list of citations.

![](./resources/statistics_display.png)
