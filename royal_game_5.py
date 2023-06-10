import streamlit as st
import streamlit.components.v1 as components
from streamlit_extras.colored_header import colored_header
from streamlit_extras.add_vertical_space import add_vertical_space
from streamlit_extras.app_logo import add_logo
from streamlit_chat import message
import streamlit_authenticator as stauth
from langchain import OpenAI, ConversationChain, LLMChain, PromptTemplate
from langchain.memory import ConversationBufferWindowMemory
from langchain.document_loaders import YoutubeLoader, BSHTMLLoader, WikipediaLoader
from langchain.indexes import VectorstoreIndexCreator
from langchain.text_splitter import CharacterTextSplitter
from langchain.chat_models import ChatOpenAI
from langchain.prompts import (
    SystemMessagePromptTemplate,
    HumanMessagePromptTemplate,
    ChatPromptTemplate,
    MessagesPlaceholder
)
from langchain.chains.conversation.memory import ConversationBufferWindowMemory
from langchain.callbacks import get_openai_callback
import os
import openai
import pygsheets
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload
from google.oauth2.service_account import Credentials
from google.oauth2 import service_account
import pandas as pd
import pydeck as pdk
import numpy as np
from openai.embeddings_utils import get_embedding, cosine_similarity
from datetime import datetime as dt
import random
import tiktoken
import matplotlib.pyplot as plt

st.set_page_config(layout="wide")

os.environ["OPENAI_API_KEY"] = st.secrets["openai_api_key"]
openai.api_key = os.getenv("OPENAI_API_KEY")

os.environ["MAPBOX_API_KEY"] = st.secrets["mapbox_api_key"]
mapbox_api_key = os.getenv("MAPBOX_API_KEY")

scope = ['https://spreadsheets.google.com/feeds',
         'https://www.googleapis.com/auth/drive']

credentials = service_account.Credentials.from_service_account_info(
                st.secrets["gcp_service_account"], scopes = scope)
gc = pygsheets.authorize(custom_credentials=credentials)

#login setup for streamlit_authenticator via Google Sheets API
sh0 = gc.open('ur_users')
wks0 = sh0[0]
database_length = wks0.get_all_values(include_tailing_empty_rows=False, include_tailing_empty=False, returnas='matrix')
end_row0 = str(len(database_length))
usernames_grab = wks0.get_as_df(has_header=False, index_column=0, start='A2', end=('A'+end_row0), numerize=False)
usernames_list = usernames_grab.values.tolist()
access_grab= wks0.get_as_df(has_header=False, index_column=0, start='B2', end=('B'+end_row0), numerize=False)
access_list = access_grab.values.tolist()
names_grab = wks0.get_as_df(has_header=False, index_column=0, start='C2', end=('C'+end_row0), numerize=False)
names_list = names_grab.values.tolist()
user_id_grab = wks0.get_as_df(has_header=False, index_column=0, start='D2', end=('D'+end_row0), numerize=False)
user_id_list = names_grab.values.tolist()

#streamlit_authenticator login
names =  [lst[0] for lst in names_list]
usernames = [lst[0] for lst in usernames_list]
passwords = [lst[0] for lst in access_list]
user_ids = [lst[0] for lst in user_id_list]
hashed_passwords = stauth.Hasher(passwords).generate()

authenticator = stauth.Authenticate(names, usernames, hashed_passwords,
    'some_cookie_name', 'some_signature_key', cookie_expiry_days=300)
name, authentication_status, username = authenticator.login('Login', 'main')

if authentication_status:
    authenticator.logout('Logout', 'main')
    st.write('Welcome *%s*' % (name))

    with st.expander("Map showing locations discussed in this assignment."):
        #df = pd.DataFrame({
        #'lat': [30.961653],
        #'lon': [46.105126]
        #})
        #Display the map
        #st.map(df)
        # Define the initial viewport
        view_state = pdk.ViewState(
         latitude=30.961653,
         longitude=46.105126,
         zoom=17
        )


        # Original - Define the data for the marker
        #data = pd.DataFrame({
            #'Latitude': [30.961653],
            #'Longitude': [46.105126]
        #})

        #data = pd.DataFrame({
            #'Latitude': [30.961653],
            #'Longitude': [46.105126],
            #'tooltip': [
            #    "<img src='https://www.metmuseum.org/-/media/images/exhibitions/2014/assyria-to-iberia/blog/twentysquares4.jpg' width='400px'><br><b>Gameboard unearthed for the royal tombs of Ur, c. 2500 BC. British Museum.</b>"
            #]
        #})

        data = pd.DataFrame({
            'Latitude': [30.961653, 35.158333, 25.727851, 31.859, 36.8266, 36.229444],
            'Longitude': [46.105126, 33.891111, 32.610801, 34.919, 40.0396, 43.403333],
            'tooltip': [
                "<img src='https://media.britishmuseum.org/media/Repository/Documents/2017_8/17_15/d63be997_915e_4d23_8bd6_a7d200fd2537/mid_WCO24357__1.jpg' width='300px' height='300px'><div style='word-wrap: break-word; width: 300px;'><br><b>Gameboard unearthed for the royal tombs of Ur, c. 2500 BC. British Museum.</b>",
                "<img src='https://www.metmuseum.org/-/media/images/exhibitions/2014/assyria-to-iberia/blog/twentysquares1.jpg' width='300px' height='300px'><div style='word-wrap: break-word; width: 300px;'><br><b>Game box with chariot hunt, ca. 1250–1100 B.C. Enkomi, Cyprus. British Museum.</b>",
                "<img src='https://www.metmuseum.org/-/media/images/exhibitions/2014/assyria-to-iberia/blog/twentysquares2.jpg' width='300px' height='300px'><div style='word-wrap: break-word; width: 300px;'><br><b>Double-sided game box with playing pieces and a pair of knucklebones. Thebes, Egypt. ca. 1635–1458 B.C. The Metropolitan Museum of Art, New York</b>",
                "<img src='https://www.metmuseum.org/-/media/images/exhibitions/2014/assyria-to-iberia/blog/twentysquares5.jpg' width='300px' height='300px'><div style='word-wrap: break-word; width: 300px;'><br><b>Ivory game board, 10th–9th century B.C. Tel Gezer, Israel.</b>",
                "<img src='https://www.metmuseum.org/-/media/images/exhibitions/2014/assyria-to-iberia/blog/twentysquares6.jpg' width='300px' height='300px'><div style='word-wrap: break-word; width: 300px;'><br><b>Chariot scene on the reverse of a game of twenty squares. Tell Halaf, Syria, early first millennium B.C</b>",
                "<img src='https://www.metmuseum.org/-/media/images/exhibitions/2014/assyria-to-iberia/blog/twentysquares7.jpg' width='300px' height='300px'><div style='word-wrap: break-word; width: 300px;'><br><b>Detail of the decorated side of a game of twenty squares, Balawat (Iraq). 9th–8th century B.C. The Louvre</b>"
            ]
        })


        # Define the icon data
        icon_data = {"url":"https://img.icons8.com/plasticine/100/000000/marker.png", "width":128, "height":128, "anchorY":128}
        # Add the icon data to the dataframe
        #data["icon"] = [icon_data]
        data["icon"] = [icon_data for _ in range(len(data))]
        # Define the layer to add to the map
        layer = pdk.Layer(
            type="IconLayer",
            data=data,
            get_icon="icon",
            get_size=4,  # Adjust size as needed
            size_scale=15,  # Adjust scale as needed
            get_position=["Longitude", "Latitude"],
            pickable=True,
        )
        # Let the user toggle between map styles
        is_satellite = st.checkbox('Show satellite view')
        if is_satellite:
            map_style = 'mapbox://styles/mapbox/satellite-v9'
        else:
            map_style = 'mapbox://styles/mapbox/streets-v11'
        #tooltip = {
        #    "html": "<b>Latitude:</b> {Latitude}<br/><b>Longitude:</b> {Longitude}",
        #    "style": {
        #        "backgroundColor": "steelblue",
        #        "color": "white"
        #    }
        #}
        tooltip={
            "html": "{tooltip}",
            "style": {
                "backgroundColor": "steelblue",
                "color": "white"
            }
        }
        # Define the map
        r = pdk.Deck(
         map_style=map_style,
         initial_view_state=view_state,
         layers=[layer],  # Add the layer to the map
         tooltip=tooltip
        )
        # Display the map
        st.pydeck_chart(r)

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

    #with st.expander("Test Space for Prompt Game 0"):


    # begin chatbot
    # based on: https://github.com/PradipNichite/Youtube-Tutorials/blob/main/Langchain%20Chatbot/utils.py

    with st.expander("Talk with ChatGPT about the Royal Game of Ur."):

        def game_of_questions():

            st.title("The Game of Questions")

            st.header("Assignment Objectives")

            st.write("Learn how to effectively use Large Language Models (LLMs) through asking different types questions about the Royal Game of Ur.\n\nLearn how to distinguish factual AI outputs from hallucinations.")

            st.header("Instructions:")
            st.write("""**Asking the Right Questions:** Begin by exploring the chatbot's capabilities. Ask it questions about the Royal Game of Ur and observe how it responds. Try to understand how the phrasing and specificity of your questions affect the responses.\n\n**Learning from the Chatbot:** Use the chatbot as a learning tool. Ask it questions about the history, rules, and significance of the Royal Game of Ur. Use the information provided by the chatbot to deepen your understanding of the game.\n\n**Fact-checking the AI**: Remember that AI can sometimes generate "hallucinations" or false information. After receiving a response from the chatbot, try verifying the information using the assignment sources. This will help you learn to distinguish between factual AI outputs and hallucinations.""")

            st.header("Rubric:")
            st.write("""**Learning from the Chatbot** (40 points):\n\nEffectively uses the chatbot as a learning tool, as demonstrated in the chat logs (40 points)\n\n**Prompting and Querying** (30 points):\n\nEffectively uses a variety of question types (10 points)\n\nDemonstrates understanding of how to phrase questions for optimal responses (10 points)\n\nShows creativity and depth in the questions asked (10 points)\n\n**Fact-checking the AI** (30 points):\n\nAccurately identifies factual information from the chatbot (15 points)\n\nAccurately identifies false information from the chatbot (15 points))""")

            #st.write("This chatbot has access to the sources for this assignment. You can ask it questions about the Royal Game of Ur and it will offer a response drawn from the texts. However, pleae note that AI interpretations of data can lead to convincing but incorrect answers.")

            st.header("Chatbot Interface:")
            st.write("""
This is where you'll interact with the chatbot. You can type your questions into the text box and press 'Submit Question' to get a response. The chatbot will then generate a response based on the sources it has been given.

If the chatbot displays an error, or if you wish to reboot the chat history, click the 'Reset Chat History' button. This will clear all previous questions and responses, allowing you to start a new conversation with the chatbot.

Remember, the chatbot is a tool to help you learn. If you don't understand a response, or if you think the chatbot has made a mistake, don't be afraid to ask for clarification or to challenge the information it provides. This is a great way to learn more about the topic and to improve your skills in interacting with AI.

Once you're done asking questions and learning from the chatbot, answer the questions in the **Quiz Submission** space. You can submit your assignment for grading by clicking the 'Submit Quiz' button. This will upload your chat history, including all your questions and the chatbot's responses, for review. Make sure you're satisfied with your questions and the chatbot's responses before you submit your quiz.
""")

            colored_header(
                label="",
                description="\n\n",
                color_name="violet-70",
            )

            if st.button('Reset Chat History'):
                st.session_state['requests'] = []
                st.session_state['responses'] = ["How can I assist you?"]
                st.session_state['sources'] = []
                st.experimental_rerun()

            datafile_path = "ur_source_embeddings.csv"
            df = pd.read_csv(datafile_path)
            df["embedding"] = df.embedding.apply(eval).apply(np.array)
            def embeddings_search(query, df, n=3):
                    # Get the embedding of the query
                query_embedding = get_embedding(
                    query,
                    engine="text-embedding-ada-002"
                )
                    # Calculate cosine similarity between the query and each document
                df["similarities"] = df.embedding.apply(lambda x: cosine_similarity(x, query_embedding))
                # Get the top n most similar documents
                top_n = df.sort_values("similarities", ascending=False).head(n)
                return top_n

            if 'responses' not in st.session_state:
                st.session_state['responses'] = ["How can I assist you?"]

            if 'requests' not in st.session_state:
                st.session_state['requests'] = []

            if 'sources' not in st.session_state:
                st.session_state['sources'] = []

            llm = ChatOpenAI(model_name="gpt-3.5-turbo", openai_api_key=st.secrets["openai_api_key"])

            if 'buffer_memory' not in st.session_state:
                st.session_state.buffer_memory=ConversationBufferWindowMemory(k=1,return_messages=True)

            def get_conversation_string():
                conversation_string = ""
                for i in range(len(st.session_state['responses'])-1):
                    conversation_string += "Human: "+st.session_state['requests'][i] + "\n"
                    conversation_string += "Bot: "+ st.session_state['responses'][i+1] + "\n"
                return conversation_string

            #prompt = ("You are an educational chatbot with access to various data sources on the Royal Game of Ur. "
            #          "Your purpose is to assist students in learning about the history, rules, and significance of the Royal Game of Ur. "
            #          "When given a user question, you will be supplied with information from those sources. \n\n"
            #          "1. **Answering Questions**: Provide insightful, engaging, and accurate answers based on the sources. "
            #          "If the answer isn't in the sources, indicate that you can't answer that with the information you currently have access to. "
            #          "Don't cite other sources besides the ones provided to you.\n\n"
            #          "2. **Citing Sources**: Always cite the source of the information used in the answer. "
            #          "This will help students verify the information.\n\n"
            #          "3. **Encouraging Exploration**: Encourage students to ask a variety of questions. "
            #          "Help them understand how the phrasing and specificity of their questions can affect the responses.\n\n"
            #          "4. **Handling Hallucinations**: If a student points out a potential hallucination or false information in your response, "
            #          "acknowledge the possibility, and encourage them to verify the information using the assignment sources.\n\n"
            #          "Remember, your goal is not just to provide information, but to help students learn how to effectively use Large Language Models (LLMs), "
            #          "ask the right questions, and distinguish between factual AI outputs and hallucinations.\n\n"
            #          "Here is an example chat dialogue who approach I'd like you to emulate:\n\n"
            #          """Human: Tell me about the rules of the Royal Game of Ur, and who discovered how to play the game.\n\nAssistant: The Royal Game of Ur is an ancient board game that dates back to the 2nd century BC. It was discovered by Irving Finkel, a curator at the British Museum, who deciphered the world's oldest rule book and was able to reconstruct the game. The game is played on a board with 20 squares and two players use round black and white pieces and two kinds of dice to #generate scores. Finkel's discovery has allowed us to understand how the game was played in ancient times.\n\nSource: "Deciphering the world's oldest rule book with  Irving Finkel.""")

            prompt = ("I asked you to compress a long text using your own abbreviations. You replied with:\n\n "
                      "EduChatbot, Royal Game of Ur data. Purpose: assist learning history, rules, significance. Info from sources. 1. Answer Qs: insightful, accurate, if no answer, indicate. 2. Cite sources. 3. Encourage exploration. 4. Handle hallucinations. Goal: help learn use of LLMs, ask right Qs, distinguish facts & hallucinations. Ex: Human: Rules & discoverer of game? Assistant: Ancient game, 2nd century BC, discovered by Irving Finkel, British Museum. 20 squares, 2 players, black & white pieces, 2 dice. Source: Finkel's rule book deciphering\n\n"
                      "Reconstruct the original text, and use it as your guide for answering questions, but don't mention it in your responses.\n\n")

            #system_msg_template = SystemMessagePromptTemplate.from_template(template="""You are an educational chatbot with access to various data sources on the Royal Game of Ur. When given a user question you will be supplied with information from those sources. Based on those sources, compose an insightful, engaging, and accurate answer based on those source. Cite the source of the information used in the answer. If the answer isn't in the sources, indicate that you can't answer that with the information you currently have access to. Don't cite other sources besides the ones provided to you.""")

            system_msg_template = SystemMessagePromptTemplate.from_template(template=prompt)

            human_msg_template = HumanMessagePromptTemplate.from_template(template="{input}")

            prompt_template = ChatPromptTemplate.from_messages([system_msg_template, MessagesPlaceholder(variable_name="history"), human_msg_template])

            conversation = ConversationChain(memory=st.session_state.buffer_memory, prompt=prompt_template, llm=llm, verbose=True)

            # token counting script
            encoding = tiktoken.encoding_for_model("gpt-3.5-turbo")

            def count_tokens(chain, query):
                with get_openai_callback() as cb:
                    result = chain.predict(input=query)
                    print(f'Spent a total of {cb.total_tokens} tokens')
                    return result, cb.total_tokens

            token_counts = []

            # container for chat history
            response_container = st.container()
            # container for text box
            textcontainer = st.container()


            with textcontainer:
                with st.form(key='chat_form'):
                    query = st.text_input("Enter your question to the chatbot here: ", key="input")
                    submit_button = st.form_submit_button(label='Submit Question')
                    if submit_button and query is not None and query != "":
                        with st.spinner("Getting Response..."):
                            results_df = embeddings_search(query, df, n=3)
                            st.dataframe(results_df)
                            conversation_string = get_conversation_string()
                            for index, row in results_df.iterrows():
                                conversation_string += "\n\n" + str(row['combined'])
                            st.write(f"{prompt}\nHere are your data sources:\n {conversation_string} \n\nUse the relevant information in the data sources to answer this question:\n{query}")

                            #tokens = encoding.encode(f"{prompt}\nQuery:\n{query}\n\nContext:\n {conversation_string}")
                            #token_count = len(tokens)
                            #st.write(f"Token count: {token_count}")
                            #response = conversation.predict(input=f"Query:\n{query}\n\nContext:\n {conversation_string}"))
                            response, tokens = count_tokens(conversation, f"Query:\n{query}\n\nContext:\n {conversation_string}")
                            token_counts.append(tokens)
                            st.write("Token Count= " + str(token_counts))

                            fig = plt.figure(figsize=(10, 6))
                            plt.plot(range(len(token_counts)), token_counts, marker='o')
                            plt.xlabel('Query Number')
                            plt.ylabel('Token Count')
                            plt.title('Token Count of ConversationChain Over Time')
                            st.pyplot(fig)

                            # Convert the "unnamed:" column values into a list
                            #source_rows = results_df["Unnamed:0"].tolist()
                            source_rows = results_df.loc[:, 'Unnamed: 0'].tolist()

                            # Convert the integers in the list to strings
                            source_rows = [str(i) for i in source_rows]
                            # Join the strings in the list with a comma and a space
                            source_string = ", ".join(source_rows)
                            # Add the "Sources:" prefix to the string
                            source_string = "Sources: " + source_string

                            st.session_state.requests.append(query)
                            st.session_state.responses.append(response)
                            #st.session_state.sources.append(source_string)



                with response_container:
                    if st.session_state['responses']:
                        for i in range(len(st.session_state['responses'])):
                            message(st.session_state['responses'][i],key=str(i))
                            if i < len(st.session_state['requests']):
                                message(st.session_state["requests"][i], is_user=True,key=str(i)+ '_user')



            with st.form(key='quiz_form'):
                st.header("Quiz Submission:")
                st.write("In the space below, offer your thoughts on the following questions:\n\n**1. The Game of Questions:** What approach did you take to framing your questions? What techniques did you find as most or least effective?\n\n**2. Learning from the Chatbot:** How helpful did you find the chatbot in enhancing your knowledge about the Royal Game of Ur?\n\n**3. AI Accuracy**: How did you assess the accuracy of the chatbot's responses? Based on your comprehension of the assisgnment materials, how well does the AI accurately capture factual information?")
                st.text_area("Enter your response here.")
                st.write("""Click on the Submit Quiz button to upload your chat history and quiz response for grading.""" )
                submit_quiz_button = st.form_submit_button(label='Submit Quiz')
                if submit_quiz_button:
                    now = dt.now()
                    formatted_history = f"User: {username}\nTime: {now}\n\n" + get_conversation_string()
                    with open('chat_history.txt', 'w') as f:
                        f.write(formatted_history)
                    credentials = Credentials.from_service_account_info(st.secrets["gcp_service_account"])
                    drive_service = build('drive', 'v3', credentials=credentials)
                    media = MediaFileUpload('chat_history.txt', mimetype='text/plain')
                    request = drive_service.files().create(media_body=media, body={
                        'name': 'chat_history.txt',
                        'parents': ['1p2ZUQuSclMvFwSEQLleaRQs0tStV_-Mu']
                    })
                    response = request.execute()
                    # Print the response
                    st.write("Quiz Submitted.")


        quiz_choice = st.selectbox("Choose chatbot type", ['Game of Questions', 'GeoQuiz'])

        if quiz_choice == "Game of Questions":
            game_of_questions()
        elif quiz_choice == "GeoQuiz":
            game_of_questions()



elif authentication_status == False:
    st.error('Username/password is incorrect')
elif authentication_status == None:
    st.warning('Please enter your username and password')
