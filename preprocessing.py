import re


def remove_prefixes(encoded_text):
    encoded_text = re.sub(r'(0[xX]|\\[xX]|0[bB])', '', encoded_text)
    return encoded_text


def remove_separators(encoded_text):
    encoded_text = re.sub(r'[-:;,\s]', '', encoded_text)
    return encoded_text


def unify_case(encoded_text):
    return encoded_text.lower()
