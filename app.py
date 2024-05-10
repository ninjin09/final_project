import streamlit as st
import pandas as pd
import requests
import re
from bs4 import BeautifulSoup
import transformers
from transformers import pipeline
from pysummarization.nlpbase.auto_abstractor import AutoAbstractor
from pysummarization.tokenizabledoc.simple_tokenizer import SimpleTokenizer
from pysummarization.abstractabledoc.top_n_rank_abstractor import TopNRankAbstractor

site_options = ['Sports','Ikon articles','Chess']
full_ikon_urls = []
ikon_urls = []
sports_urls = []
chess_urls = []

df = pd.read_csv('nba-sample.csv')
###############################
st.title("Get the Latest News Based on Your Interests")

option = st.selectbox("What would you like to read about?", site_options)
if option == 'Ikon articles':
    ikon_option = st.selectbox("Choose a topic", ('All latest','Politics','Economy'))
elif option == 'Sports':
    sports_option = st.selectbox("Choose a topic", ('NBA','Soccer','MLB','NFL'))

################################
#IKON
################################
if st.button('Give me the latest news!'):
    if option == 'Ikon articles':
        if ikon_option == 'All latest':
            response = requests.get("https://ikon.mn/j/sd7qmo/sd7qmo")
        elif ikon_option == 'Politics':
            response = requests.get("https://ikon.mn/l/1")
        elif ikon_option == 'Economy':
            response = requests.get("https://ikon.mn/l/2")
        soup = BeautifulSoup(response.content)
        ikon_links = soup.find_all("div",{"class":"nlitem"})
        
        for link in ikon_links:
            if "Өчигдөр" not in link:
                ikon_a = link.find("a")
                ikon_url = ikon_a.get('href')
                ikon_urls.append(ikon_url)
        for url in ikon_urls:
            full_url = "https://ikon.mn" + url
            full_ikon_urls.append(full_url)
        
        article_titles = []
        article_bodies = []
        for url in full_ikon_urls:
            response = requests.get(url)
            soup = BeautifulSoup(response.content,features="html.parser")
            article_title = soup.find('h1').get_text(strip=True)
            article_paragraphs = soup.find_all('p')
            body = ""
            for paragraph in article_paragraphs:
                paragraph = paragraph.get_text(strip=True)
                body = body + paragraph
            article_titles.append(article_title)
            article_bodies.append(body)
        df = pd.DataFrame({'title': article_titles, 'article': article_bodies,'article url': full_ikon_urls,})
        st.dataframe(data=df,width=1000000)

#################################
#Yahoo Sports
#################################

    elif option == 'Sports':
        if sports_option == 'NBA':
            response = requests.get("https://sports.yahoo.com/nba/news/")
        elif sports_option == 'Soccer':
            response = requests.get("https://sports.yahoo.com/soccer/news/")
        elif sports_option == 'NFL':
            response = requests.get("https://sports.yahoo.com/nfl/news/")
        elif sports_option == 'MLB':
            response = requests.get("https://sports.yahoo.com/mlb/news/")
        soup = BeautifulSoup(response.content,features="html.parser")
        sports_links = soup.find_all("li",{"class":"stream-item js-stream-content Bgc(t) Pos(r) Mb(24px)"})
        for link in sports_links:
            time = link.find("time").get_text(strip=True)
            if "h" in time:
                sports_a = link.find("a",{"class":"stream-title D(b) Td(n) Td(n):f C(--batcave) C($streamBrandHoverClass):h C($streamBrandHoverClass):fv"})
                sports_url = sports_a.get('href')
                sports_urls.append(sports_url)
        
        article_titles = []
        article_bodies = []
        for url in sports_urls:
            response = requests.get(url)
            soup = BeautifulSoup(response.content,features="html.parser")
            article_title = soup.find('h1').get_text(strip=True)
            article_paragraphs = soup.find_all('p')
            body = ""
            for paragraph in article_paragraphs:
                paragraph = paragraph.get_text(strip=True)
                body = body + paragraph
            article_titles.append(article_title)
            article_bodies.append(body)
        df = pd.DataFrame({'title': article_titles, 'article': article_bodies,'article url': sports_urls})
        st.dataframe(data=df,width=1000000)      
 
#################################
#Chess
#################################      

    elif option == 'Chess':
        response = requests.get("https://www.chess.com/news")
        soup = BeautifulSoup(response.content,features="html.parser")
        chess_links = soup.find_all("a",{"class":"post-preview-title"})
        for link in chess_links[:10]:
            chess_url = link.get('href')
            chess_urls.append(chess_url)
            
        article_titles = []
        article_bodies = []
        for url in chess_urls:
            response = requests.get(url)
            soup = BeautifulSoup(response.content,features="html.parser")
            article_title = soup.find('h1').get_text(strip=True)
            article_body = soup.find('div',{"class":"post-view-content"})
            article_titles.append(article_title)
            article_bodies.append(article_body.get_text(strip=True))
        df = pd.DataFrame({'article url': chess_urls, 'title': article_titles, 'article': article_bodies})
        st.dataframe(data=df,width=1000000) 

####################################
#Summarization
####################################

    if st.button('Summarize'):
        for text in df['article']:
            auto_abstractor = AutoAbstractor()
            auto_abstractor.tokenizable_doc = SimpleTokenizer()
            auto_abstractor.delimiter_list = [".", "\n"]
            abstractable_doc = TopNRankAbstractor()
            result_dict = auto_abstractor.summarize(text, abstractable_doc)
            for sentence in result_dict["summarize_result"]:
                st.write(sentence)
