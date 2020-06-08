import uuid
import time
import random
import time
from hashlib import sha1


def get_mac():
    return ':'.join(['{:02x}'.format((uuid.getnode() >> ele) & 0xff)
                     for ele in range(0, 8*6, 8)][::-1])


def nonce():
    auth_type = "0"
    device_id = get_mac()
    timestamp = str(int(time.time()))
    rnd = str(random.randrange(100, 999))
    return "_".join([auth_type, device_id, timestamp, rnd])


def encoded_password(key, password, nonce):
    return sha1(bytes(nonce +
                      sha1(bytes(password + key, encoding='utf-8')).hexdigest(), encoding='utf-8')).hexdigest()
