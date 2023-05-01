import random
import urllib.parse
import re

VALUES = '富强民主文明和谐自由平等公正法治爱国敬业诚信友善'
A2F_FLAG = 10


def assert_(cond, msg='Assert Error'):
    if not cond:
        raise ValueError(msg)


def rand_bin():
    return random.SystemRandom().getrandbits(1)


def str2utf8(string):
    not_encoded = r'[A-Za-z0-9\-\_\.\!\~\*\'\(\)]'
    str1 = re.sub(not_encoded, lambda m: hex(ord(m.group(0)))[2:], string)
    str2 = urllib.parse.quote(str1)
    return ''.join(str2.split('%')).upper()


def utf82str(utfs):
    assert_(isinstance(utfs, str), 'utfs Error')
    assert_(len(utfs) % 2 == 0)

    splited = ['%' + utfs[i:i+2] for i in range(0, len(utfs), 2)]
    return urllib.parse.unquote(''.join(splited))


def hex2duo(hexs):
    duo = []
    for c in hexs:
        n = int(c, 16)
        if n < 10:
            duo.append(n)
        else:
            if rand_bin():
                duo.append(A2F_FLAG)
                duo.append(n - 10)
            else:
                duo.append(A2F_FLAG + 1)
                duo.append(n - 6)
    return duo


def duo2hex(duo):
    assert_(isinstance(duo, list))

    hexs = []
    i = 0
    while i < len(duo):
        if duo[i] < 10:
            hexs.append(str(duo[i]))
        else:
            if duo[i] == A2F_FLAG:
                i += 1
                hexs.append(hex(duo[i] + 10)[2:].upper())
            else:
                i += 1
                hexs.append(hex(duo[i] + 6)[2:].upper())
        i += 1
    return ''.join(hexs)


def duo2values(duo):
    return ''.join([VALUES[2*d] + VALUES[2*d+1] for d in duo])


def values_decode(encoded):
    duo = []
    for c in encoded:
        i = VALUES.find(c)
        if i == -1 or i % 2 == 1:
            continue
        duo.append(i // 2)

    hexs = duo2hex(duo)
    assert_(len(hexs) % 2 == 0)

    try:
        string = utf82str(hexs)
    except Exception as e:
        raise ValueError(e)
    return string


def values_encode(string):
    return duo2values(hex2duo(str2utf8(string)))