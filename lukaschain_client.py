# lukaschain_client.py

# from secrets import 
from ecdsa import SigningKey, SECP256k1
import logging as log

def pub_from_pk(key: bytes):
    pk = SigningKey.from_string(key, SECP256k1)
    log.info('Obtaining public key from private key...')
    pub = pk.get_verifying_key().to_string(encoding='compressed')
    log.info(f'Public key is {pub[:4]}...')
    return pub

class Client:
    def __init__(self):
        self.signing_key = SigningKey.generate(curve=SECP256k1)
        self.verifying_key = self.signing_key.verifying_key

    def get_pubkey(self):
        return self.verifying_key.to_string()
