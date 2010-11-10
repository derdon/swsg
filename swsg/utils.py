from functools import partial
from operator import is_
from hashlib import sha256

is_none = partial(is_, None)

def hash_file(filename):
    with open(filename) as fp:
        text = fp.read()
    return sha256(text).hexdigest()
