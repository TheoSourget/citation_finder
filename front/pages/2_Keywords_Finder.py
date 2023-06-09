import streamlit as st
from streamlit_tags import st_tags
import pandas as pd
import numpy as np
import requests
import json 
import csv

st.set_page_config(
    page_title="Keyword Finder",
    page_icon="💬",
    layout="wide"
)
st.session_state.search = False
if "search_keywords" not in st.session_state:
        st.session_state.search_keywords = False
        
@st.cache_data(show_spinner=False)
def query_api(query_param):
    url = f"http://backend:8000/search_keywords/"
    json_param = json.dumps(query_param, indent = 4) 
    request = requests.get(url,data=json_param)
    df_year = pd.DataFrame.from_dict(request.json()).T

    return df_year

@st.cache_data(show_spinner=False)
def convert_df(df):
    return df.to_csv().encode("utf-8")


st.title('Keywords finder')
st.write("Keywords finder is a tool to ther a list of paper related to general concept such as 'Machine Learning' or 'Computer Science' and some keywords\
         using OpenAlex API")
st.markdown('---')
st.header("Search options")


concepts_dict = {}
csv_reader = csv.DictReader(open('./res/concepts.csv'))
for l in csv_reader:
    concepts_dict[l["concept_name"]] = l["concept_id"]

col1, col2, col3 = st.columns(3)
with col1:
    concepts_id = st.multiselect("Concepts",list(concepts_dict.keys()),help="Concept of papers you're searching for. If multiple are selected, paper will need to respect every concept")
with col2:
    time_period = st.slider("Time period",2000,2023,(2000,2023),help="Year of research")
with col3:
    timeout = st.number_input("Search time limit (in seconds)",format="%i",step=1,help="Time limit is for 1 year. Put 0 or negative value to disable time limit")

keywords = st_tags(label='Keywords',text='Type a keyword and press enter')
search = st.button("Search")
if (search) or ("search_keywords" in st.session_state and st.session_state.search_keywords):
    
    concepts = [concepts_dict[c_id] for c_id in concepts_id]
    if not st.session_state.search_keywords:
        st.session_state.search_keywords = True
    
    lst_df = []
    
    params = {
        "concepts":concepts,
        "keywords":keywords,
        "timeout":timeout
    }
    with st.spinner('Research in progress...'):
        for year in range(time_period[0],time_period[1]+1):
            params["year"] = year
            df_year = query_api(params)
            lst_df.append(df_year)
    df_merged = pd.concat(lst_df).reset_index(drop=True)
    if not df_merged.empty:
        df_merged["Year"] = df_merged['Year'].astype(str)
        df_merged = df_merged[['Title', 'DOI', 'Year', 'Abstract','Full Text']]

        st.dataframe(df_merged)
        
        csv = convert_df(df_merged)

        st.download_button(
            label="Download data as CSV",
            data=csv,
            file_name=f'search_keywords:{keywords}_concepts:{concepts}.csv',
            mime='text/csv',
        )
    else:
        st.error("No result found")