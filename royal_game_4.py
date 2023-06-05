import streamlit as st
import streamlit.components.v1 as components
from streamlit_chat import message
import streamlit_authenticator as stauth
from langchain import OpenAI, ConversationChain, LLMChain, PromptTemplate
from langchain.memory import ConversationBufferWindowMemory
from langchain.document_loaders import YoutubeLoader, BSHTMLLoader, WikipediaLoader
from langchain.indexes import VectorstoreIndexCreator
from langchain.text_splitter import CharacterTextSplitter
from langchain.chat_models import ChatOpenAI
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
        # Define the data for the marker
        data = pd.DataFrame({
            'Latitude': [30.961653],
            'Longitude': [46.105126]
        })
        # Define the icon data
        icon_data = {"url":"https://img.icons8.com/plasticine/100/000000/marker.png", "width":128, "height":128, "anchorY":128}
        # Add the icon data to the dataframe
        data["icon"] = [icon_data]
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
        tooltip = {
            "html": "<b>Site of the Mesoptomimian city of Ur.</b>",
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

    if 'history' not in st.session_state:
        st.session_state.history = ""

    with st.expander("Chat about the Royal Game of Ur"):
        #if 'history' not in st.session_state:
            #st.session_state.history = ""
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
        template = """You are an educational chatbot with access to various data sources on the Royal Game of Ur. When given a user question you will be supplied with information from those sources. Based on those sources, compose an insightful and accurate answer based on those sources, and cite the source of the information used in the answer.
        ...
        {history}
        Human: {human_input}
        Assistant:"""
        prompt = PromptTemplate(
         input_variables=["history", "human_input"],
         template=template
        )
        chatgpt_chain = LLMChain(
         llm=ChatOpenAI(model_name='gpt-3.5-turbo', temperature=0),
         prompt=prompt,
         verbose=True,
         memory=ConversationBufferWindowMemory(k=2),
        )
        #st.write(f"Debug: {st.session_state}")  # Debug print statement
        #st.session_state.history += f"Assistant: {response}\\n"
        message("Messages from the bot", key="message_0")
        message("Your messages", is_user=True, key="message_1")
        #if st.session_state.history:
            #for i, line in enumerate(st.session_state.history.split('\n')):
                #if line.startswith('Human:'):
                #    message(line[6:], is_user=True, key=f"message_{i+2}")
                #elif line.startswith('Assistant:'):
                #    message(line[10:], key=f"message_{i+2}")
                #elif line.startswith('YouTube data:'):
                    #message(line[13:], key=f"message_{i+2}")
                #elif line.startswith('Wikipedia data:'):
                    #message(line[16:], key=f"message_{i+2}")
                #elif line.startswith('Met Museum data:'):
                    #message(line[16:], key=f"message_{i+2}")

        if st.session_state.history:
            for i, line in enumerate(st.session_state.history.split('\\n')):
                if line.startswith('Human:'):
                    message(line[6:], is_user=True, key=f"message_{i+2}")
                elif line.startswith('Assistant:'):
                    message(line[10:], is_user=False, key=f"message_{i+2}")  # Pass is_user=False for the assistant's messages
        user_input = st.text_input("Enter your message:")

        if st.button("Send"):

            if user_input:
                st.session_state.history += f"Human: {user_input}\\n"
                # Perform semantic search
                results_df = embeddings_search(user_input, df, n=5)
                history = st.session_state.history
                for i, row in results_df.iterrows():
                    history += f"Assistant: {row['combined']}\\n"
                #for i, row in results_df.iterrows():
                    #st.session_state.history += f"Assistant: {row['combined']}\\n"
                    #st.session_state.history += f"Similarity score: {row['similarities']}\\n"
                result = chatgpt_chain.generate([{"history": history, "human_input": user_input}])
                # Extract the generated text from the Generation objects
                response = result.generations[0][0].text
                # Add the response to the chat history
                st.session_state.history += f"Assistant: {response}\\n"
                st.text_input("Enter your message:", value="", key="user_input")
                now = dt.now()
                #@st.cache(ttl=6000)

                st.experimental_rerun()

        if st.button("Submit Quiz"):
            now = dt.now()

            formatted_history = f"User: {username}\nTime: {now}\n" + st.session_state.history.replace('\\n', '\n\n')
            with open('chat_history.txt', 'w') as f:
                f.write(formatted_history)
            credentials = Credentials.from_service_account_info(st.secrets["gcp_service_account"])
            # Build the service
            drive_service = build('drive', 'v3', credentials=credentials)
            # Create a MediaFileUpload object and specify the MIME type of the file
            media = MediaFileUpload('chat_history.txt', mimetype='text/plain')
            # Call the drive service files().create method to upload the file
            request = drive_service.files().create(media_body=media, body={
                'name': 'chat_history.txt',  # name of the file to be uploaded
                'parents': ['1p2ZUQuSclMvFwSEQLleaRQs0tStV_-Mu']  # id of the directory where the file will be uploaded
            })
            # Execute the request
            response = request.execute()

            # Print the response
            st.write("Quiz Submitted.")

        if st.button('Reset Chat History'):
            st.session_state.history = ""
            st.experimental_rerun()

elif authentication_status == False:
    st.error('Username/password is incorrect')
elif authentication_status == None:
    st.warning('Please enter your username and password')
