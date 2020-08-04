# app.py

from fastapi import FastAPI
import logging, logging.config
import atexit

import chain 

logging.config.fileConfig('logging.conf')
app_logger = logging.getLogger('appLogger')

chain.load()
app = FastAPI()
app_logger.info('Starting...')

@app.get("/")
def read_root():
    return {"Hello": "World"}


@atexit.register
def on_exit():
    app_logger.info('Exiting...')
    app_logger.info('----------------------------')
    