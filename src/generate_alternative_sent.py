import sys
import spacy
import pyinflect
import re
from nltk.tokenize.treebank import TreebankWordDetokenizer

nlp = spacy.load("en_core_web_lg")

en_pro = {'i', 'my', 'me', 'mine', 'myself',
                'we', 'us', 'our', 'ours', 'ourselves',
                'you', 'your', 'yours', 'yourself', 'yourselves',
                'he', 'him', 'his', 'himself',
                'she', 'her', 'hers', 'herself',
                'they', 'them', 'their', 'theirs', 'themself', 'themselves',
                'it', 'its', 'itself'}

d = TreebankWordDetokenizer()

def detokenize(text):
    text = d.detokenize(text)
    text = text.replace(' .', '.')
    text = text.replace('...', '... ')
    text = text.replace(' ,', ',')
    text = text.replace(" '", "'")
    text = re.sub(r'\" (.*?) \"', r'"\1"', text)
    return text

def mask_pronouns(lst):
    return ['[MASK]' if token.lower() in en_pro else token for token in lst]

with open(sys.argv[1], 'r') as f:
    text = f.read().split('\n')

possible_texts = []

for sent in nlp.pipe(text):
    possible_sents = [[]]
    #print(possible_texts)
    for token in sent:
        if token.tag_ in {'VBP', 'VBZ', 'VB'}:
            if token.dep_ in {'aux', 'auxpass'}:
                children = [child.text.lower() for child in token.head.children if (child.text.lower() in en_pro and child.dep_ in {'nsubj', 'nsubjpass'})]
            else:
                children = [child.text.lower() for child in token.children if (child.text.lower() in en_pro and child.dep_ in {'nsubj', 'nsubjpass'})]
            if children != []:
                #for child in children:
                #if child.text.lower() in en_pro and child.dep_ == 'nsubj':
                #print(token.text, token.tag_, child.text, child.dep_)
                new_possible_sents = []
                inflected_tokens = []
                if token.text in {'am', 'is', 'are'}:
                    inflected_tokens = ['am', 'is', 'are']
                elif token.text == "'ve" or \
                    (token.text == "'s" and \
                    (token.head.text.lower() == 'been' or \
                    'been' in [child.text.lower() for child in token.head.children])):
                    print(True, sent)
                    assert(token.dep_ in {'aux', 'auxpass'})
                    inflected_tokens = ["'s", "'ve"]
                elif token.text in {"'m", "'s", "'re"}:
                    inflected_tokens = ["'m", "'s", "'re"]
                else:
                    for tag in ['VBP', 'VBZ']:
                            inflected_token = token._.inflect(tag, form_num=0)
                            if inflected_token != None:
                                inflected_tokens.append(inflected_token)

                for inflected_token in inflected_tokens:           
                    new_possible_sents += [cand + [inflected_token] for cand in possible_sents] 

                if new_possible_sents == []:
                    possible_sents = [cand + [token.text] for cand in possible_sents]
                else:
                    possible_sents = new_possible_sents

            else:
                possible_sents = [cand + [token.text] for cand in possible_sents]

        # elif token.tag_  == 'VB' and \
        #     token.text in {"'s", "'ve"} and \
        #     len([child for child in token.head.children if child.dep_ == 'nsubj' and child.text.lower() in en_pro]) > 0:
        #     print(sent)

        #     inflected_tokens = ["'s", "'ve"]
        #     new_possible_sents = []

        #     for inflected_token in inflected_tokens:           
        #         new_possible_sents += [cand + [inflected_token] for cand in possible_sents] 

        #     possible_sents = new_possible_sents

        else:
            #print(possible_sents)
            possible_sents = [cand + [token.text] for cand in possible_sents]

    possible_sents = list(set([detokenize(mask_pronouns(cand)) for cand in possible_sents]))
    possible_texts.append(' | '.join(possible_sents))

with open(sys.argv[1].replace('.en', '.pron_masked_alt_en'), 'w') as f:
    f.write('\n'.join(possible_texts))