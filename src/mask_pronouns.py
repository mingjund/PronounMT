import sys
import argparse
import spacy
import re
from nltk.tokenize.treebank import TreebankWordDetokenizer
from tqdm import tqdm


nlp = spacy.load("en_core_web_sm")

en_pro = {'i', 'my', 'me', 'mine', 'myself',
                'we', 'us', 'our', 'ours', 'ourselves',
                'you', 'your', 'yours', 'yourself', 'yourselves',
                'he', 'him', 'his', 'himself',
                'she', 'her', 'hers', 'herself',
                'they', 'them', 'their', 'theirs', 'themself', 'themselves',
                'it', 'its', 'itself'}

ja_pro = {'私', 'わたし', 'ワタシ', '私達', '私たち', '僕', 'ぼく', '自分', 'みんな', '皆', '皆さん',
                'ボク', '僕ら', '僕たち', 'ぼくたち', '俺', 'おれ', 'オレ', '俺ら', '俺たち', 'おれたち',
                'あなた', 'あなた達', 'あなたたち', '貴方', 'あんた','貴様', '手前',
                'お前', 'おまえ','お前ら','君','きみ','キミ','君達', '君たち',
                '彼', 'かれ', 'カレ', '彼ら',
                '彼女', 'かのじょ', 'カノジョ', 'かのじょたち', '彼女たち', '彼女達'}

ja_pro2person = {'私':'1', 'わたし':'1', 'ワタシ':'1', '私達':'1', '私たち':'1', '僕':'1', 'ぼく':'1', '自分':'self', 'みんな':'x', '皆':'x', '皆さん':'x',
                'ボク':'1', '僕ら':'1', '僕たち':'1', 'ぼくたち':'1', '俺':'1', 'おれ':'1', 'オレ':'1', '俺ら':'1', '俺たち':'1', 'おれたち':'1',
                'あなた':'2', 'あなた達':'2', 'あなたたち':'2', '貴方':'2', 'あんた':'2','貴様':'2', '手前':'2',
                'お前':'2', 'おまえ':'2','お前ら':'2','君':'2','きみ':'2','キミ':'2','君達':'2', '君たち':'2',
                '彼':'3m', 'かれ':'3m', 'カレ':'3m', '彼ら':'3m',
                '彼女':'3f', 'かのじょ':'3f', 'カノジョ':'3f', 'かのじょたち':'3f', '彼女たち':'3f', '彼女達':'3f'}


person2en_pro = {'1':{'i', 'my', 'me', 'mine', 'myself', 'we', 'us', 'our', 'ours', 'ourselves'},
                '2':{'you', 'your', 'yours', 'yourself', 'yourselves'},
                '3m':{'he', 'him', 'his', 'himself', 'they', 'them', 'their', 'theirs', 'themself', 'themselves'},
                '3f':{'she', 'her', 'hers', 'herself', 'they', 'them', 'their', 'theirs', 'themself', 'themselves'},
                'self':{'myself', 'ourselves', 'yourselves', 'themselves'},
                'x':{}}


d = TreebankWordDetokenizer()

def detokenize(text):
    text = d.detokenize(text)
    text = text.replace(' .', '.')
    text = text.replace('...', '... ')
    text = text.replace(' ,', ',')
    text = text.replace(" '", "'")
    text = re.sub(r'\" (.*?) \"', r'"\1"', text)
    return text


def src2tgt_pronouns(src_prons):
    tgt_prons = set().union(*map(lambda x: person2en_pro[ja_pro2person[x]] , src_prons))
    return tgt_prons


def mask_pronouns(in_src, in_tgt, out_tgt, out_labels):
    if in_src != None:
        with open(in_src, 'r') as f_src, open(in_tgt, 'r') as f_tgt:
            print("preprocessing...")
            src_lines = [sent.split() for sent in f_src.readlines()]
            tgt_lines = [sent for sent in tqdm(nlp.pipe(f_tgt.readlines()))]
            print("preprocessed!")
            
            new_tgt_lines = []
            masked_pron_labels = []

            print("masking pronouns...")
            for src_sent, tgt_sent in tqdm(zip(src_lines, tgt_lines)):
                src_pronouns = set(src_sent) & ja_pro
                src_pron_translations = src2tgt_pronouns(src_pronouns)
                prons_to_mask = en_pro - src_pron_translations

                # new_line = []
                # for token in tgt_sent:
                #     if token.text.lower() not in prons_to_mask:
                #         new_line.append(token.text)
                #     else:
                #         new_line.append('<mask>')
                #         masked_pron_labels.append(token.text.lower()+'\n')

                # new_src_lines.append(detokenize(new_line)+'\n')
                new_tgt_lines.append(detokenize([token.text if token.text.lower() not in prons_to_mask else '[MASK]' for token in tgt_sent])+'\n')
                masked_pron_labels.append('\t'.join([token.text for token in tgt_sent if token.text.lower() in prons_to_mask])+'\n')

            print("masked!")
            #new_src_lines = [detokenize(line) for line in new_src_lines]

    else:
        with open(in_tgt, 'r') as f_tgt:
            print("preprocessing...")
            tgt_lines = [sent for sent in tqdm(nlp.pipe(f_tgt.readlines()))]
            print("preprocessed!")
            
            new_tgt_lines = []
            masked_pron_labels = []

            print("masking pronouns...")
            for tgt_sent in tgt_lines:
                new_tgt_lines.append(detokenize([token.text if token.text.lower() not in en_pro else '[MASK]' for token in tgt_sent])+'\n')
                masked_pron_labels.append('\t'.join([token.text for token in tgt_sent if token.text.lower() in en_pro])+'\n')

            print("masked!")
            #new_src_lines = [detokenize(line) for line in new_src_lines]

    with open(out_tgt, 'w') as f_tgt, open(out_labels, 'w') as f_labels:
        f_tgt.writelines(new_tgt_lines)
        f_labels.writelines(masked_pron_labels)

    print("tgt file written!")


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument('--in_src_path', type=str, default=None)
    parser.add_argument('--in_tgt_path', type=str, default='train.en')
    parser.add_argument('--out_tgt_path', type=str, default='train.pron_masked_en')
    parser.add_argument('--out_labels_path', type=str, default='train.pron_masked_labels')

    args = parser.parse_args()  
    
    mask_pronouns(args.in_src_path, args.in_tgt_path, args.out_tgt_path, args.out_labels_path)