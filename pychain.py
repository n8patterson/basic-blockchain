"""PyChain Ledger

Example blockchain application

Example:
    $ streamlit run pychain.py
"""

# Imports
import streamlit as st
from dataclasses import dataclass
from typing import Any, List
import datetime as datetime
import pandas as pd
import hashlib

@dataclass
class Record:
    """A class used to represent the data/record inside of a block

    ...

    Attributes
    ----------
    sender : str
        a  string to identify the sender
    receiver : str
        a  string to identify the receiver
    amount : float
        a  float to identify the amount of the record
    """

    sender: str
    receiver: str
    amount: float


@dataclass
class Block:
    """A class used to represent a block in the blockchain

    Attributes
    ----------
    record : Record
        the data/record of the block
    creator_id : int
        id for the name of the creator
    prev_hash : str
        link to the previous hash in the blockchain
    timestamp : str
        the current time of when the block was created in UTC
    nonce : str
        the number added to the hash/block "number only used once"

    Methods
    -------
    hash_block(self)
        computes the hash of the current block
    """

    record: Record
    creator_id: int
    prev_hash: str = 0
    timestamp: str = datetime.datetime.utcnow().strftime("%H:%M:%S")
    nonce: str = 0

    def hash_block(self):
        """Determine the hash of the current block

        The current block hash is based on:
            - record
            - creator_id
            - timestamp
            - pev_hash
            - nonce

        Parameters
        ----------
            self ([Block]): current block

        Returns
        -------
            a hex value for the current hash of this block
        """

        sha = hashlib.sha256()

        record = str(self.record).encode()
        sha.update(record)

        creator_id = str(self.creator_id).encode()
        sha.update(creator_id)

        timestamp = str(self.timestamp).encode()
        sha.update(timestamp)

        prev_hash = str(self.prev_hash).encode()
        sha.update(prev_hash)

        nonce = str(self.nonce).encode()
        sha.update(nonce)

        return sha.hexdigest()


@dataclass
class PyChain:
    """A class used to represent a blockchain

    Attributes
    ----------
    chain : List[Block]
        a representation of a blockchain with Blocks
    difficulty : int
        difficulty for computing the next block/hash

    Methods
    -------
    proof_of_work(self)
        calculates the next hash given a difficulty and a candidate block and returns a block to be added to the blockchain
    add_block(self)
        adds a block to the chain(blockchain)
    is_valid(self)
        determines if the entire blockchain is valid, i.e. all have correct hash values
    """

    chain: List[Block]
    difficulty: int = 4

    def proof_of_work(self, block):
        """Determine the hash of the current block

        The candidate block is created based on:
            - difficluty

        Parameters
        ----------
            self (PyChain): current PyChain
            block ([Block]): candidate block to be added to the blockchain

        Returns
        -------
            a new block with correct number set for nonce to help compute the winning hash
        """

        calculated_hash = block.hash_block()

        num_of_zeros = "0" * self.difficulty

        while not calculated_hash.startswith(num_of_zeros):

            block.nonce += 1

            calculated_hash = block.hash_block()

        print("Wining Hash", calculated_hash)
        return block

    def add_block(self, candidate_block):
        """Adds a new block to this blockchain using poof_of_work()

        A new block is added by using:
            - proof_of_work()

        Parameters
        ----------
            self (PyChain): current PyChain
            block ([Block]): candidate block to be added to the blockchain
        """

        block = self.proof_of_work(candidate_block)
        self.chain += [block]

    def is_valid(self):
        """Determines if this entire blockchain is valid

        Starts with the first block in the chain and iterates over the entire chain comparing hash values

        Parameters
        ----------
            self (PyChain): current PyChain

        Returns
        -------
            a if this blockchain is valid
        """
        
        block_hash = self.chain[0].hash_block()

        for block in self.chain[1:]:
            if block_hash != block.prev_hash:
                print("Blockchain is invalid!")
                return False

            block_hash = block.hash_block()

        print("Blockchain is Valid")
        return True

################################################################################
# Streamlit Code

# Adds the cache decorator for Streamlit
@st.cache(allow_output_mutation=True)
def setup():
    print("Initializing Chain")
    return PyChain([Block("Genesis", 0)])


st.markdown("# PyChain")
st.markdown("## Store a Transaction Record in the PyChain")

pychain = setup()

################################################################################

# Input area where you can get a value for `sender` from the user.
sender = st.text_input("Sender")

# Input area where you can get a value for `receiver` from the user.
receiver = st.text_input("Receiver")

# Input area where you can get a value for `amount` from the user.
amount = st.text_input("Amount")

if st.button("Add Block"):
    prev_block = pychain.chain[-1]
    prev_block_hash = prev_block.hash_block()

    # Update `new_block` so that `Block` consists of an attribute named `record`
    # which is set equal to a `Record` that contains the `sender`, `receiver`,
    # and `amount` values
    new_block = Block(
        record=Record(sender, receiver, float(amount)),
        creator_id=42,
        prev_hash=prev_block_hash
    )

    pychain.add_block(new_block)
    st.balloons()

################################################################################

st.markdown("## The PyChain Ledger")

pychain_df = pd.DataFrame(pychain.chain)
st.write(pychain_df)

difficulty = st.sidebar.slider("Block Difficulty", 1, 5, 2)
pychain.difficulty = difficulty

st.sidebar.write("# Block Inspector")
selected_block = st.sidebar.selectbox(
    "Which block would you like to see?", pychain.chain
)

st.sidebar.write(selected_block)

if st.button("Validate Chain"):
    st.write(pychain.is_valid())