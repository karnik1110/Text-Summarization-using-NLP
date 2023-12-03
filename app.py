import streamlit as st
from helper import spacy_rander, fetch_news, fetch_news_links, summarize_llm, categorize_news, get_summary, fetch_text
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

option = ["News Summary and Headlines", "Custom Text Summarization", "Find News by Category"]
choice = st.sidebar.selectbox("Select your choice", options=option, format_func=lambda x: x)


if choice == "Custom Text Summarization":
    st.title("Welcome to {}".format(choice))

    input_option = st.radio("Choose input option:", ["Text", "Link"])
    text = st.text_area(label="Enter Your Article Text or Link", height=350)

    if st.button("Get Summary and Category") :
        if input_option == "Text":
            # Summary and category processing
            summary = get_summary(text)
            categories = categorize_news(summary)
        elif input_option == "Link":
            if text:
                try:
                    text = fetch_text(text)
                    #text = text[:7000]
                    st.success("Text fetched successfully!")
                    st.code(text)
                except Exception as e:
                    st.error(f"Error fetching text: {str(e)}")
                    st.stop()
                try:
                    summary = get_summary(text)
                    categories = categorize_news(summary)
                except Exception as e:
                    st.error(f"Error Summarizing text: {str(e)}")
                    print(e)
                    raise e
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
                st.code(f'Category: {categories.get("label")} | Probability: {round(categories.get("score")*100,2)}%')

        # Rendering using Spacy
                spacy_rander(summary)

        # Original Article Analysis
                spacy_rander(text, text="Yes")
            else:
                st.warning("Article too short to generate a summary. Please enter a longer article.")


if choice == "News Summary and Headlines":
    st.title("Welcome to News Summary and Headlines")

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
#Second format with slider
#     with st.form("news_category"):
#         arc_map = {"Sports": "sports", "Business": "business", "World": 'world', "Sci/Tech": 'science_and_technology'}
#         st.header("Choose News Category and Number of Articles")
#         news_category = st.selectbox("Select news category", options=["Sports", "Business", 'World', "Sci/Tech"])
#         number = st.slider("Number of news articles to fetch", min_value=1, max_value=10, value=5)
#         submitted = st.form_submit_button("Show News")
#         if submitted:
#             headers = {
#         'Authorization': 'ApiKey TjA5ckdJd0JKLUQ3RUJkdXdwY2I6Qk9xR2JTUWlTSGVQaUdGbXoxWXRjUQ==',
#         'Content-Type': 'application/json',
#     }

#             response = requests.get(
#                 f'https://e8206b505dc648f78d24b894fef165b1.us-central1.gcp.cloud.es.io:443/search-news-article-data-298b/_search?q=category:{arc_map[news_category]}&from=0&size={number}&_source=article',
#                 headers=headers,
#             )

#             response_json = response.json()
if choice == "Find News by Category":

    response_json = None
    col1, col2 = st.columns(2)
    with col1.form("news_category"):
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
        if response_json:
        # Extract articles and filter by minimum character limit
            articles = [hit["_source"]["article"] for hit in response_json["hits"]["hits"] if len(hit["_source"]["article"]) >= 0]

            # Display total number of articles
            st.header(f"Found {len(articles)} Articles")

            # Use a text box with columns to display articles
            col1, col2 = st.columns(2)
            for i, art in enumerate(articles):
                if i % 2:
                    col2.markdown(f'<div style="background-color:#f0f0f0; padding:10px; border-radius:5px; margin-bottom:10px;"><strong>Article {i+1}:</strong><br>{art}</div>', unsafe_allow_html=True)
                else:
                    col1.markdown(f'<div style="background-color:#f0f0f0; padding:10px; border-radius:5px; margin-bottom:10px;"><strong>Article {i+1}:</strong><br>{art}</div>', unsafe_allow_html=True)

