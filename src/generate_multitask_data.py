import sys
import spacy
from tqdm import tqdm
from rakutenma import RakutenMA


ja_pro = {'私', 'わたし', 'ワタシ', '私達', '僕', 'ぼく',
                'ボク', '僕ら', '俺', 'おれ', 'オレ', '俺ら',
                'あなた', 'あなた達', '貴方', 'あんた','貴様', '手前',
                'お前', 'おまえ','お前ら','君','きみ','キミ','君たち', '君たち',
                '彼', 'かれ', 'カレ', '彼ら',
                '彼女', 'かのじょ', 'カノジョ', '彼女たち', '彼女達'}

en_pro = {'i', 'my', 'me', 'mine', 'myself',
                'we', 'us', 'our', 'ours', 'ourselves',
                'you', 'your', 'yours', 'yourself', 'yourselves',
                'he', 'him', 'his', 'himself',
                'she', 'her', 'hers', 'herself',
                'they', 'them', 'their', 'theirs', 'themself', 'themselves',
                'it', 'its', 'itself'}

nlp = spacy.load("en_core_web_sm")

rma = RakutenMA(phi=1024, c=0.007812)
rma.load("model_ja.json")
rma.hash_func = rma.create_hash_func(15)


def text2text(src, tgt):
    return tgt[0].strip()


def text2pron(src, tgt):
    pron_text = []
    for token in tgt[1]:
        token_text = token.text.lower()
        if token_text in en_pro:
            pron_text.append(token_text)
    pron_text.append('|')
    return ' '.join(pron_text)


def text2pos(src, tgt):
    text = rma.tokenize(src.split(']	')[1].replace(' ', '').replace('▁', ''))
    return ' '.join([token[1] for token in text])


if __name__ == "__main__":
    src_in = sys.argv[1] 
    tgt_in = sys.argv[2]

    src_out = sys.argv[3]
    tgt_out = sys.argv[4]

    docs_out = sys.argv[5]

    simul = sys.argv[6]

    tasks = {'text2pron': text2pron, 'text2pos': text2pos}
    multi_task = tasks[sys.argv[6]]

    with open(src_in, 'r') as src_f, open(tgt_in, 'r') as tgt_f:
        src_text = src_f.read().strip().splitlines()
        tgt_text = tgt_f.read().strip().splitlines()
        if 'bpe' not in tgt_in:
            tgt_text = nlp.pipe(tgt_text)
        tgt_text = zip(tgt_text, tgt_text)

    multi_src = []
    multi_tgt = []
    multi_docs = []

    if simul == 'simul':
        for src_sent, tgt_sent in tqdm(zip(src_text, tgt_text)):
                multi_src.append(src_sent)
                multi_tgt.append(multi_task(src_sent, tgt_sent) + ' ' + text2text(src_sent, tgt_sent))      

    else:
        for tag, task in [('TASK', multi_task), ('TRANS', text2text)]:
            for src_sent, tgt_sent in tqdm(zip(src_text, tgt_text)):
                multi_docs.append(len(multi_tgt))
                multi_src.append('[{}] {}'.format(tag, src_sent))
                multi_tgt.append(task(src_sent, tgt_sent))  

    with open(src_out, 'w') as src_out_f, open(tgt_out, 'w') as tgt_out_f, open(docs_out, 'w') as docs_f:
        src_out_f.write('\n'.join(multi_src))
        tgt_out_f.write('\n'.join(multi_tgt))
        docs_f.write('\n'.join(multi_docs))
    