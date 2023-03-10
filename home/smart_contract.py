import os
import hashlib
from Crypto.PublicKey import RSA
from Crypto.Signature import pkcs1_15
from Crypto.Hash import SHA256

from web3 import Web3
from web3.middleware import geth_poa_middleware

from django.conf import settings


def sign_document(document, private_key):
    """
    Create a digital signature for the given document using the given private key.
    Returns the signature as bytes.
    """
    # Generate SHA-256 hash of document
    hash = hashlib.sha256(document).digest()
    
    # Load private key
    rsa_key = RSA.import_key(private_key)
    
    # Sign hash with private key
    signer = pkcs1_15.new(rsa_key)
    signature = signer.sign(SHA256.new(hash))
    
    return signature


def connect_to_blockchain():
    """
    Connect to Ethereum blockchain and return a web3 instance.
    """
    # Connect to blockchain
    provider = Web3.HTTPProvider(settings.ETH_NODE_URL)
    web3 = Web3(provider)
    web3.middleware_onion.inject(geth_poa_middleware, layer=0)
    
    # Load contract ABI and bytecode
    with open(os.path.join(settings.BASE_DIR, 'contracts', 'DocumentContract.abi')) as f:
        abi = f.read()
    with open(os.path.join(settings.BASE_DIR, 'contracts', 'DocumentContract.bin')) as f:
        bytecode = f.read()
    
    # Compile contract
    contract = web3.eth.contract(abi=abi, bytecode=bytecode)
    return web3, contract
    

def store_document_on_blockchain(document, party_a_private_key, party_b_private_key):
    """
    Store the given document on the blockchain as a contract between two parties.
    Returns the contract address.
    """
    # Connect to blockchain
    web3, contract = connect_to_blockchain()
    
    # Generate digital signatures for parties A and B
    party_a_signature = sign_document(document, party_a_private_key)
    party_b_signature = sign_document(document, party_b_private_key)
    
    # Convert signatures to hex strings
    party_a_signature_hex = party_a_signature.hex()
    party_b_signature_hex = party_b_signature.hex()
    
    # Get organization names for parties A and B
    party_a_organization_name = "Example Org A"  # replace with actual lookup logic
    party_b_organization_name = "Example Org B"  # replace with actual lookup logic
    
    # Submit document to contract
    tx_hash = contract.functions.storeDocument(document, party_a_signature_hex, party_b_signature_hex, party_a_organization_name, party_b_organization_name).transact()
    
    # Wait for transaction to be mined
    receipt = web3.eth.waitForTransactionReceipt(tx_hash)
    
    # Get contract address from receipt
    contract_address = receipt['contractAddress']
    
    return contract_address
