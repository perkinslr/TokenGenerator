import twisted.web._flatten as _f

def efc(x):
    if isinstance(x, bytes):
        return x
    return x.encode('utf-8')

_f.escapeForContent = efc
