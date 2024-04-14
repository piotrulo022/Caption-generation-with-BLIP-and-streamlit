import streamlit as st

import mysql.connector

from PIL import Image
from io import BytesIO

import requests
import os
from time import time 


API_URL = os.environ.get('API_URL')
DB_HOST = os.environ.get('DB_HOST')
DB_USER = os.environ.get('DB_USER')
DB_PASSWORD = os.environ.get('DB_PASSWORD')
DB_DATABASE = os.environ.get('DB_DATABASE')

SUPPORTED_MODELS = ['tarekziade/deit-tiny-distilgpt2', 'Salesforce/blip-image-captioning-base', 'llava-hf/llava-1.5-7b-hf', 'keras-io/ocr-for-captcha', 'noamrot/FuseCap_Image_Captioning']




############## UTILS FOR database_preview.py ############## 
def get_data():
    db_connection = mysql.connector.connect(
                host=DB_HOST,
                user=DB_USER,
                password=DB_PASSWORD,
                database=DB_DATABASE
                )
    db_cursor = db_connection.cursor()
    
    query = "SELECT * FROM Images;"
    db_cursor.execute(query)

    data = db_cursor.fetchall()

    colnames = [column[0] for column in db_cursor.description]


    return {'data': data,
            'colnames': colnames}

def decode_image(file):
    image = Image.open(BytesIO(file)).convert('RGB')

    return image


def delete_row(created_time, caption):
    requests.delete(url = API_URL + '/delete_row/', json = {'created_time': created_time,
                                                              'caption': caption} )

def delete_all_rows():
    requests.delete(url = API_URL + '/purge_database/')

############## UTILS FOR database_preview.py ############## 

def model_card(name):
    st.title("Model card")

    url = "https://huggingface.co/" + name

    st.components.v1.html(
        f'<iframe src="{url}" width="100%" height="600" frameborder="0" scrolling="auto"></iframe>',
        height=800
    )


def change_model():
    with st.spinner(f'Changing model....'):
        response = requests.post(API_URL + '/change_model/', params = {'name': st.session_state["selected-model"]})

        if response.status_code == 200:
            mess = st.success(f"Succesfully switched model to {st.session_state['selected-model']}", icon="✅")
        else:
            mess = st.error("Failed to switch model.", icon="🚨") 
        time.sleep(2)
        mess.empty()




############## UTILS FOR database_preview.py ############## 

def check_backend_status(url):
    """
    This funcion checks wheter URL is available and is used to monitor FastAPI container status.
    """
    try:
        response = requests.get(url)
        if response.status_code == 200:
            return True
        else:
            return False
    except:
        return False
    