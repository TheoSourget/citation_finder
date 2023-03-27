import streamlit as st
import pandas as pd
import numpy as np
import requests
import time

@st.cache_data(show_spinner=False)
def convert_df(df):
    # IMPORTANT: Cache the conversion to prevent computation on every rerun
    return df.to_csv().encode("utf-8")


@st.cache_data(show_spinner=False)
def query_openalex(doi):
    url = f"http://localhost:8000/get_citations/openalex/?doi={doi}"
    request = requests.get(url)
    return request

st.set_page_config(layout="wide")
st.markdown(""" <style>
#MainMenu {visibility: hidden;}
footer {visibility: hidden;}
</style> """, unsafe_allow_html=True)

st.title('Citation finder')
st.write('Citation finder is a tool to gather the list of paper citing another one using multiple sources such as OpenAlex and OpenCitation')

st.markdown('---')
st.header("Find the citations")
doi = st.text_input(label="DOI :")

source = st.selectbox("Source to use :",["OpenAlex","OpenCitation POCI","OpenCitation COCI"])


if st.button("Search") and doi:
    st.header("Search Results")
    with st.spinner('Research in progress... it can take some time'):
        if source == "OpenAlex":
            request = query_openalex(doi)
        elif source == "OpenCitation POCI":
            request = query_openalex(doi) 
        elif source == "OpenCitation COCI":
            request = query_openalex(doi) 


        if request.status_code == 200:
            r_json = request.json()
            st.success('Done!')
            df = pd.DataFrame.from_dict(r_json).T
            df["Year"] = pd.to_datetime(df.Year)
            
            csv = convert_df(df)

            st.dataframe(df,use_container_width=True)

            st.download_button(
                label="Download data as CSV",
                data=csv,
                file_name=f'citations_{doi}.csv',
                mime='text/csv',
            )
        else:
            st.error(f"{request.json()['detail']}")


 