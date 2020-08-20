import re
from nltk.tokenize.treebank import TreebankWordDetokenizer

d = TreebankWordDetokenizer()

def detokenize(text):
    text = d.detokenize(text.split())
    text = text.replace(' .', '.')
    text = text.replace('...', '... ')
    text = text.replace(' ,', ',')
    text = text.replace(" '", "'")
    text = re.sub(r'\" (.*?) \"', r'"\1"', text)
    return text