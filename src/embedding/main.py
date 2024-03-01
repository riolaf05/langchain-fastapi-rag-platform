import streamlit as st
from PyPDF2 import PdfFileReader
import streamlit_authenticator as stauth
# import json
from PIL import Image
import os
import platform
from dotenv import load_dotenv
from utils import AWSTexttract, LangChainAI, AWSS3, AWSTranscribe, DynamoDBManager, TextSplitter, EmbeddingFunction, QDrantDBManager
import yaml
from yaml.loader import SafeLoader
# from trubrics.integrations.streamlit import FeedbackCollector
import logging
load_dotenv('.env', override=True)
from mutagen.mp3 import MP3
from st_files_connection import FilesConnection
import datetime
from decimal import Decimal
from streamlit_cognito_auth import CognitoAuthenticator #https://github.com/pop-srw/streamlit-cognito-auth
# import subprocess


### VARIABLES #####
JOB_URI=os.getenv('JOB_URI')
S3_BUCKET=os.getenv('S3_BUCKET')
COGNITO_USER_POOL=os.getenv('COGNITO_USER_POOL')
COGNITO_CLIENT_ID=os.getenv('COGNITO_CLIENT_ID')
QDRANT_URL=os.getenv('QDRANT_URL')
COLLECTION_NAME=os.getenv('COLLECTION_NAME')
UPLOAD_FOLDER = r"C:\Users\ELAFACRB1\Codice\GitHub\chatgpt-summmary\uploads" if platform.system()=='Windows' else '/tmp' 
SQS_URL = os.getenv('SQS_URL')
### END VARIABLES #####


### INITIALIZATION #####
lang="ITA"
dynamodb_table_name = "chatgpt-summary-users"
langchain_client = LangChainAI()
s3_client=AWSS3('riassume-document-bucket')
conn = st.experimental_connection('s3', type=FilesConnection)
transcribe_s3client = AWSS3(S3_BUCKET)
transcribe = AWSTranscribe(JOB_URI)
textract = AWSTexttract()
dynamo_manager = DynamoDBManager(os.getenv('AWS_REGION'), dynamodb_table_name)
logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)
# chromaDbClient = ChromaDBManager() 
textSplitter = TextSplitter()

qdrantClient = QDrantDBManager(
    url=QDRANT_URL,
    port=6333,
    collection_name=COLLECTION_NAME,
    vector_size=1536,
    embedding=EmbeddingFunction('openAI').embedder,
    record_manager_url="sqlite:///record_manager_cache.sql"
)
### END INITIALIZATION #####



# Configurazione della pagina Streamlit
# st.set_page_config(page_title="Riassume: l'AI a supporto degli studenti", page_icon=":memo:", layout="wide")


### UTILS
def speech_to_text(job_name, language_code):
    job_name=transcribe.generate_job_name()
    data = transcribe.amazon_transcribe(JOB_URI, job_name, uploaded_mp3.name, language_code)
    logger.info("File audio transcribed!")
    return data

def read_pdf(file):
    '''
    Takes a file in input and return the read text
    '''
    text_input = []
    if file.type == "application/pdf":
        pdf_reader = PdfFileReader(file)
        for page in pdf_reader.pages:
            text = page.extractText()
            text_input.append(text.replace('\n', ' '))
    elif file.type == "image/jpeg" or file.type == "image/png" or file.type == "image/jpg":             
        img1 = Image.open(file)
        rgb_im = img1.convert('RGB') #to convert png to jpg
        text = textract.get_text(rgb_im).replace('\n', ' ')
        text_input.append(text.replace('\n', ' '))
    else:
        st.write("Formato non supportato.")
    return text_input 

def dynamodb_update_counter(username):
    get_key = {
            "username": username
        }
    update_expression = "SET n_images = :new_counter"
    expression_values = {
        ":new_counter": dynamo_manager.get_item(get_key)['Item']['n_images']+1
    }
    dynamo_manager.update_item(get_key, update_expression, expression_values)
### END UTILS

### Cognito login 
authenticator = CognitoAuthenticator(
    pool_id=COGNITO_USER_POOL,
    app_client_id=COGNITO_CLIENT_ID,
)
is_logged_in = authenticator.login()
username = authenticator.get_username()

# With Cognito login
if is_logged_in == True:

# #With no Cognito login
# if True:
    # username = 'test'

    tab1, tab2, tab3, tab4, tab5, tab6, tab7, tab8 = st.tabs(["AUDIO", "TESTO", "WEB", "VIDEO", "CHAT", "I MIEI RIASSUNTI", "FEED RSS", "IMAGES"])

    try: 
        USER_ID = dynamo_manager.get_item({"username": username})['Item']['username']
    except Exception as e:
        st.error("Login fallito. Riprova.")
        raise Exception("User not found!")
    
    with tab1:
        st.title("Benvenuto, " + username + "!")

        ########### Riasusmi da una registrazione ###########
        st.title("Sbobina una registrazione")
        st.write("Per favore converti il file in mp3. Presto saranno supportati nuovi formati audio.")
        uploaded_mp3 = st.file_uploader("Carica un file MP3", type=["mp3"])
        
        if uploaded_mp3 is not None:
            if st.button('Elabora il file audio'):
                    
                with open(os.path.join(UPLOAD_FOLDER, uploaded_mp3.name), 'wb') as f:
                    f.write(uploaded_mp3.read())
                # Convert m4a to mp3 #FIXME: doesn't work
                # if uploaded_mp3.name.endswith('.m4a'):
                #     CurrentFileName= os.path.join(UPLOAD_FOLDER, uploaded_mp3.name)
                #     FinalFileName = os.path.join(UPLOAD_FOLDER, uploaded_mp3.name[:-4] + '.mp3')
                #     try:
                #         subprocess.call(['ffmpeg', '-i', f'{CurrentFileName}', f'{FinalFileName}'])
                #     except Exception as e:
                #         print(e)
                #         print('Error While Converting Audio')
                #     uploaded_mp3.name = FinalFileName
                with st.spinner('Elaborazione, per favore attendi...'):
                    transcribe_s3client.upload_file(os.path.join(UPLOAD_FOLDER, uploaded_mp3.name),uploaded_mp3.name)
                    audio = MP3(os.path.join(UPLOAD_FOLDER, uploaded_mp3.name))
                    duration = audio.info.length
                    os.remove(os.path.join(UPLOAD_FOLDER, uploaded_mp3.name))

                    #Check user timeouts
                    get_key = {"username": username}
                    if dynamo_manager.get_item(get_key)['Item']['time_limit'] < 0:
                        st.error("Non hai più minuti disponibili per la versione di prova! Contattaci per continuare ad usare l'applicazione.")
                        raise Exception("User out of time!")
                    else:
                        ## Speech-to-text
                        logger.info("Transcribing audio file...")

                        ## Speech-to-text module
                        data = speech_to_text(uploaded_mp3.name, 'it-IT')

                        ## Summarize module
                        try:
                            # Riassunto dei testi
                            summarized_data = langchain_client.summarize_text(data)
                        
                            # Creazione lista argomenti
                            bullet_point_text = langchain_client.bullet_point_text(summarized_data)
                            logger.info("Audio file summarized!")

                        except Exception as e:
                            logger.error(e)
                            st.error("Il file audio è troppo lungo, stiamo lavorandop er aumentare il limite, nel frattempo prova a dividere il file audio in più parti, ci scusiamo per l'inconveniente.")
                            # raise Exception("Summarize timeout!")

                        try:
                            ## Create file testo
                            with open(os.path.join(UPLOAD_FOLDER, 'tmp.txt'), 'w', encoding='utf-8') as f:
                                f.write("Contenuo audio: \n\n")
                                f.write(summarized_data)
                                f.write('Argomenti principali trattati: \n\n')
                                f.write(bullet_point_text)
                                

                            ## Upload file testo
                            s3_client.upload_file(os.path.join(UPLOAD_FOLDER, 'tmp.txt'), username+'/'+"Argomenti audio "+str(uploaded_mp3.name)+".txt")
                            #Remove tmp file
                            os.remove(os.path.join(UPLOAD_FOLDER, 'tmp.txt')) 
                            st.success("Nota carica con successo!")

                            ## Update user timeouts
                            update_expression = "SET time_limit = :new_value"
                            expression_values = {":new_value": dynamo_manager.get_item(get_key)['Item']['time_limit']-Decimal(duration)}
                            dynamo_manager.update_item(get_key, update_expression, expression_values)
                        
                        except Exception as e:
                            logger.error(e)
                            st.error("Errore durante il caricamento della nota. Riprova o contatta l'assistenza.")

    with tab2:

        st.title("Benvenuto, " + username + "!")

        ########### Riasusmi da un libro ###########
        st.title("Lettura documenti (TXT, PDF, etc.)")

        st.write('Cosa vuoi fare?')
        option_1 = st.checkbox('Embedding')
        option_2 = st.checkbox('Riassunto')
        option_3 = st.checkbox('Parafrasi')
        

        option_embedding = st.selectbox(
            "Scegli la strategia di embedding",
            ("Fixed", "Parent Document", "Semantic"),
            index=None,
            placeholder="Seleziona strategia di embedding...",
            )

        # Definizione dell'area di drag and drop
        uploaded_files = st.file_uploader("Carica i file qui", type=["pdf"], accept_multiple_files=True)

        #1. Lettura PDF
        if st.button("Elabora i file testuali"):
            if uploaded_files is not None:
                with st.spinner('Elaborazione, per favore attendi...'):
                
                    for file in uploaded_files:
                        filename= file.name
                        text_input=read_pdf(file)
                                            
                    #Save response
                    string_input=" ".join(text_input) #join the array in a single string (summarize_text vuole una string in input)

                    #2. ELABORATION
                    if option_2:
                        #FIXME: DEBUGGARE IL METODO summarize_text, HA QUALCOSA CHE NON VA!!!
                        response = langchain_client.summarize_text(string_input) #TODO: portare fuori semantic_split_text!!
                        with open(os.path.join(UPLOAD_FOLDER, 'tmp.txt'), 'w', encoding='utf-8') as f:
                            f.write(response)

                        # Upload file testo
                        s3_client.upload_file(os.path.join(UPLOAD_FOLDER, 'tmp.txt'), username+'/'+"Argomenti documento "+str(filename)+".txt")
                        # Remove tmp file
                        os.remove(os.path.join(UPLOAD_FOLDER, 'tmp.txt'))
                        st.success("Nota carica con successo!")

                        ## Update user counter on DynamoDB
                        dynamodb_update_counter(username)

                    # if option_3:
                            #TODO

                    if option_1:
                        
                        #Create embeddings #FIXME: put it in async block ??? 
                        # collection = chromaDbClient.get_or_create_collection(COLLECTION_NAME)
                        if option_embedding:
                            if option_embedding == "Semantic":
                                splitted_docs=textSplitter.semantic_split_text(string_input) #split semantically
                                docs = textSplitter.create_langchain_documents(splitted_docs, {"source": "text"}) #create langchain documents from array of text
                            elif option_embedding == "Parent Document":
                                #TODO
                                docs=[]
                            elif option_embedding == "Fixed":
                                docs = textSplitter.create_langchain_documents(string_input, {"source": "text"}) #create langchain documents from array of text
                                docs=textSplitter.fixed_split(docs) #fixed split

                        try:
                            # chromaDbClient.store_documents(collection=collection, docs=docs)
                            qdrantClient.index_documents(docs)
                        except Exception as e:
                            logger.error(e)
                            st.error("Errore durante l'embedding. Connessione al DB fallita.")

                        st.success("Embedding caricato con successo!")
                    
                    
            else:
                st.write("Nessun file caricato.")


        ########### Text elaboration ###########
        st.title("Lettura handwritten")
        st.write("Usa la sezione sottostante e seleziona un'opzione dal menù a tendina per elaborare il testo.")

        text_name = st.text_input("Inserisci il titolo")

        # Definizione dell'area di testo
        text_input = st.text_area("Inserisci i tuoi appunti qui")

        # Definizione del menù a tendina
        choice = st.selectbox("Scegli un'opzione", ["riassumere", "parafrasare", "arricchire", "minuta"])

        # Definizione del pulsante di invio
        if st.button("Salva", disabled=False):
            with st.spinner('Elaborazione, per favore attendi...'):
                if choice == "riassumere":
                    res = langchain_client.summarize_text(text_input)
                    st.write(res)
                elif choice == "parafrasare":
                    res = langchain_client.paraphrase_text(text_input)
                    st.write(res)
                elif choice == "arricchire":
                    res = langchain_client.expand_text(text_input)
                    st.write(res)
                elif choice == "minuta":
                    res = langchain_client.draft_text(text_input)
                    st.write(res)
            
                #Save response
                with open(os.path.join(UPLOAD_FOLDER, 'tmp.txt'), 'w', encoding='utf-8') as f:
                    f.write(text_name)
                    f.write('\n\n')
                    f.write(res)
                ## Upload file testo
                s3_client.upload_file(os.path.join(UPLOAD_FOLDER, 'tmp.txt'), username+'/'+"Nuova nota - "+ (choice) + " - " + str(datetime.datetime.now())+".txt")
                #Remove tmp file
                os.remove(os.path.join(UPLOAD_FOLDER, 'tmp.txt'))
                st.success("Nota carica con successo!")

    with tab3:

        #TODO CREARE MANUALMENTE LE TABELLE DYNAMO DB, CREARE L'IAC PER LE TABELLE!!

        st.title("Benvenuto, " + username + "!")

        #### PAGINE WEB #######
        dynamodb_feed_manager = DynamoDBManager(os.getenv('AWS_REGION'), "rio-rag-webpages-table")
        get_key={"title": "web"}
        feed_list=dynamodb_feed_manager.get_item(get_key)['Item']['webpages']

        st.write("Inserisci una pagina web")
        new_web_page_url = st.text_input("Inserisci un url", key="5")
        if st.button("Salva", key="3"):
            update_expression = "SET webpages = :new_value"
            # feed_list=
            feed_list.append(new_web_page_url)
            expression_values = {":new_value": feed_list}
            dynamodb_feed_manager.update_item(get_key, update_expression, expression_values)
            st.success("Aggiunto")

        st.write("Elabora pagina web")
        if feed_list :
            option = st.selectbox(
                'Seleziona una pagina web da inserire..',
                 feed_list)

            if st.button("Elabora", key="4"):
                with st.spinner('Elaborazione, per favore attendi...'):
                    splitted_docs = langchain_client.webpage_loader(option)
                    qdrantClient.index_documents(splitted_docs)
                    st.success("Pagina web elaborata con successo!")

    with tab4:
        st.title("Benvenuto, " + username + "!")

        ########### Riasusmi dal testo di un video online ###########
        with st.form("my_form"):
            st.write("Inserisci l'url di un video con cui chattare")
            url = st.text_input('URL del video', "")

            # Every form must have a submit button.
            submitted = st.form_submit_button("Submit")
            if submitted:
                with st.spinner('Elaborazione, per favore attendi...'):
                    logger.info("Transcribing video url...")
                    try:
                        text = langchain_client.extract_video(url)
                        logger.info("Transcription completed...")
                    except Exception as e:
                        logger.error(e)
                        st.error("Errore durante la trascrizione del video. Riprova o contatta l'assistenza.")
            
                    ## Upload file testo
                    with open(os.path.join(UPLOAD_FOLDER, 'tmp.txt'), 'w', encoding='utf-8') as f:
                        f.write("Contenuo video: \n\n")
                        f.write(text)
                    s3_client.upload_file(os.path.join(UPLOAD_FOLDER, 'tmp.txt'), username+'/'+"Testo video.txt")
                    #Remove tmp file
                    os.remove(os.path.join(UPLOAD_FOLDER, 'tmp.txt')) 
                    logger.info("Transcriptin uploaded...")
                    st.success("Trascrizione video carica con successo!")
                   
    with tab5:

        st.title("Benvenuto, " + username + "!")

        st.write("COMING SOON")

    with tab6:

        st.title("Benvenuto, " + username + "!")

        ##### CONTENUTI CARICATI ######
        list_contents=s3_client.list_items(username)
        for content in list_contents:
            st.header(s3_client.read_metadata(content['Key'], 'name').replace(username+"/", ''))
            text = conn.read("riassume-document-bucket/"+content['Key'], input_format="text", ttl=600)
            st.write(text)
            st.write("")

    with tab7:

        st.title("Benvenuto, " + username + "!")

        #### FEED RSS #######
        dynamodb_feed_manager = DynamoDBManager(os.getenv('AWS_REGION'), "rio-rag-feed-table")
        get_key={"title": "feed_rss"}
        feed_list=dynamodb_feed_manager.get_item(get_key)['Item']['feeds']

        st.write("Inserisci un nuovo feed")
        new_feed_url = st.text_input("Inserisci un url")
        if st.button("Salva", key="1"):
            st.write('Why hello there')
            update_expression = "SET feeds = :new_value"
            # feed_list=
            feed_list.append(new_feed_url)
            expression_values = {":new_value": feed_list}
            dynamodb_feed_manager.update_item(get_key, update_expression, expression_values)
            st.success("Aggiunto")

        st.write("Elabora feed")
        if feed_list :
            option = st.selectbox(
                'Seleziona un feed dal quale leggere i dati..',
                 feed_list)

            if st.button("Elabora", key="2"):
                with st.spinner('Elaborazione, per favore attendi...'):
                    splitted_docs = langchain_client.rss_loader(option)
                    qdrantClient.index_documents(splitted_docs)
                    st.success("Feed elaborato con successo!")

    with tab8: 

        st.title("Benvenuto, " + username + "!")
        st.title("Multimodal video analysis")

# else:
#     st.error("Login fallito. Riprova.")
