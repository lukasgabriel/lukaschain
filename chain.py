# lukaschain.py

import time
import sys
import logging
import atexit
import json
import pickle
from Crypto.Hash import SHA256


chain_logger = logging.getLogger('chainLogger')


class Transaction:
    def __init__(self, sender: str, recipient: str, amount: int, signature: bytes, tstamp: float):
        self.sender = sender
        self.recipient = recipient
        self.amount = amount
        self.tstamp = tstamp
        self.own_tstamp = time.time()
        self.tx_hash = self.calc_hash()
    
    def verify(self):
        pass

    def to_string(self):
        tx_string = f'{self.sender}_{self.recipient}_{self.amount}_{self.tstamp}'
        return tx_string

    def calc_hash(self):
        hash_obj = SHA256.new()
        hash_obj.update(self.to_string().encode())
        return hash_obj.hexdigest()

    def to_json(self):
        return json.dumps(self.__dict__)


class Block:
    def __init__(self, prev_hash: str, prev_ind: int):
        '''
        Constructor of the 'Block' class.
        :param b_ind: Index of the block.
        :param tx_list: List of transactions.
        :param tstamp: Timestamp at block generation.
        :param prev_hash: Hashdigest of the preceding block.
        :param prev_ind: Index of the previous block.
        '''
        self.b_ind = prev_ind + 1
        self.tx_list = []
        self.tstamp = time.time()
        self.prev_hash = prev_hash
        self.block_hash = self.calc_hash()

    def to_string(self):
        block_string = f'{self.b_ind}_{self.tstamp}_{self.tx_list}_{self.prev_hash}'
        return block_string

    def calc_hash(self):
        hash_obj = SHA256.new()
        hash_obj.update(self.to_string().encode())
        return hash_obj.hexdigest()

    def to_json(self):
        return json.dumps(self.__dict__)

    def add_tx(self, tx):
        self.tx_list.append(tx)

GENESIS = Block(prev_hash=None, prev_ind=0)

class Chain:
    def __init__(self):
        self.chain = []
        self.queue = []
        self.chain.append(GENESIS)

    def add_block(self, block):
        old_prev = self.chain[-1].block_hash
        new_prev = block.prev_hash
        new_hash = block.block_hash
        new_verify = SHA256.new(block.to_string().encode()).hexdigest()
        if not old_prev == new_prev:
            chain_logger.info(f'Parent hash mismatch between own [{old_prev}] and new [{new_prev}].')
            return False
        if not new_hash == new_verify:
            chain_logger.info(f'Invalid hash of block [{new_hash}]; should be [{new_verify}].')
            return False
        self.chain.append(block)
        chain_logger.info(f'Appended block {new_hash} to chain.')

    def to_bytes(self):
        outfile = 'chain.dat'
        chain_logger.info(f'Writing chain state to {outfile}.')
        with open('chain.dat', 'wb') as outfile:
            pickle.dump(self, outfile)
        chain_logger.info('Chain state successfully saved.')


CHAIN = Chain()

def load():
    try:
        with open('chain.dat', 'rb') as infile:
            chain_logger.info('Loading chain.dat')
            CHAIN = pickle.load(infile)
            return CHAIN
    except FileNotFoundError:
        new_prompt = input('Chainfile not found. Initialize new chain? (y/n)')
        if new_prompt == 'y' or 'Y':
            CHAIN = Chain()
            chain_logger.info('Initializing new chain...')
            return CHAIN
        else:
            sys.exit()

@atexit.register
def on_exit():
    CHAIN.to_bytes()
    chain_logger.info('Exiting...')
    chain_logger.info('----------------------------')
