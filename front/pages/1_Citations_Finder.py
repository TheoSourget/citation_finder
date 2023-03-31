import streamlit as st
import pandas as pd
import numpy as np
import requests
import time
import plotly.express as px
from wordcloud import WordCloud

import nltk
nltk.download("stopwords")
from nltk.corpus import stopwords

st.set_page_config(
    page_title="Citations Finder",
    page_icon="💬",
    layout="wide"
)
st.session_state.search_keywords = False

pd.options.plotting.backend = "plotly"

@st.cache_data(show_spinner=False)
def convert_df(df):
    return df.to_csv().encode("utf-8")


@st.cache_data(show_spinner=False)
def query_openalex(doi):
    url = f"http://backend:8000/get_citations/openalex/?doi={doi}"
    request = requests.get(url)
    return request

@st.cache_data(show_spinner=False)
def query_coci(doi):
    url = f"http://backend:8000/get_citations/coci/?doi={doi}"
    request = requests.get(url)
    return request

@st.cache_data(show_spinner=False)
def query_poci(doi):
    url = f"http://backend:8000/get_citations/poci/?doi={doi}"
    request = requests.get(url)
    return request

st.title('Citations finder')
st.write('Citations finder is a tool to gather the list of paper citing another one using multiple sources such as OpenAlex and OpenCitation')
st.markdown('---')
st.header("Find the citations")
doi = st.text_input(label="DOI :")

source = st.selectbox("Source to use :",["OpenAlex","OpenCitation POCI","OpenCitation COCI"])

if (st.button("Search") and doi) or ("search" in st.session_state and st.session_state.search):
    if not st.session_state.search:
        st.session_state.search = True

    st.header("Search Results")
    with st.spinner('Research in progress... it can be very long if the paper is cited a lot'):
        if source == "OpenAlex":
            request = query_openalex(doi)
        elif source == "OpenCitation POCI":
            request = query_poci(doi) 
        elif source == "OpenCitation COCI":
            request = query_coci(doi) 


    if request.status_code == 200:
        r_json = request.json()
        df = pd.DataFrame.from_dict(r_json).T
        df["Year"] = df['Year'].astype(str)
        df_plot = df[['Title','DOI','Year']]
        csv = convert_df(df_plot)

        st.dataframe(df_plot,use_container_width=True)

        st.download_button(
            label="Download data as CSV",
            data=csv,
            file_name=f'citations_{doi}.csv',
            mime='text/csv',
        )

        st.header("Statistical informations")
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric(label="Total number of citation",value=len(df))
        with col2:
            st.metric(label="Year of first citation",value=min(df["Year"]))
        with col3:
            st.metric(label="Year of last citation",value=max(df["Year"]))

        st.subheader("Citations per year") 
        df_groupby = df.groupby(["Year"]).count()["DOI"]
        fig = px.line(df_groupby,markers=True)
        fig.update_traces(name="",mode="markers+lines", hovertemplate='Number of citation in %{x}: %{y}')
        fig.update_layout(hovermode=None)
        fig.update_layout(
            xaxis_title="Year", yaxis_title="Number of citations"
        )
        fig.update_xaxes(type='category')
        st.plotly_chart(fig,use_container_width=True)

        if source == "OpenAlex":
            st.subheader("Most present words in the abstracts")
            text = ' '.join(df["Abstract"])
            stop_words = list(stopwords.words("english"))

            #Plot
            wordcloud = WordCloud(stopwords=stop_words,background_color="white",width=1500, height=400).generate(text)

            fig = px.imshow(wordcloud)
            fig.update_xaxes(visible=False)
            fig.update_yaxes(visible=False)
            fig.update_layout(showlegend=False)
            fig.update_traces(
                hovertemplate=None,
                hoverinfo="skip"
            )
            st.plotly_chart(fig,use_container_width=True)

    else:
        st.error(f"{request.json()['detail']}")


 