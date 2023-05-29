import streamlit as st
import streamlit.components.v1 as components
from streamlit_chat import message
from langchain import OpenAI, ConversationChain, LLMChain, PromptTemplate
from langchain.memory import ConversationBufferWindowMemory
from langchain.document_loaders import YoutubeLoader, BSHTMLLoader, WikipediaLoader
from langchain.indexes import VectorstoreIndexCreator
from langchain.text_splitter import CharacterTextSplitter
import os
import openai


os.environ["OPENAI_API_KEY"] = st.secrets["openai_api_key"]
openai.api_key = os.getenv("OPENAI_API_KEY")

with st.expander("Article about the history of the Royal Game of Ur from the New York Metropolitan Museum:"):
    #screenshot_url = "https://raw.githubusercontent.com/Dr-Hutchinson/Royal-Game-of-Ur/main/met_article_screenshot.png"
    st.markdown(
        "<a href='https://www.metmuseum.org/exhibitions/listings/2014/assyria-to-iberia/blog/posts/twenty-squares' target='_blank'><img src='https://raw.githubusercontent.com/Dr-Hutchinson/Royal-Game-of-Ur/main/met_article_screenshot.png'></a>",
        unsafe_allow_html=True
    )
    #st.image(screenshot_url)
    st.write("Click on the image above to open the [article](https://www.metmuseum.org/exhibitions/listings/2014/assyria-to-iberia/blog/posts/twenty-squares) in a new tab.")



with st.expander('Video about Irving Finkel of the British Museum, who discovered the rules for the Royal Game of Ur:'):
    video_url = "https://youtu.be/wHjznvH54Cw"
    st.video(video_url)

with st.expander('Game board for the Royal Game of Ur from the British Museum'):
    image_url_0 = "https://media.britishmuseum.org/media/Repository/Documents/2017_8/17_15/d63be997_915e_4d23_8bd6_a7d200fd2537/mid_WCO24357__1.jpg"
    st.image(image_url_0)
    st.write("[Link](https://www.britishmuseum.org/collection/object/W_1928-1009-378) to the catalog entry for the object in the British Musuem.")

with st.expander('Cuniform Tablet featuring rules for the Royal Game of Ur from the British Museum:'):
    image_url = "http://media.britishmuseum.org/media/Repository/Documents/2014_11/12_20/f8d09bf3_a156_4a95_befc_a3e101544e67/preview_00129985_001.jpg"
    st.image(image_url)
    st.write("[Link](https://www.britishmuseum.org/collection/object/W_Rm-III-6-b) to the catalog entry for the object in the British Musuem.")

with st.expander("Play the Royal Game of Ur:"):
    components.iframe("https://royalur.net/", width=800, height=600)


with st.expander("Chat about the Royal Game of Ur"):

    metmuseum_loader = BSHTMLLoader(file_path='./met_article.html')
    wikipedia_loader = WikipediaLoader("https://en.wikipedia.org/wiki/Royal_Game_of_Ur")

    # Load the YouTube transcript
    loader = YoutubeLoader.from_youtube_url("https://youtu.be/wHjznvH54Cw", add_video_info=False, language='en-GB')
    docs = loader.load()

    metmuseum_docs = metmuseum_loader.load()
    wikipedia_docs = wikipedia_loader.load()

    for doc in metmuseum_docs:
        st.session_state.history += f"MetMuseum Document: {doc.text}\n"
    for doc in wikipedia_docs:
        st.session_state.history += f"Wikipedia Document: {doc.text}\n"

    # Print the loaded documents
    st.write("Loaded documents:")
    for doc in docs:
        st.write(doc)

    # Split the transcript into chunks
    text_splitter = CharacterTextSplitter(chunk_size=100, chunk_overlap=10)
    split_docs = text_splitter.split_documents(docs)

    # Create an index from the split documents
    index = VectorstoreIndexCreator().from_documents(split_docs)

    # Print the created index
    st.write("Created index:")
    st.write(index)


    template = """You are an educational chatbot with access to various data sources on the Royal Game of Ur. When given a user question you will be supplied with information from those sources. Based on those sources, compose an insightful and accurate answer based on those sources.
    ...
    {history}
    Human: {human_input}
    Assistant:"""

    prompt = PromptTemplate(
     input_variables=["history", "human_input"],
     template=template
    )

    chatgpt_chain = LLMChain(
     llm=OpenAI(temperature=0),
     prompt=prompt,
     verbose=True,
     memory=ConversationBufferWindowMemory(k=2),
    )

    if 'history' not in st.session_state:
        st.session_state.history = ""

    message("Messages from the bot", key="message_0")
    message("Your messages", is_user=True, key="message_1")

    if st.session_state.history:
        for i, line in enumerate(st.session_state.history.split('\n')):
            if line.startswith('Human:'):
                message(line[6:], is_user=True, key=f"message_{i+2}")
            elif line.startswith('Assistant:'):
                message(line[10:], key=f"message_{i+2}")
            elif line.startswith('Document being fed into the model:'):
                message(line[32:], key=f"message_{i+2}")
            elif line.startswith('MetMuseum Document:'):
                message(line[18:], key=f"message_{i+2}")
            elif line.startswith('Wikipedia Document:'):
                message(line[19:], key=f"message_{i+2}")

    user_input = st.text_input("Enter your message:")

    if st.button("Send"):
        if user_input:
            st.session_state.history += f"Human: {user_input}\n"
            output = chatgpt_chain.predict(human_input=user_input)
            youtube_response = index.query(user_input)

            st.write("Document being fed into the model:")
            st.write(youtube_response)

            output += "\n" + youtube_response
            st.session_state.history += f"Assistant: {output}\n"
            st.session_state.history += f"Document being fed into the model: {youtube_response}\n"
            st.text_input("Enter your message:", value="", key="user_input")
            st.experimental_rerun()
