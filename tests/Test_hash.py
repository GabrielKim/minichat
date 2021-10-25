from hashlib import blake2b
import os
import pytest

@pytest.fixture
def genHash() -> str:
    # A function that makes id a random hash value.
    # references : 
    # https://docs.python.org/3/library/hashlib.html
    __salt = os.urandom(blake2b.SALT_SIZE)
    __digest = blake2b(salt=__salt, digest_size=4).hexdigest()
    return __digest

def test_hash(genHash):
     for x in range(0, 10):
         assert type(genHash) is str
    #assert type(genHash) is str