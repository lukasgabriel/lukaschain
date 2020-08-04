# app.py

from typing import Optional
from fastapi import FastAPI
from pydantic import BaseModel
import logging, logging.config
import atexit
import asyncio

import chain 

logging.config.fileConfig('logging.conf')
app_logger = logging.getLogger('appLogger')

CHAIN = chain.load()
app = FastAPI()
app_logger.info('Starting...')


class Transaction(BaseModel):
    sender: str
    recipient: str
    amount: int
    tstamp: float
    signature: bytes


@app.get("/")
async def read_root():
    return {"Hello": "World"}

@app.post("/create_tx")
async def create_tx(tx: Transaction):
    new_tx = chain.Transaction(tx.sender, tx.recipient, tx.amount, tx.signature, tx.tstamp)
    CHAIN.queue[-1].add_tx(new_tx)
    

@atexit.register
def on_exit():
    app_logger.info('Exiting...')
    app_logger.info('----------------------------')
    