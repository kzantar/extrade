import hashlib

def callMethod(o, name):
    getattr(o, name)()

def strmd5sum(string):
    m = hashlib.md5()
    m.update(str(string))
    return m.hexdigest()
