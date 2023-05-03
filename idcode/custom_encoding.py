import re
import base64
import urllib.parse
import html
from quopri import decodestring
from .core_values import values_decode
import string
from abc import ABC, abstractmethod


class Encoding(ABC):
    pattern = None

    @classmethod
    def is_valid(cls, encoded_text):
        return cls.is_valid_length(encoded_text) and re.match(cls.pattern, encoded_text) is not None

    @staticmethod
    def is_valid_length(encoded_text):
        return True  # 默认情况下，我们不对长度进行任何检查

    @staticmethod
    @abstractmethod
    def decode(encoded_text):
        pass

    @classmethod
    def try_decode(cls, encoded_text):
        try:
            decoded_text = cls.decode(encoded_text)
            return True, decoded_text
        except Exception as e:
            return False, None


class Base94Encoding(Encoding):
    pattern = r'^[\x21-\x7E]+$'
    ALPHABET = ''.join(chr(i) for i in range(0x21, 0x7F))

    @staticmethod
    def decode(encoded_text):
        num = 0
        for char in encoded_text:
            num *= 94
            num += Base94Encoding.ALPHABET.index(char)

        result = bytearray()
        while num > 0:
            num, mod = divmod(num, 256)
            result.append(mod)

        return bytes(result[::-1]).decode('utf-8')


class Base92Encoding(Encoding):
    pattern = r'^[\x21\x23-\x5f\x61-\x7e]+$'
    ALPHABET = "!#$%&'()*+,-./0123456789:;<=>?@ABCDEFGHIJKLMNOPQRSTUVWXYZ[\]^_abcdefghijklmnopqrstuvwxyz{|}~"
    ALPHAMAP = {c: idx for idx, c in enumerate(ALPHABET)}

    @staticmethod
    def decode(encoded_text):
        alphamap = Base92Encoding.ALPHAMAP
        if encoded_text == '~':
            return ''

        decoded = bytearray()
        bits = ''
        for i in range(0, len(encoded_text)-1, 2):
            c = alphamap[encoded_text[i]] * 91 + alphamap[encoded_text[i+1]]
            bits += bin(c)[2:].zfill(13)

        if len(encoded_text) % 2 == 1:
            c = alphamap[encoded_text[-1]]
            bits += bin(c)[2:].zfill(6)

        for i in range(0, len(bits), 8):
            decoded.append(int(bits[i:i+8], 2))

        return decoded.decode('utf-8')


class Base91Encoding(Encoding):
    pattern = r'^[A-Za-z0-9!#\$%&\(\)\*\+,\./:;<=>\?@\[\]\^_`\{\|\}~]+$'
    ALPHABET = string.ascii_uppercase + string.ascii_lowercase + \
        string.digits + '!#$%&()*+,./:;<=>?@[]^_`{|}~"'
    ALPHAMAP = {c: idx for idx, c in enumerate(ALPHABET)}

    @staticmethod
    def decode(encoded_text):
        ''' Decode Base91 string to a bytearray '''
        alphamap = Base91Encoding.ALPHAMAP

        decoded = bytearray()
        value = 0
        bit_len = 0
        for i in range(0, len(encoded_text)-1, 2):
            c = alphamap[encoded_text[i]] + alphamap[encoded_text[i+1]] * 91
            value += c << bit_len
            if c & 8191 > 88:
                bit_len += 13
            else:
                bit_len += 14
            while bit_len >= 8:
                decoded.append(value & 255)
                value >>= 8
                bit_len -= 8

        if len(encoded_text) % 2 == 1:
            c = alphamap[encoded_text[-1]]
            value += c << bit_len
            decoded.append(value & 255)

        return decoded.decode('utf-8')


class Base85Encoding(Encoding):
    pattern = r'^[0-9A-Za-z\(\)\{\}\[\]<>\.\^\*\+\-!&%\$@;:_,`|~]+$'

    @staticmethod
    def decode(encoded_text):
        return base64.b85decode(encoded_text).decode('utf-8')


class Ascii85Encoding(Encoding):
    pattern = r'^[\x21-\x75]+$'

    @staticmethod
    def decode(encoded_text):
        return base64.a85decode(encoded_text, adobe=False).decode('utf-8')


class AdobeAscii85Encoding(Encoding):
    pattern = r'^[\x21-\x75]+$'

    @staticmethod
    def decode(encoded_text):
        return base64.a85decode(encoded_text, adobe=True).decode('utf-8')


class Z85Encoding(Encoding):
    pattern = r'^[0-9a-zA-Z.\-:+=^!/*?&<>()\[\]{}@%$#]+$'
    ALPHABET = "0123456789abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ.-:+=^!/*?&<>()[]{}@%$#"
    ALPHAMAP = {c: idx for idx, c in enumerate(ALPHABET)}

    @staticmethod
    def is_valid_length(encoded_text):
        return len(encoded_text) % 5 == 0

    @staticmethod
    def decode(encoded_text):
        alphamap = Z85Encoding.ALPHAMAP
        base = [85**i for i in range(5)][::-1]
        decoded = ''
        for i in range(0, len(encoded_text), 5):
            c = 0
            for j in range(5):
                c += alphamap[encoded_text[i + j]] * base[j]
            decoded += c.to_bytes(4, byteorder='big').decode('utf-8')
        return decoded


class Base64Encoding(Encoding):
    pattern = r'^[A-Za-z0-9+/]+={0,2}$'

    @staticmethod
    def is_valid_length(encoded_text):
        return len(encoded_text) % 4 == 0

    @staticmethod
    def decode(encoded_text):
        return base64.b64decode(encoded_text).decode('utf-8')


class Base62Encoding(Encoding):
    pattern = r'^[0-9A-Za-z]+$'
    ALPHABET = string.digits + string.ascii_uppercase + string.ascii_lowercase

    @staticmethod
    def decode(encoded_text):
        num = 0
        for char in encoded_text:
            num *= 62
            num += Base62Encoding.ALPHABET.index(char)

        result = bytearray()
        while num > 0:
            num, mod = divmod(num, 256)
            result.append(mod)

        # 计算 padding
        padding = 0
        for char in encoded_text:
            if char == '0':
                padding += 1
            else:
                break

        return (b'\x00' * padding + bytes(result[::-1])).decode('utf-8')


class Base58Encoding(Encoding):
    pattern = r'^[123456789ABCDEFGHJKLMNPQRSTUVWXYZabcdefghijkmnopqrstuvwxyz]+$'
    ALPHABET = '123456789ABCDEFGHJKLMNPQRSTUVWXYZabcdefghijkmnopqrstuvwxyz'

    @staticmethod
    def decode(encoded_text):
        num = 0
        for char in encoded_text:
            num *= 58
            num += Base58Encoding.ALPHABET.index(char)

        result = bytearray()
        while num > 0:
            num, mod = divmod(num, 256)
            result.append(mod)

        padding = 0
        for char in encoded_text:
            if char == '1':
                padding += 1
            else:
                break

        return (b'\x00' * padding + bytes(result[::-1])).decode('utf-8')


class Base45Encoding(Encoding):
    pattern = r'^[0-9A-Za-z$%*+-./:]+$'
    ALPHABET = '0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZ $%*+-./:'
    ALPHAMAP = {c: idx for idx, c in enumerate(ALPHABET)}

    @staticmethod
    def is_valid_length(encoded_text):
        return len(encoded_text) % 3 == 0

    @staticmethod
    def decode(encoded_text):
        alphamap = Base45Encoding.ALPHAMAP
        base = [45**i for i in range(3)]
        decoded = ''
        for i in range(0, len(encoded_text), 3):
            c = 0
            for j in range(3):
                c += alphamap[encoded_text[i+j]] * base[j]
            decoded += c.to_bytes(2, byteorder='big').decode('utf-8')

        return decoded


class Base36Encoding(Encoding):
    pattern = r'^[0-9A-Za-z]+$'
    ALPHABET = string.digits + string.ascii_uppercase

    @staticmethod
    def decode(encoded_text):
        num = int(encoded_text, 36)
        return num


class Base32Encoding(Encoding):
    pattern = r'^[A-Z2-7]+=*$'

    @staticmethod
    def is_valid_length(encoded_text):
        return len(encoded_text) % 8 == 0

    @staticmethod
    def decode(encoded_text):
        return base64.b32decode(encoded_text).decode('utf-8')


class HexEncoding(Encoding):
    pattern = re.compile(
        r'^(0[xX]|\\[xX])?[0-9a-fA-F]+([-:,;\s](0[xX]|\\[xX])?[0-9a-fA-F]+)*$')

    @staticmethod
    def is_valid_length(encoded_text):
        # 移除常见的前缀和分隔符
        encoded_text = re.sub(r'^(0[xX]|\\[xX])', '', encoded_text)
        encoded_text = re.sub(r'[-:,;\s]', '', encoded_text)
        return len(encoded_text) % 2 == 0

    @staticmethod
    def decode(encoded_text):
        # 移除常见的前缀和分隔符
        encoded_text = re.sub(r'(0[xX]|\\[xX])', '', encoded_text)
        encoded_text = re.sub(r'[-:,;\s]', '', encoded_text)
        print(encoded_text)
        # 解码hex字符串
        decoded_data = bytes.fromhex(encoded_text)
        return decoded_data.decode('utf-8')


class Base8Encoding(Encoding):
    pattern = r'^[0-7]+$'

    @staticmethod
    def decode(encoded_text):
        num = int(encoded_text, 8)
        return bytes.fromhex(hex(num)[2:]).decode('utf-8')


class BinaryEncoding(Encoding):
    pattern = r'^(0b)?([01]{8}[-:,;\s]?)+$'

    @staticmethod
    def is_valid_length(encoded_text):
        if encoded_text.startswith('0b'):
            encoded_text = encoded_text[2:]
        encoded_text = re.sub(r'[-:,;\s]', '', encoded_text)
        return len(encoded_text) % 8 == 0

    @staticmethod
    def decode(encoded_text):
        if encoded_text.startswith('0b'):
            encoded_text = encoded_text[2:]
        encoded_text = re.sub(r'[-:,;\s]', '', encoded_text)
        return bytearray(int(encoded_text[i:i+8], 2) for i in range(0, len(encoded_text), 8)).decode('utf-8')


class URLEncoding(Encoding):
    pattern = r'%[0-9A-Fa-f]{2}'

    @staticmethod
    def is_valid(encoded_text):
        return re.search(URLEncoding.pattern, encoded_text) is not None

    @staticmethod
    def decode(encoded_text):
        return urllib.parse.unquote(encoded_text)


class HTMLEncoding(Encoding):
    pattern = r'&(#?)(\w+);'

    @staticmethod
    def is_valid(encoded_text):
        return re.search(HTMLEncoding.pattern, encoded_text) is not None

    @staticmethod
    def decode(encoded_text):
        return html.unescape(encoded_text)


class QuotedPrintableEncoding(Encoding):
    pattern = r'(?:=([0-9A-F]{2})|=0D=0A|\r\n)'

    @staticmethod
    def is_valid(encoded_text):
        return re.search(QuotedPrintableEncoding.pattern, encoded_text) is not None

    @staticmethod
    def decode(encoded_text):
        return decodestring(encoded_text.encode('utf-8')).decode('utf-8')


class CoreValuesEncoding(Encoding):
    pattern = r'^(富强|民主|文明|和谐|自由|平等|公正|法治|爱国|敬业|诚信|友善)+$'
    ALPHABET = '富强民主文明和谐自由平等公正法治爱国敬业诚信友善'

    @staticmethod
    def decode(encoded_text):
        return values_decode(encoded_text)


all_encodings = [
    Base94Encoding, Base92Encoding, Base91Encoding, Base85Encoding, Ascii85Encoding,
    AdobeAscii85Encoding, Z85Encoding, Base64Encoding, Base62Encoding, Base58Encoding,
    Base45Encoding, Base36Encoding, Base32Encoding, HexEncoding, Base8Encoding,
    BinaryEncoding, URLEncoding,  HTMLEncoding, QuotedPrintableEncoding, CoreValuesEncoding
]
