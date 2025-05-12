import hashlib
import time
import uuid

def encrypt(signStr):
    hash_algorithm = hashlib.sha256()
    hash_algorithm.update(signStr.encode('utf-8'))
    return hash_algorithm.hexdigest()

def truncate(q):
    if q is None:
        return None
    size = len(q)
    return q if size <= 20 else q[0:10] + str(size) + q[size-10:size]

def addAuthParams(appKey, appSecret, params):
    q = params.get('q')
    if q is None:
        q = params.get('img')
    curtime = str(int(time.time()))
    salt = str(uuid.uuid1())
    signStr = appKey + truncate(q) + salt + curtime + appSecret
    sign = encrypt(signStr)

    params['appKey'] = appKey
    params['salt'] = salt
    params['curtime'] = curtime
    params['signType'] = 'v3'
    params['sign'] = sign

    return params 