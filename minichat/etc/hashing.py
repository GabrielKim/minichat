#-*- coding: utf-8 -*-

from hashlib import blake2b
import os

def genHash() -> str:
    # A function that makes id a random hash value.
    # references : 
    # https://docs.python.org/3/library/hashlib.html
    __salt = os.urandom(blake2b.SALT_SIZE)
    return blake2b(salt=__salt, digest_size=4).hexdigest()