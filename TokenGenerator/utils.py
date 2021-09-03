import hashlib
from twisted.python.filepath import FilePath
from itertools import chain, count


def md5f(fp: FilePath):
    with fp.open('rb') as f:
        return hashlib.md5(f.read()).hexdigest()


def findImg(fp):
    for child in chain(fp.children(),
                       fp.parent().children(),
                       fp.parent().parent().children()):
        if child.basename().startswith('token.'):
            return child
    return None
