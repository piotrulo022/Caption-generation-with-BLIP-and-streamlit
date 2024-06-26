# utils
import logging
import os

# web modules
from pydantic import BaseModel

# database management
import mysql.connector

# models for caption generation
from transformers import pipeline




logging.basicConfig(level = logging.INFO) # logging module settings


################### Global variables ################### 
                                                       
MODEL_NAME = 'tarekziade/deit-tiny-distilgpt2' # default model

# Database authentication
DB_HOST = os.environ.get('DB_HOST')
DB_USER = os.environ.get('DB_USER')
DB_PASSWORD = os.environ.get('DB_PASSWORD')
DB_DATABASE = os.environ.get('DB_DATABASE')


################### Request/Response data models ################### 
class PredictURLRequestModel(BaseModel):
    """
    Expected data model for requests for prediction image from URL.
    """
    url: str
    push_db: bool = False

class DeleteRowRequestModel(BaseModel):
    """
    Delete request data model.
    """
    caption: str
    created_time: str

class PredictionResponseModel(BaseModel):
    """
    Prediction response data model.
    """
    prediction: str
    processing_time: str
    used_model_name: str


class ChangeModelResponseModel(BaseModel):
    result: str


class DeleteDataResponseModel(BaseModel):
    """
    Delete response data model.
    """
    result: str



################### Util functions ################### 

def img2db(image, caption)-> None:
    """
    Push instance (image, caption) to the database.
    
    """
    try:
        logging.info('Connecting to the database')
        with mysql.connector.connect(
                host=DB_HOST,
                user=DB_USER,
                password=DB_PASSWORD,
                database=DB_DATABASE
            ) as db_connection:
            logging.info('Connected successfully to the database!')
            
            db_cursor = db_connection.cursor()
            
            insert_query = "INSERT INTO Images (caption, model_used, image_file) VALUES (%s, %s, %s)"
            insert_data = (caption, MODEL_NAME, image)

            db_cursor.execute(insert_query, insert_data)
            db_connection.commit()
            
            logging.info('Image inserted successfully into the database')

    except mysql.connector.Error as e:
        logging.error(f'An error occurred while connecting to or interacting with the database: {e}')
        raise  # Re-raise the exception to let the caller handle it

    except Exception as e:
        logging.error(f'An unexpected error occurred: {e}')
        raise  # Re-raise the exception




def delete_data(caption:str, created_time: str):
    logging.info('Connecting to the database')
    try:
        conn = mysql.connector.connect(
                host=DB_HOST,
                user=DB_USER,
                password=DB_PASSWORD,
                database=DB_DATABASE
        )

    except mysql.connector.Error as e:
        logging.error(f'An error occured while connecting to the database\n{str(e)}')

        return f'failed to connect to database {str(e)}'
    
    try:
        cursor = conn.cursor()
        sql = "DELETE FROM Images WHERE caption = %s AND created_time = %s"
        cursor.execute(sql, (caption, created_time))
        
        conn.commit()

        cursor.close()
        conn.close()

        logging.info('Succesfully deleted row in the database!')

        return 'success' 
    except mysql.connector.Error as err:
        logging.error(f'An error occured while deleting row\n{str(e)}')

        return f"failed to delete row {str(err)}"


def delete_table():
    logging.info('Connecting to the database')

    try:
        conn = mysql.connector.connect(
                host=DB_HOST,
                user=DB_USER,
                password=DB_PASSWORD,
                database=DB_DATABASE
        )
    except mysql.connector.Error as e:
        logging.error(f'An error occured while connecting to the database\n{str(e)}')

        return f'failed to connect to database {str(e)}'
    try:
        cursor = conn.cursor()

        sql = "DELETE FROM Images;"
        cursor.execute(sql)
        
        conn.commit()

        cursor.close()
        conn.close()

        logging.info('Succesfully purged elements from table in the database!')

        return 'success' 
    except mysql.connector.Error as err:
        return f"failed to purge database {str(err)}"


