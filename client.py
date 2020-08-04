# lukaschain_client.py

# from secrets import 
from ecdsa import SigningKey, SECP256k1
from Crypto.Hash import SHA256, RIPEMD
from base58check import b58encode, b58decode
import logging as log

def pub_from_pk(key: bytes):
    pk = SigningKey.from_string(key, SECP256k1)
    log.info('Obtaining public key from private key...')
    pub = pk.get_verifying_key().to_string(encoding='compressed')
    log.info(f'Public key is {pub[:4]}...')
    return pub

class Client:

    def __init__(self):
        log.info('Initializing Client...')
        try:
            with open(f'wallet\\private.pem', 'rb') as f:
                self.signing_key = SigningKey.from_pem(f.read())
                log.info('Found keyfile.')
        except FileNotFoundError:
            self.gen_key()
        self.verifying_key = self.signing_key.verifying_key
        log.info(f'Client initialized with public key {self.__str__()}...')
        self.wallet = Wallet(pubkey=self.get_pubkey())

    def __str__(self):
        return self.verifying_key.to_string().hex()[:4]

    def gen_key(self):
        log.info('Generating new keypair...')
        self.signing_key = SigningKey.generate(curve=SECP256k1)

    def get_pubkey(self):
        return self.verifying_key.to_string()

    def to_file(self):
        with open('wallet\\private.pem', 'wb') as f:
            f.write(self.signing_key.to_pem())
            log.info(f'Writing private key of {self.__str__()} to keyfile...')

    def create_tx(self, recipient: bytes, amount: int):
        # tx = {'sender': }
        pass

class Wallet(Client):
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


testclient = Client()
print(testclient.wallet.address.decode('utf-8'))
testclient.to_file()