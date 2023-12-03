import streamlit as st
from helper import spacy_rander, fetch_news, fetch_news_links, summarize_llm, categorize_news, get_summary
import newspaper

st.set_page_config(
     page_title="Data Analysis Web App",
     page_icon="🧊",
     layout="wide",
     initial_sidebar_state="expanded",
)


st.sidebar.title("Text Summarization Web App")

option = ["News Summary and Headlines", "Custom Text Summarization"]
choice = st.sidebar.selectbox("Select your choice", options=option, format_func=lambda x: x)
#hoice = st.sidebar.radio("Select your choice", option)


if choice == "Custom Text Summarization":
    #st.sidebar.markdown("Copy Sample Article if you want to test the web app. [[article source](https://edition.cnn.com/2022/02/14/us/new-mexico-albuquerque-stabbings/index.html)]")
    #st.sidebar.code(open("presentation/sample.txt","r").read())
    st.title("Welcome to {}".format(choice))

    input_option = st.radio("Choose input option:", ["Text", "Link"])
    
    if input_option == "Text":
        text = st.text_area(label="Enter Your Text or Article", height=350, placeholder="Enter your text or article")

    elif input_option == "Link":
        article_link = st.text_input(label="Enter the article link", placeholder="Paste the article link here")
        if st.button("Fetch Text"):
            try:
                article = newspaper.Article(article_link)
                article.download()
                article.parse()
                text = article.text
                st.success("Text fetched successfully!")
                st.code(text)
            except Exception as e:
                st.error(f"Error fetching text: {str(e)}")
                st.stop()
    # with st.container():
    #     text = st.text_area(label="Enter Your Text or Article", height=350, placeholder="Enter your text or article")

    if st.button("Get Summary and Category") :
        # Summary and category processing
        summary = get_summary(text)
        categories = categorize_news(text)

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
    st.title("BBC News Summary")

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
