import streamlit as st
from helper import spacy_rander, fetch_news, fetch_news_links, summarize_llm, categorize_news, get_summary
import newspaper
import json
import requests

st.set_page_config(
     page_title="Data Analysis Web App",
     page_icon="🧊",
     layout="wide",
     initial_sidebar_state="expanded",
)


st.sidebar.title("Text Summarization Web App")

option = ["News Summary and Headlines", "Custom Text Summarization", "Search news based on category"]
choice = st.sidebar.selectbox("Select your choice", options=option, format_func=lambda x: x)
#hoice = st.sidebar.radio("Select your choice", option)


if choice == "Custom Text Summarization":
    #st.sidebar.markdown("Copy Sample Article if you want to test the web app. [[article source](https://edition.cnn.com/2022/02/14/us/new-mexico-albuquerque-stabbings/index.html)]")
    #st.sidebar.code(open("presentation/sample.txt","r").read())
    st.title("Welcome to {}".format(choice))

    input_option = st.radio("Choose input option:", ["Text", "Link"])
    text = st.text_area(label="Enter Your Article Text or Link", height=350)
    
        

    
    # with st.container():
    #     text = st.text_area(label="Enter Your Text or Article", height=350, placeholder="Enter your text or article")

    if st.button("Get Summary and Category") :
        if input_option == "Text":
            # Summary and category processing
            summary = get_summary(text)
            categories = categorize_news(text)
        elif input_option == "Link":
            if text:
                try:
                    article = newspaper.Article(text)
                    article.download()
                    article.parse()
                    text = article.text[:15000]
                    st.success("Text fetched successfully!")
                    #st.code(text)
                    summary = get_summary(text)
                    categories = categorize_news(text)
                except Exception as e:
                    st.error(f"Error fetching text: {str(e)}")
                    st.stop()
            else:
                st.warning("Article too short to generate a summary. Please enter a longer article.")
                st.stop()            
        with st.container():
            if summary:
                st.subheader("Text Summary (Summary length: {})".format(len(summary)))
        
        # Display summary in a box with background
                summary_html = f'<div style="background-color:#f0f0f0; padding:10px; border-radius:5px;">{summary}</div>'
                st.markdown(summary_html, unsafe_allow_html=True)
        
                st.subheader("News Category")
                st.code(f'Category: {categories.get("label")} | Probability: {categories.get("score")}')

        # Rendering using Spacy
                spacy_rander(summary)

        # Original Article Analysis
                spacy_rander(text, text="Yes")
            else:
                st.warning("Article too short to generate a summary. Please enter a longer article.")


if choice == "News Summary and Headlines":
    st.title(" News Summary")

    search_query = st.text_input("", placeholder="Enter the topic you want to search")
    st.write(" ")

    link, title, thumbnail = fetch_news_links(search_query)
    fetch_news = fetch_news(link)
    
    if link != []:
        col1, col2 = st.columns(2)

        with col1:
            for i in range(len(link)):
                if (i % 2) == 0:
                    st.image(thumbnail[i])
                    st.write(title[i])
                    with st.expander("Read The Summary"):
                        st.write(get_summary(fetch_news[i]))
                    st.markdown("[**Read Full Article**]({})".format(link[i]), unsafe_allow_html=True)
                    st.write(" ")
        
        with col2:
            for i in range(len(link)):
                if (i % 2) != 0:
                    st.image(thumbnail[i])
                    st.write(title[i])
                    with st.expander("Read The Summary"):
                        st.write(get_summary(fetch_news[i]))
                    st.markdown("[**Read Full Article**]({})".format(link[i]), unsafe_allow_html=True)
                    st.write(" ")
    
    else:
        st.info("No Result found for {} Please try some popular Keywords".format(search_query))

if choice == "Search news based on category":

    response_json = None
    with st.form("news_category"):
        arc_map = {"Sports": "sports", "Business": "business", "World": 'world', "Sci/Tech": 'science_and_technology'}
        st.header("Welcome to Find News by Category")
        news_category = st.selectbox("Select news category", options=["Sports", "Business", 'World', "Sci/Tech"])
        submitted = st.form_submit_button("Show News")
        if submitted:
            headers = {
                'Authorization': 'ApiKey TjA5ckdJd0JKLUQ3RUJkdXdwY2I6Qk9xR2JTUWlTSGVQaUdGbXoxWXRjUQ==',
                'Content-Type': 'application/json',
            }

            response = requests.get(
                f'https://e8206b505dc648f78d24b894fef165b1.us-central1.gcp.cloud.es.io:443/search-news-article-data-298b/_search?q=category:{arc_map[news_category]}&from=0&size=1000&_source=article',
                headers=headers,
            )

            response_json = response.json()

    # Load JSON response
    # response_json = json.loads(response_data)

    if response_json:
        # Extract articles
        articles = [hit["_source"]["article"] for hit in response_json["hits"]["hits"]]

        # Display articles in two columns
        st.title("Articles")

        # Use a text box with columns to display articles
        col1, col2 = st.columns(2)

        for i, art in enumerate(articles):
            if i%2:
                col1.markdown(art)
            else:
                col2.markdown(art)

    # # Display articles in the first column
    # with col1:
    #     col1.text()
    #     st.text("\n".join(articles[:len(articles)//2]))

    # # Display articles in the second column
    # with col2:
    #     st.text("\n".join(articles[len(articles)//2:]))
