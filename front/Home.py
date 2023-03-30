import streamlit as st
import pandas as pd
import numpy as np
import requests
import time
import plotly.express as px
st.set_page_config(
    page_title="Citation Finder",
    page_icon="💬",
    layout="wide"
)
st.session_state.search_keywords = False
st.session_state.search = False

pd.options.plotting.backend = "plotly"

st.title('Welcome !')
st.write("This website helps you parse the huge amount of scientific paper to help find the information you need")
st.write("Please select the module you want to use in the sidebar, Find the description of each module below.")
st.markdown('---')
st.subheader("Citation Finder")
st.write("This module helps you to find the references to a given papers using open access API like OpenAlex and OpenCitations")
st.subheader("Keyword Finder")
st.write("This module helps you to gather a list of paper related to general concept such as 'Machine Learning' or 'Computer Science' and some keywords\
         using OpenAlex API")