from random import random
from spacy.lang.en.stop_words import STOP_WORDS
import en_core_web_sm
from string import punctuation
from heapq import nlargest
import spacy_streamlit
import requests
import json
from bs4 import BeautifulSoup
import configparser
import streamlit as st
import random
from transformers import AutoTokenizer, AutoModelForSeq2SeqLM, AutoModelForSequenceClassification, TextClassificationPipeline
from decouple import AutoConfig()
import spacy


tokenizer = AutoTokenizer.from_pretrained("mrm8488/t5-base-finetuned-summarize-news")
model = AutoModelForSeq2SeqLM.from_pretrained("mrm8488/t5-base-finetuned-summarize-news")


# nlp= en_core_web_sm.load()
nlp= spacy.load("en_core_web_sm")
stopwords = list(STOP_WORDS)
punctuation = punctuation + "\n"

config = AutoConfig()
news_api_key = config('NEWS_API')



def spacy_rander(summary, text=None):

    summ = nlp(summary)
    if text == "Yes":
        rend = spacy_streamlit.visualize_ner(summ, labels=nlp.get_pipe("ner").labels, title="Full Article Visualization", show_table=False, key=random.randint(0, 100))
    
    else:
        rend = spacy_streamlit.visualize_ner(summ, labels=nlp.get_pipe("ner").labels, title="Summary Visualization", show_table=False, key=random.randint(0, 100))
    
    return rend



def word_frequency(doc):
    word_frequencies = {}

    for word in doc:
        if word.text.lower() not in stopwords:
            if word.text.lower() not in punctuation:
                if word.text not in word_frequencies.keys():
                    word_frequencies[word.text] = 1
                else:
                    word_frequencies[word.text] += 1
    
    return word_frequencies




def sentence_score(sentence_tokens, word_frequencies):
    sentence_score = {}

    for sent in sentence_tokens:
        for word in sent:
            if word.text.lower() in word_frequencies.keys():
                if sent not in sentence_score.keys():
                    sentence_score[sent] = word_frequencies[word.text.lower()] 
                else:
                    sentence_score[sent] += word_frequencies[word.text.lower()]
    
    return sentence_score


@st.cache(allow_output_mutation=False)
def fetch_news_links(query):
    link_list = []
    title_list = []
    thumbnail_list = []

    if query == "":
        reqUrl = "https://newsapi.org/v2/everything?sources=bbc-news&q=india&language=en&apiKey={}".format(news_api_key)
    else:
        reqUrl = "https://newsapi.org/v2/everything?sources=bbc-news&q={}&language=en&apiKey={}".format(query, news_api_key)
    
    headersList = {
    "Accept": "*/*",
    "User-Agent": "Thunder Client (https://www.thunderclient.com)" 
    }

    payload = ""

    response = requests.request("GET", reqUrl, data=payload,  headers=headersList).text
    response = json.loads(response)

    tw = 0
    for i in range(len(response["articles"])):
        if tw ==10:
            pass
        else:
            if "/news/" in response["articles"][i]["url"] and "stories" not in response["articles"][i]["url"]:
                link_list.append(response["articles"][i]["url"])
                title_list.append(response["articles"][i]["title"])
                thumbnail_list.append(response["articles"][i]["urlToImage"])
            else:
                pass
            tw += 1

    return link_list, title_list, thumbnail_list



@st.cache(allow_output_mutation=False)
def fetch_news(link_list):

    news = []
    news_list = []

    for i in range(len(link_list)):
        news_reqUrl = link_list[i]
        headersList = {
        "Accept": "*/*",
        "User-Agent": "Thunder Client (https://www.thunderclient.com)" 
        }

        payload = ""

        news_response = requests.request("GET", news_reqUrl, data=payload,  headers=headersList)
        soup = BeautifulSoup(news_response.content, features="html.parser")
        soup.findAll("p", {"class":"ssrcss-1q0x1qg-Paragraph eq5iqo00"})
        soup.findAll("div", {"data-component":"text-block"})
        for para in soup.findAll("div", {"data-component":"text-block"}):
                news.append(para.find("p").getText())
        joinnews = " ".join(news)
        news_list.append(joinnews)
        news.clear()
    
    return news_list


def summarize_llm(text):
    max_length = 150
    input_ids = tokenizer.encode(text, return_tensors="pt", add_special_tokens=True)

    generated_ids = model.generate(input_ids=input_ids, num_beams=2, max_length=max_length,  repetition_penalty=2.5, length_penalty=1.0, early_stopping=True)

    preds = [tokenizer.decode(g, skip_special_tokens=True, clean_up_tokenization_spaces=True) for g in generated_ids]

    return preds[0]    

def categorize_news(text):
    # Load model directly

    tokenizer = AutoTokenizer.from_pretrained("wesleyacheng/news-topic-classification-with-bert")
    model = AutoModelForSequenceClassification.from_pretrained("wesleyacheng/news-topic-classification-with-bert")
    pipe = TextClassificationPipeline(model=model, tokenizer=tokenizer)
    prediction = pipe(text, return_all_scores=True)
    flat_data = [item for sublist in prediction for item in sublist]

    # Find the maximum key-value pair based on the "score"
    max_pair = max(flat_data, key=lambda x: x['score'])
    return max_pair




def get_summary(text):
    
    doc = nlp(text)

    word_frequencies = word_frequency(doc)
    for word in word_frequencies.keys():
        word_frequencies[word] = word_frequencies[word] / max(word_frequencies.values())
    
    sentence_tokens = [sent for sent in doc.sents]
    sentence_scores = sentence_score(sentence_tokens, word_frequencies)

    
    select_length = int(len(sentence_tokens)*0.10)
    summary  = nlargest(select_length, sentence_scores, key=sentence_scores.get)
    summary = [word.text  for word in summary]
    summary = " ".join(summary)

    return summary





    
