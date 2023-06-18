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
import re
#import matplotlib.pyplot as plt
import ee
import folium
from streamlit_folium import st_folium
import geemap.colormaps as cm
import geemap.foliumap as geemap

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

credentials2 = service_account.Credentials.from_service_account_info(
    st.secrets["earth_engine_account"],
    scopes=['https://www.googleapis.com/auth/earthengine'])



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

    col1, col2 = st.columns(2)


    with col1:
        with st.expander("Map showing locations discussed in this assignment."):
            #df = pd.DataFrame({
            #'lat': [30.961653],
            #'lon': [46.105126]
            #})
            #Display the map
            #st.map(df)
            # Define the initial viewport
            view_state = pdk.ViewState(
             latitude=32.7938135,
             longitude=38.4948285,
             zoom=4
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
                'Latitude': [32.542233, 30.961653, 35.158333, 25.727851, 31.859, 36.8266, 36.229444],
                'Longitude': [44.420936, 46.105126, 33.891111, 32.610801, 34.919, 40.0396, 43.403333],
                'tooltip': [
                    "<img src='http://media.britishmuseum.org/media/Repository/Documents/2014_11/12_20/f8d09bf3_a156_4a95_befc_a3e101544e67/preview_00129985_001.jpg' width='300px' height='300px'><div style='word-wrap: break-word; width: 300px;'><br><b>Cuneiform tablet found near Babylon with the rules of the Royal Game of Ur, 2nd century BC. British Museum.</b>",
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

    with st.expander("Earth Engine Test"):

        #ee.Authenticate()
        # code comes from: https://medium.com/@tahjudil.witra/deploy-your-google-earth-engine-gee-analysis-into-a-web-app-streamlit-a7841e35b0d8

        # begin code
        ee.Initialize(credentials2)

        def add_ee_layer(self, ee_image_object, vis_params, name):
            """Adds a method for displaying Earth Engine image tiles to  folium map."""
            map_id_dict = ee.Image(ee_image_object).getMapId(vis_params)
            folium.raster_layers.TileLayer(
                tiles=map_id_dict['tile_fetcher'].url_format,
                attr='Map Data &copy; <a href="https://earthengine.google.com/">Google Earth Engine</a>',
                name=name,
                overlay=True,
                control=True
            ).add_to(self)

        # Add Earth Engine drawing method to folium.
        folium.Map.add_ee_layer = add_ee_layer

        #st.session_state.Map = folium.Map()

        # Import the MODIS land cover collection.
        lc = ee.ImageCollection('MODIS/006/MCD12Q1')
        # Initial date of interest (inclusive).
        i_date = '2017-01-01'
        # select one image
        lc_img = lc.select('LC_Type1').filterDate(i_date).first()

        @st.cache_data
        def load_data():
            # Import the MODIS land cover collection.
            lc = ee.ImageCollection('MODIS/006/MCD12Q1')
            # Initial date of interest (inclusive).
            i_date = '2017-01-01'
            # select one image
            lc_img = lc.select('LC_Type1').filterDate(i_date).first()
            return lc_img

        # Check if 'Map' already exists in session_state
        # If not, then initialize it
        if 'Map' not in st.session_state:
            st.session_state.Map = folium.Map()

        # Add the Earth Engine layer to the map.
        vis_params = {
            'min': 0,
            'max': 17,
            'palette': ['aec3d4', '152106', '225129', '369b47', '30eb5b', '387242', '6a2325', 'c3aa69', 'b76031', 'd9903d', '91af40', '111149'],
            'bands': ['LC_Type1']
        }
        st.session_state.Map.add_ee_layer(load_data(), vis_params, 'MODIS Land Cover')

        rendered_map = st_folium(st.session_state.Map)
        # end code








    #with st.expander("Article about the history of the Royal Game of Ur from the New York Metropolitan Museum:"):
        #screenshot_url = "https://raw.githubusercontent.com/Dr-Hutchinson/Royal-Game-of-Ur/main/met_article_screenshot.png"
    #    st.markdown(
    #        "<a href='https://www.metmuseum.org/exhibitions/listings/2014/assyria-to-iberia/blog/posts/twenty-squares' target='_blank'><img src='https://raw.githubusercontent.com/Dr-Hutchinson/Royal-Game-of-Ur/main/met_article_screenshot.png'></a>",
    #        unsafe_allow_html=True
    #    )
        #st.image(screenshot_url)
    #    st.write("Click on the image above to open the [article](https://www.metmuseum.org/exhibitions/listings/2014/assyria-to-iberia/blog/posts/twenty-squares) in a new tab.")

    #with st.expander('Video about Irving Finkel of the British Museum, who discovered the rules for the Royal Game of Ur:'):
    #    video_url = "https://youtu.be/wHjznvH54Cw"
    #    st.video(video_url)

    #with st.expander('Game board for the Royal Game of Ur from the British Museum'):
    #    image_url_0 = "https://media.britishmuseum.org/media/Repository/Documents/2017_8/17_15/d63be997_915e_4d23_8bd6_a7d200fd2537/mid_WCO24357__1.jpg"
    #    st.image(image_url_0)
    #    st.write("[Link](https://www.britishmuseum.org/collection/object/W_1928-1009-378) to the catalog entry for the object in the British Musuem.")

    #with st.expander('Cuniform Tablet featuring rules for the Royal Game of Ur from the British Museum:'):
    #    image_url = "http://media.britishmuseum.org/media/Repository/Documents/2014_11/12_20/f8d09bf3_a156_4a95_befc_a3e101544e67/preview_00129985_001.jpg"
    #    st.image(image_url)
    #    st.write("[Link](https://www.britishmuseum.org/collection/object/W_Rm-III-6-b) to the catalog entry for the object in the British Musuem.")

    #with st.expander("Play the Royal Game of Ur:"):
    #    components.iframe("https://royalur.net/", width=800, height=600)

    #with st.expander("Test Space for Prompt Game 0"):


    # begin chatbot
    # based on: https://github.com/PradipNichite/Youtube-Tutorials/blob/main/Langchain%20Chatbot/utils.py

    with col2:
        with st.expander("Talk with ChatGPT about the Royal Game of Ur."):

            #def geoquiz():

            #    st.title("GeoQuiz")

            #    st.header("Placeholder")

            #    st.header("Chatbot Interface:")

            #    colored_header(
            #        label="",
            #        description="\n\n",
            #        color_name="violet-70",
            #    )

            #    sh1 = gc.open('ur_quiz_questions')
            #    wks1 = sh1[0]
            #    df_quiz_source = wks1.get_as_df()

                # Randomly sample questions from the DataFrame
            #    df_sample = df_quiz_source.sample(n=3)  # replace 10 with the number of questions you want in the quiz

                # Store the sampled DataFrame in the session state
            #    st.session_state.df_sample = df_sample

                # Create a form
            #    with st.form(key='quiz_form'):
                    # Loop through the sampled DataFrame and display questions
            #        for index, row in df_sample.iterrows():
            #            st.write(f"Question {row['question_number']}: {row['question']}")

                        # Check if it's a True/False question
            #            if pd.isnull(row['option_3']):
            #                options = ['True', 'False']
            #            else:
            #                options = [row['option_1'], row['option_2'], row['option_3'], row['option_4'], row['option_5']]

                        # Display options as radio buttons and store the user's answer in the session state
                        # Use different keys for st.session_state and st.radio
            #            st.session_state[f"answer_{row['question_number']}"] = st.radio("Select your answer:", options, key=str(row['question_number']))

                    # Add a submit button to the form
            #        if st.form_submit_button(label='Submit Answers'):
            #            st.session_state.submitted = True

                # Function to check the answers
            #    def check_answers():
            #        for question_number in st.session_state.df_sample['question_number']:
            #            user_answer = st.session_state[f"answer_{question_number}"]
            #            correct_answer = st.session_state.df_sample.loc[st.session_state.df_sample['question_number'] == question_number, 'answer'].values[0]
            #            if user_answer == str(correct_answer):
            #                st.write(f"Question {question_number}: Correct!")
            #            else:
            #                st.write(f"Question {question_number}: Incorrect. The correct answer is: " + str(correct_answer))

                # Check the answers when the submit button is clicked
            #    if 'df_sample' in st.session_state and st.session_state.submitted:
            #        check_answers()
                #if st.button('Reset Chat History'):
                    #st.session_state['requests'] = []
                    #st.session_state['responses'] = ["How can I assist you?"]
                    #st.session_state['sources'] = []
                    #st.session_state['token_count'] = []
                    #st.experimental_rerun()

                #if 'token_count' not in st.session_state:
                    #st.session_state['token_count'] = []

                #if 'responses' not in st.session_state:
                #    st.session_state['responses'] = ["How can I assist you?"]

                #if 'requests' not in st.session_state:
                #    st.session_state['requests'] = []

                #llm = ChatOpenAI(model_name="gpt-3.5-turbo", openai_api_key=st.secrets["openai_api_key"])

                #if 'buffer_memory' not in st.session_state:
                #    st.session_state.buffer_memory=ConversationBufferWindowMemory(k=1,return_messages=True)

                #def get_conversation_string():
                #    conversation_string = ""
                #    for i in range(len(st.session_state['responses'])-1):
                #        conversation_string += "Human: "+st.session_state['requests'][i] + "\n"
                #        conversation_string += "Bot: "+ st.session_state['responses'][i+1] + "\n"
                #    return conversation_string

                #prompt = "Compose a response based on the user input."

                #system_msg_template = SystemMessagePromptTemplate.from_template(template=prompt)

                #human_msg_template = HumanMessagePromptTemplate.from_template(template="{input}")

                #prompt_template = ChatPromptTemplate.from_messages([system_msg_template, MessagesPlaceholder(variable_name="history"), human_msg_template])

                #conversation = ConversationChain(memory=st.session_state.buffer_memory, prompt=prompt_template, llm=llm, verbose=True)

                # token counting script
                #encoding = tiktoken.encoding_for_model("gpt-3.5-turbo")

                #def count_tokens(chain, query):
                #    with get_openai_callback() as cb:
                #        result = chain.predict(input=query)
                #        print(f'Spent a total of {cb.total_tokens} tokens')
                #        st.session_state.token_count.append(cb.total_tokens)
                #        return result, cb.total_tokens

                #token_counts = []

                # container for chat history
                #response_container = st.container()
                # container for text box
                #textcontainer = st.container()

                #with textcontainer:
                #    with st.form(key='chat_form'):
                #        query = st.text_input("Enter your question to the chatbot here: ", key="input")
                #        submit_button = st.form_submit_button(label='Submit Question')
                #        if submit_button and query is not None and query != "":
                #            with st.spinner("Getting Response..."):


                #                conversation_string = get_conversation_string()

                #                response, tokens = count_tokens(conversation, f"Here are your data sources:\n {conversation_string} \n\Respond in the manner requested by the user. Extract only the relevant details from the data sources, and avoid repetition. Use direct quotes from these relevant details to answer this user input:\n\n{query}\n\nIf you don't have relevant information from the sources to answer that, say so.")

                #                st.write("Token Count= " + str(st.session_state.token_count))




            def game_of_questions():

                st.title("Placeholder")



                colored_header(
                    label="",
                    description="\n\n",
                    color_name="violet-70",
                )

                if st.button('Reset Chat History'):
                    st.session_state['requests'] = []
                    st.session_state['responses'] = ["Hello, I'm Clio! Enter /start to begin the assignment!"]
                    st.session_state['sources'] = []
                    st.session_state['token_count'] = []
                    st.experimental_rerun()

                if 'token_count' not in st.session_state:
                    st.session_state['token_count'] = []

                token_count = []
                st.write(st.session_state.token_count)

                if 'responses' not in st.session_state:
                    st.session_state['responses'] = ["Hello, I'm Clio! Enter /start to begin the assignment!"]

                if 'requests' not in st.session_state:
                    st.session_state['requests'] = []

                llm = ChatOpenAI(model_name="gpt-3.5-turbo-16k", openai_api_key=st.secrets["openai_api_key"])

                if 'buffer_memory' not in st.session_state:
                    st.session_state.buffer_memory=ConversationBufferWindowMemory(k=4,return_messages=True)

                # ORIGINAL - DON'T DELETE
                #def get_conversation_string():
                #    conversation_string = ""
                #    for i in range(len(st.session_state['responses'])-1):
                #        conversation_string += "User: "+st.session_state['requests'][i] + "\n"
                #        conversation_string += "Clio: "+ st.session_state['responses'][i+1] + "\n"
                #    return conversation_string

                def get_conversation_string():
                    conversation_string = ""
                    for i in range(len(st.session_state['responses'])-1):
                        # Remove the sections enclosed in < > after "Answers:" and "Initial Thought:"
                        revised_response = re.sub(r'<Answers:.*?>', '', st.session_state['responses'][i+1])
                        revised_response = re.sub(r'<Initial Thought:.*?>', '', revised_response)

                        # Add the request and the revised response to the conversation string
                        conversation_string += "Human: "+st.session_state['requests'][i] + "\n"
                        conversation_string += "Bot: "+ revised_response + "\n"
                    return conversation_string

                def pull_random_row():
                    """Pull a random row from a Google Sheet called 'ur_questions'"""
                    # Open the Google Spreadsheet using its name
                    sheet = gc.open('ur_quiz_questions')
                    # Select Sheet1
                    wks = sheet.sheet1
                    # Get all values of the first column
                    column_values = wks.get_col(1)
                    # Randomly select a value
                    random_value = random.choice(column_values)
                    return random_value

                def upload_value():
                    """Upload a numerical value of 1 to row 1/column 1 of a Google Sheet called 'ur_data'"""
                    # Open the Google Spreadsheet using its name
                    sheet = gc.open('ur_data')
                    # Select Sheet1
                    wks = sheet.sheet1
                    # Update the value at row 1, column 1
                    wks.update_value('A1', 1)

                functions = [
                    {
                        "name": "pull_random_row",
                        "description": "Pull a random row from a Google Sheet called 'ur_questions'",
                        "parameters": {},
                    },
                    {
                        "name": "upload_value",
                        "description": "Upload a numerical value of 1 to row 1/column 1 of a Google Sheet called 'ur_data'",
                        "parameters": {},
                    },
                ]



                prompt = ("""
                # begin prompt\n
                Hello. You are an AI tutor with expertise on the Ziggurat of Ur and its place within the broader history of ancient Mesopotamia. Your mission is to engage users in dialogue and pose questions about a reading about the Ziggurat of Ur. Your dialogue should seek to fulfill the stated learning objectives below and meet the dialogue style guidelines.\n\n
                Here is the reading: \n\n
                # begin reading\n
                The Ziggurat of Ur, an architectural marvel of the ancient world, stands as a testament to the power, ingenuity, and cultural richness of the civilization that built it. Constructed around 2100 B.C.E. under the rule of King Ur-Nammu, the ziggurat was dedicated to the moon goddess Nanna, the patron deity of Ur. This massive structure, rising from the flat landscape, was the highest point in the city, serving as a beacon for travelers and a focal point for the city's inhabitants.\n\n
                Architecturally, the ziggurat was a marvel of engineering. Its core was made of mud brick, covered with a protective layer of baked bricks laid with bitumen, a naturally occurring tar. The structure was tiered, with each level smaller than the one below, creating a stepped pyramid. The architects incorporated functional elements into the design, including holes through the baked exterior layer to allow water to evaporate from its core, and built-in drainage systems on the terraces to carry away the winter rains. This attention to detail and practicality speaks to the advanced engineering skills of the people of Ur.\n\n
                Religiously, the Ziggurat of Ur was the city's spiritual heart. It was a place of worship, a home for the city's patron deity, and a site for important religious rituals. The ziggurat's towering presence would have served as a constant reminder of the city's devotion to Nanna. This religious significance is mirrored in the Royal Game of Ur, which was found in the Royal Cemetery of Ur and may have held a significant role in the city's religious or ritualistic practices.\n\n
                Politically, the construction of the Ziggurat of Ur reflects the power and authority of the city's rulers. The ability to mobilize the resources and labor necessary to build such a massive structure demonstrates the political strength of the ruling class. The ziggurat, visible from miles around, would have served as a symbol of the city's power and the might of its rulers.\n\n
                Socially, the ziggurat reinforced the city's social hierarchy. Its grandeur and prominence would have been a constant reminder of the social order, with the city's rulers and gods at the top. The ziggurat's role as a center for religious, administrative, and possibly even economic activities would have made it a hub of city life, reflecting the city's social structure.\n\n
                Historically and culturally, the Ziggurat of Ur is a significant artifact that sheds light on the achievements of the Ancient Near East. Its construction demonstrates advanced architectural and engineering skills, while its role in the city's religious and social life speaks to the cultural richness of this civilization. The connection to the Royal Game of Ur further underscores this cultural richness, offering insights into the city's religious practices, social structure, and material culture.\n\n
                In conclusion, the Ziggurat of Ur and the Royal Game of Ur are intertwined in their reflection of the city's religious, political, social, and cultural life. The game, found in the nearby royal tombs, may have been used in rituals or as a symbolic object, much like the ziggurat was a stage for religious rituals. Moreover, both the game and the ziggurat reflect the city's wealth and the craftsmanship of its artisans, providing insights into the material culture of Ur. Both artifacts offer valuable insights into the civilization that created them, revealing a society marked by advanced engineering skills, complex social structures, and a rich cultural and religious life.
                # end reading\n\n
                Here are the learning objectives for this reading:\n\n
                # begin learning objectives\n\n
                Recognize the architectural and engineering features of the Ziggurat of Ur.\n
                Understand the role of the Ziggurat of Ur in the religious life of the city.
                Comprehend how the Ziggurat of Ur reflects the political structure of Ur.
                Demonstrate an appreciation for how the Ziggurat of Ur reflects the social structure of the city\n
                Provide an accurate statement reflecting on the historical and cultural significance of the Ziggurat of Ur.\n
                Establish connections between the Ziggurat of Ur and the Royal Game of Ur.\n
                # end learning objectives\n\n
                Here is the dialogue style guidelines:\n\n
                # begin dialogue style guidelines\n
                1. Agent Identity: You are Clio, a historically-minded learning companion. Your job is to engage in a dialogue to assess student understanding of a reading. You will employ your theory of mind skills to understand the user’s meaning and intention.\n
                2. Opening Statement: The dialogue begins with this statement: I'm Clio, your AI tutor for assessing your understanding of the Ziggurat of Ur and its historical significance. We're going to have a dialogue where I ask you a series of questions. If you get the question right we'll move on to the next question. If your response is inaccurate or only partially accurate then I'll ask follow-ups to help you think about how to find the answer. For each accurate answer you get 1 point. For each partially accurate answer you get half a point. Inaccurate answers don’t receive points. Our dialogue ends when all five questions have been posed. A score of 3 successfully earns credit for the assessment. However, if you score all five correctly you gain a special achievement.\n
                3. Dialogue Style Modes: You have the following dialogue style modes: question-posing, user-response-evaluation, score-keeping, and command. After the Opening Statement, you will evaluate the state of the dialogue to determine which mode in which to engage.Here are the different dialogue modes:\n
                3A: Question-Posing Mode: In this mode you will set up a question to establish a new phase in the dialogue. Here is your approach to this mode:\n
                3A-1. Question Formation: At the start of the mode, list a learning objective to assess and then compose a single question for the user. Questions should not only test the user's factual recall but also their comprehension, application, analysis, synthesis, and evaluation abilities. Your questions should be open-ended but specific enough that students can use the reading to answer them. Vary the types of questions you ask to stimulate progressively more advanced levels of cognitive engagement in the manner of Bloom's Taxonomy.\n
                3A-2. Answer Identification: Based on your question, compose suitable answers based on information in the reading. These answers will inform your evaluation of user accuracy in the user-response-mode. Don't worry about the user seeing this - I have set up a parsing program to hide this section from users. Always be sure to include this section.\n
                3B: User-Response-Evaluation Mode: In this mode you will evaluate the user response against the question/answers output prepared in Question-Posing mode.  Here is your approach to this mode:\n
                3B-1: Initial Thought Statement: Based on the user response, generate an initial thought assessing the accuracy of the user's response against the answers generated in the Answer Identification step. If the answer is inaccurate, make a prediction about how to steer the dialogue to help the user towards an accurate answer, but without revealing the answer itself. In posing this response, examine anything in the current dialogue that would help improve your prediction.\n
                3B-2: Accuracy Statement: Based on your initial thought, produce a statement about the accuracy of the user's response. If the response is accurate, affirm the users correctness and move on to the next question via the Question Posing mode. If the response is inaccurate or partially accurate, continue in this mode and use your initial thought to generate an appropriate response to the user input that steers the user towards the right answer and another round in this mode. Keep your responses concise and specific, and if the user wants to end the conversation or skip the question, always comply.\n
                3C: Score-Keeping Mode: In this mode you will keep a score of how many questions students have gotten correct. Score Keeping Mode should occur at the conclusion of every instance of the User-Response-Evaluation Mode. Use the Score Keeping Rules in keeping score in this mode.\n
                3C-1: Score Keeping Rules: Based on the user response, generate a score for the user’s accuracy thus far in the dialogue. Each accurate response gets a score of 1. Partially accurate
            scores get a score of .5. Inaccurate responses get a score of 0.  The user's current score is then measured against the score goals for the dialogue.\n
                3D. Command Mode: In this mode you will take an action based on user invocation of a command. These commands resemble Discord bot commands. Here is your approach to this  mode:
            3D-1: Command Mode Rules: Users possess a range of commands that when used change the normal course of a dialogue. Those commands are represented in the form “/<x_command>. Here are the command options:\n
                3D-2: Start Chat: Your dialogue begins when a user inputs /start”. When initiated, start the dialogue with the Opening Statement. After your Opening Statement, transition into User Interest Mode before moving onto Question-Posing Mode.\n
                3D-3: End Chat: Your dialogue ends when a user inputs “/end”. When initiated conclude the dialogue with the Closing Statement.\n
                3D-4: Appeal: Your dialogue is interrupted when the user wishes to appear the results of the most recent question assessment by inputting “/appeal x”, x representing the question. Double check whether the score generated during the Score Keeping Mode accurately reflects the evaluation offered by Initial Thought, and whether the total score is accurate based on the chat history.\n
                4. Overall Output Structure: Here is the expected output for a given user response. Be sure to follow this structure when composing replies.\n\n
                # begin overall output structure\n
                <begin Question-Posing Mode>\n
                Learning Objective: <content of learning objective>\n
                Question x: <question informed by the learning objective>\n
                <end Question-Posing Mode>\n\n
                User: <user reply>\n\n
                <begin User-Response-Evaluation mode>\n
                Initial Thought: <initial evaluation of user reply>\n
                Response to User: <response to user based on Initial Thought>\n
                <end User-Response-Evaluation mode>\n\n
                <begin Score-Keeping mode. Always include to follow User-Response-Evaluation mode>\n
                Score: <information on the user score and progress towards assignment goal>\n
                <end Score-Keeping mode>\n\n
                <begin Question-Posing Mode>\n
                User: if <user reply> is </command>:\n
                run command\n
                else:\n
                <begin User-Response-Evaluation mode>\n
                # end overall output structure\n
                5. Example Dialogue: Here is an example dialogue. Mode switches are indicated in <> for example purposes, but shouldn't be included in your output. However, pay attention to the rest of the output to see how Clio's responses are formatted. Seek to do the same for your responses.\n\n
                # begin example dialogue\n
                <begin Opening Statement>\n
                <begin Question-Posing Mode>\n
                Learning Objective: Recognize the architectural and engineering features of the Ziggurat of Ur.\n\n
                Question 1: What materials were used in the construction of the Ziggurat of Ur, and how did these materials reflect on the resources and skills of those who built it?\n\n
                Answers: The Ziggurat of Ur was built with a core of mud brick, covered with a protective layer of baked bricks laid with bitumen, a naturally occurring tar. The baked exterior had holes to allow water to evaporate from its core, and there were built-in drainage systems on the terraces. These details demonstrate the advanced architectural and engineering skills of the people of Ur.\n\n
                <end Question-Posing Mode>\n\n
                User: The Ziggurat of Ur was constructed using mud bricks, which were then covered with baked bricks. Bitumen was also used as a sort of adhesive.\n\n
                <begin User-Response-Evaluation mode>\n
                Initial Thought: The user has correctly identified the main materials used in the construction of the Ziggurat of Ur. However, they didn't mention the engineering features like the drainage systems and the evaporative holes.\n\n
                Response to User: That's right! The Ziggurat of Ur was indeed built with a core of mud brick, which was then covered with a protective layer of baked bricks. Bitumen, a naturally occurring tar, was used as an adhesive. Can you also mention some of the architectural features that reflect the advanced engineering skills of the people of Ur?\n\n
                <end User-Response-Evaluation mode>\n\n
                <begin Score-Keeping mode>\n
                Score: You currently have a score of 0.5 because your response was partially accurate. By providing additional information about the engineering features of the Ziggurat, you could earn the full point for this question.\n
                <end Score-Keeping mode>\n\n
                <begin Question-Posing Mode>\n
                # end example dialogue\n\n
                # end dialogue style guidelines\n\n
                Begin your dialogue assessing student knowledge when the user begins the chat with /start. Be sure to complete each part of the dialogue with all the required modes appropriate to that section of the dialogue.\n\n"""
                )





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
                        st.session_state.token_count.append(cb.total_tokens)
                        return result, cb.total_tokens

                #token_counts = []

                # container for chat history
                response_container = st.container()
                # container for text box
                textcontainer = st.container()


                with textcontainer:
                    with st.form(key='chat_form'):
                        query = st.text_area("Enter your question to Clio here: ", key="input")
                        submit_button = st.form_submit_button(label='Submit Question')
                        if submit_button and query is not None and query != "":
                            with st.spinner("Getting Response..."):

                                conversation_string = get_conversation_string()
                                response, tokens = count_tokens(conversation, f"""{query}\n""")

                                #user_dialogue = re.findall(r'User: (.*)', response)
                                #clio_dialogue = re.findall(r'Clio: (.*)', response)
                                #learning_objective = re.findall(r'Learning Objective: (.*)', response)
                                #question = re.findall(r'Question \d+: (.*)', response)
                                #score = re.findall(r'Score: (.*)', response)

                                st.write("Token Count= " + str(st.session_state.token_count))


                                st.session_state.requests.append(query)
                                st.session_state.responses.append(response)



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
                            'name': 'chat_history_zig.txt',
                            'parents': ['1p2ZUQuSclMvFwSEQLleaRQs0tStV_-Mu']
                        })
                        response = request.execute()
                        # Print the response
                        st.write("Quiz Submitted.")


            quiz_choice = st.selectbox("Choose chatbot type", ['Game of Questions', 'GeoQuiz'])

            if quiz_choice == "Game of Questions":
                game_of_questions()
            elif quiz_choice == "GeoQuiz":
                geoquiz()



elif authentication_status == False:
    st.error('Username/password is incorrect')
elif authentication_status == None:
    st.warning('Please enter your username and password')
