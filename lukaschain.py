# lukaschain.py

from Crypto.Hash import SHA256, RIPEMD
from base58check import b58encode, b58decode
import time
import sys
import logging as log
import atexit
import json
import pickle

from lukaschain_client import Client

# LOGFILE = f'{time.strftime("%Y%m%d-%H%M%S")}.log'
LOGFILE = 'lukaschain.log'

log.basicConfig(filename=LOGFILE, format='[%(asctime)s] %(message)s', level=log.INFO)

class Wallet:
    def __init__(self, pubkey: bytes):
        self.balance = 0
        log.info('Creating new Wallet...')
        self.address = self.gen_address(pubkey)
        log.info(f'Wallet address is {self.address.decode("utf-8")}.')

    def gen_address(self, pubkey: bytes):
        log.info(f'Generating Wallet address for public key {pubkey.hex()[:4]}...')
        pub_ripemd = RIPEMD.new(SHA256.new(pubkey).digest())
        pub_b58 = b58encode(pub_ripemd.digest())
        return pub_b58


class Transaction:
    def __init__(self, sender: Wallet, recipient: Wallet, amount: int):
        self.sender = sender
        self.recipient = recipient
        self.amount = amount
        self.tstamp = time.time()
        self.tx_hash = self.calc_hash()
    
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
            log.info(f'Parent hash mismatch between own [{old_prev}] and new [{new_prev}].')
            return False
        if not new_hash == new_verify:
            log.info(f'Invalid hash of block [{new_hash}]; should be [{new_verify}].')
            return False
        self.chain.append(block)
        log.info(f'Appended block {new_hash} to chain.')

    def to_bytes(self):
        outfile = 'chain.dat'
        log.info(f'Writing chain state to {outfile}.')
        with open('chain.dat', 'wb') as outfile:
            pickle.dump(self, outfile)
        log.info('Chain state successfully saved.')


@atexit.register
def on_exit():
    CHAIN.to_bytes()
    log.info('Exiting...')
    log.info('----------------------------')

if __name__ == '__main__':
    log.info('Starting...')
    try:
        with open('chain.dat', 'rb') as infile:
            log.info(f'Loading chain.dat')
            CHAIN = pickle.load(infile)
    except FileNotFoundError as e:
        new_prompt = input('Chainfile not found. Initialize new chain? (y/n)')
        if new_prompt == 'y' or 'Y':
            CHAIN = Chain()
            log.info('Initializing new chain...')
        else:
            sys.exit()


testclient = Client()
testwallet = Wallet(pubkey=testclient.get_pubkey()) 
print(testwallet.address.decode('utf-8'))