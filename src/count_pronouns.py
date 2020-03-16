from collections import Counter
import spacy
import re

nlp = spacy.load('en')

en_pron = ['i', 'my', 'me', 'mine', 'myself',
                'we', 'us', 'our', 'ours', 'ourselves',
                'you', 'your', 'yours', 'yourself', 'yourselves',
                'he', 'him', 'his', 'himself',
                'she', 'her', 'hers', 'herself',
                'they', 'them', 'their', 'theirs', 'themself', 'themselves',
                'it', 'its', 'itself']


def count_prons(file, outfile):
    with open(file, 'r') as rf, open(outfile, 'w') as wf:
        print('processing '+file)
        wf.write('{:10}\t{}\n\n'.format('Pronoun', '% in corpus'))
        total_per = 0
        text = rf.read().lower().split('\n')
        tok_text = [token.text for sent in nlp.pipe(text) for token in sent]
        vocab = Counter(tok_text)
        doc_len = len(tok_text)

        for pron in en_pron:
            per = vocab[pron]/doc_len
            wf.write('{:10}\t{:.9f}\n'.format(pron, per))
            total_per += per
    
        wf.write('\n{:10}\t{:.9f}'.format('Total', total_per))

count_prons('../en_subs/friends_all.en', '../results/Friends_pron_stats.txt')
count_prons('../en_subs/Amachan_all_clean.en', '../results/Amachan_pron_stats.txt')
count_prons('../JESC/data/train.en', '../results/JESC_pron_stats.txt')
count_prons('../opensubs/en-ko/data/OpenSubtitles.en-ko.en', '../results/opensubs_en-ko_pron_stats.txt')
count_prons('../opensubs/en-ja/data/OpenSubtitles.en-ja.en', '../results/opensubs_en-ja_pron_stats.txt')