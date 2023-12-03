import streamlit as st
from helper import spacy_rander, fetch_news, fetch_news_links, summarize_llm, categorize_news, get_summary


st.set_page_config(
     page_title="Data Analysis Web App",
     page_icon="🧊",
     layout="wide",
     initial_sidebar_state="expanded",
     menu_items={
         'Get Help': 'https://github.com/everydaycodings/Text-Summarization-using-NLP',
         'Report a bug': "https://github.com/everydaycodings/Text-Summarization-using-NLP/issues/new",
         'About': "# This is a header. This is an *extremely* cool app!"
     }
)


st.sidebar.title("Text Summarization Web App")

option = ["News Summary and Headlines", "Custom Text Summarization"]
choice = st.sidebar.selectbox("Select of your choice", options=option)


if choice == "Custom Text Summarization":
    st.sidebar.markdown("Copy Sample Article if you want to test the web app. [[article source](https://edition.cnn.com/2022/02/14/us/new-mexico-albuquerque-stabbings/index.html)]")
    st.sidebar.code(open("presentation/sample.txt","r").read())
    st.title("Welcome to {}".format(choice))

    with st.container():
        text = st.text_area(label="Enter Your Text or Article", height=350, placeholder="Enter your text or article")

    if st.button("Get Summary and Category"):
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


    # col1, col2 = st.columns(2)

    # with col1:
    #     text = st.text_area(label="Enter Your Text or article", height=350, placeholder="Enter Your Text or story or your article")
        
    # if st.button("Get Summary and Category"):
    #     #summary = summarize_llm(text)
    #     summary = get_summary(text)
    #     categories = categorize_news(text)

    #     try:
    #         with col2:
    #             if summary:
    #                 st.write("Text Summary (Summary length: {})".format(len(summary)))
    #                 st.text(summary)
    #                 # st.expander("Article Summary",expanded=True)
    #                 # st.code(summary, language='markdown')

    #             else:
    #                 st.warning("Article too short to generate summary. Please enter a longer article.")
    #             st.write("News Category")
    #             st.code(f'Category: {categories.get("label")} | Probability: {categories.get("score")}')
    #         if summary:
    #             spacy_rander(summary)

    #             #with st.expander("Get Original Article Analysis"):
    #             spacy_rander(text, text="Yes")
            
    #     except NameError:
    #         pass

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
