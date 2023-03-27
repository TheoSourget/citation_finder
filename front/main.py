import streamlit as st
import pandas as pd
import numpy as np
import requests
import time
st.title('Citation finder')
st.write('Citation finder is a tool to gather the list of paper citing another one using multiple sources such as OpenAlex and OpenCitation')

st.markdown('---')
st.header("Find the citations")
st.text_input(label="DOI :")

source = st.selectbox("Source to use :",["OpenAlex","OpenCitation POCI","OpenCitation COCI"])

if st.button("Search"):
    st.header("Search Results")
    with st.spinner('Research in progress... it can take some time'):
        df = pd.DataFrame(columns=["Title","DOI","Publication year","abstract"])
        st.dataframe(df)
    st.success('Done!')


 