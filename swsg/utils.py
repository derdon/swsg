from functools import partial
from operator import is_

is_none = partial(is_, None)
