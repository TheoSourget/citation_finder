import streamlit as st
from streamlit_tags import st_tags
import pandas as pd
import numpy as np
import requests

st.set_page_config(
    page_title="Keyword Finder",
    page_icon="💬",
    layout="wide"
)

@st.cache_data(show_spinner=False)
def query_api(query_param):
    df_year = pd.DataFrame()
    return df_year


st.title('Keywords finder')
st.write("Keywords finder is a tool to ther a list of paper related to general concept such as 'Machine Learning' or 'Computer Science' and some keywords\
         using OpenAlex API")
st.markdown('---')
st.header("Search options")

col1, col2, col3 = st.columns(3)
with col1:
    concepts = st.multiselect("Concepts",["Ouais","Nope"])
with col2:
    time_period = st.slider("Time period",2000,2023,(2000,2023))
with col3:
    time_limit = st.number_input("Search time limit (in seconds)",format="%i",step=1)

keywords = st_tags(label='keywords',text='Type and press enter')
search = st.button("Search")
if search:
    lst_df = []
    
    params = {
        "concepts":concepts,
        "keywords":keywords
    }

    for year in range(time_period[0],time_period[1]+1):
        params["year"] = year
        df_year = query_api(params)
        lst_df.append(df_year)

    df_merged = pd.concat(lst_df)
    st.dataframe(df_merged)