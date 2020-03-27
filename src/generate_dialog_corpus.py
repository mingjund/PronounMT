import os
import re
import tinysegmenter
from nltk.tokenize.treebank import TreebankWordDetokenizer


def detokenize(text):
    text = d.detokenize(text.split())
    text = text.replace(' .', '.')
    text = text.replace('...', '... ')
    text = text.replace(' ,', ',')
    text = text.replace(" '", "'")
    text = re.sub(r'\" (.*?) \"', r'"\1"', text)
    return text


def clean_speaker(text):
    speaker = []
    for word in re.sub(r'[\(\（].*?[\)\）]', '', text.strip().replace('continued', '')).split():
        if word not in speaker:
            speaker.append(word)
    return ' '.join(speaker)


def spk2turn(speakers, docs):
    turns = []
    docs = set(docs)

    for i in range(len(speakers)):
        if i == 0 or i in docs:
            turns.append('<new>')
        elif speakers[i] == 'UNK_SPK' or speakers[i-1] == 'UNK_SPK':
            turns.append('<unk_turn>')
        elif speakers[i] != speakers[i-1]:
            turns.append('<continued>')
        else:
            turns.append('<new>')
    
    return turns


def add2corpus(filename, speakers, ja_sents, en_sents, doc_boundaries):
    with open(filename) as f:
        for line in f:
            alignment = line.strip().split('|')
            if '' not in alignment:
                if alignment[1].strip() == '':
                    speakers.append('UNK_SPK')
                else:
                    speakers.append(clean_speaker(alignment[1]))
                ja_sents.append(' '.join(segmenter.tokenize(alignment[3])).strip())
                en_sents.append(alignment[4])
        doc_boundaries.append(str(len(speakers)))
    return speakers, ja_sents, en_sents, doc_boundaries


def write_corpus(outpath, split, speakers, ja_sents, en_sents, doc_boundaries):
    assert(len(speakers) == len(ja_sents) and 
        len(en_sents) == len(ja_sents) and 
        int(doc_boundaries[-1]) == len(speakers))    
    print('All {} set parts aligned!'.format(split))

    with open(outpath+split+'.spk', 'w', encoding='utf-8') as spk_f, \
        open(outpath+split+'.turn', 'w', encoding='utf-8') as turn_f, \
        open(outpath+split+'.ja', 'w', encoding='utf-8') as ja_f, \
        open(outpath+split+'.en', 'w', encoding='utf-8') as en_f, \
        open(outpath+split+'.docs', 'w', encoding='utf-8') as doc_f:
        spk_f.write('\n'.join(speakers))
        turn_f.write('\n'.join(spk2turn(speakers, doc_boundaries)))
        ja_f.write('\n'.join(ja_sents))
        en_f.write('\n'.join(en_sents))
        doc_f.write('\n'.join(doc_boundaries))
    print('Generated {} set files!'.format(split))


segmenter = tinysegmenter.TinySegmenter()
d = TreebankWordDetokenizer()

all_speakers = []
all_ja_sents = []
all_en_sents = []
all_doc_boundaries = []

train_speakers = []
train_ja_sents = []
train_en_sents = []
train_doc_boundaries = []

dev_speakers = []
dev_ja_sents = []
dev_en_sents = []
dev_doc_boundaries = []

test_speakers = []
test_ja_sents = []
test_en_sents = []
test_doc_boundaries = []

raw_path = '../../opensubs/en-ja_aligned_subtitles/'
clean_path = '../../opensubs/en-ja_speaker-sub_alignment/'

for drama in ['Amachan', 'Yutori', 'Nigehaji']:
    path = '../../subs/{}/script-sub_alignment/'.format(drama)
    for filename in os.listdir(path):
        all_speakers, all_ja_sents, all_en_sents, all_doc_boundaries = \
            add2corpus(path+filename, all_speakers, all_ja_sents, all_en_sents, all_doc_boundaries)
        if (drama == 'Nigehaji' and (filename.startswith('008') or filename.startswith('009'))) \
        or (drama == 'Yutori' and (filename.startswith('007') or filename.startswith('008'))):
            dev_speakers, dev_ja_sents, dev_en_sents, dev_doc_boundaries = \
                add2corpus(path+filename, dev_speakers, dev_ja_sents, dev_en_sents, dev_doc_boundaries)
        elif (drama == 'Nigehaji' and (filename.startswith('010') or filename.startswith('011'))) \
        or (drama == 'Yutori' and (filename.startswith('009') or filename.startswith('010'))):
            test_speakers, test_ja_sents, test_en_sents, test_doc_boundaries = \
                add2corpus(path+filename, test_speakers, test_ja_sents, test_en_sents, test_doc_boundaries)
        else:
            train_speakers, train_ja_sents, train_en_sents, train_doc_boundaries = \
                add2corpus(path+filename, train_speakers, train_ja_sents, train_en_sents, train_doc_boundaries)

for filename in os.listdir(clean_path):
    if filename.endswith("-t") and not filename.startswith('1462758'):
        with open(raw_path+filename.replace('-alignment.txt-t', '.en')) as raw_en, \
             open(raw_path+filename.replace('-alignment.txt-t', '.ja')) as raw_ja, \
             open(clean_path+filename) as clean_en, \
             open(clean_path+filename.replace('-t','-s')) as speaker_f:

            raw_en_text = raw_en.read().strip().split('\n')
            raw_en_len = len(raw_en_text)
            raw_ja_text = re.sub(r' (?! )', '', raw_ja.read().strip()).split('\n')
            clean_en_text = clean_en.read().strip().split('\n')
            speaker_list = speaker_f.read().strip().split('\n')

            prev_raw_i = raw_i = 0

            for clean_i in range(len(speaker_list)):
                while raw_i < raw_en_len and raw_en_text[raw_i] not in clean_en_text[clean_i]:
                    raw_i += 1

                if raw_i == raw_en_len:
                    raw_i = prev_raw_i
                    while raw_en_text[raw_i] not in clean_en_text[clean_i] and raw_i > 0:
                        raw_i -= 1          

                clean_en_text[clean_i].replace(raw_en_text[raw_i], '')
                train_speakers.append(clean_speaker(speaker_list[clean_i]))
                train_ja_sents.append(' '.join(segmenter.tokenize(raw_ja_text[raw_i])).strip())
                train_en_sents.append(detokenize(raw_en_text[raw_i]))

                all_speakers.append(clean_speaker(speaker_list[clean_i]))
                all_ja_sents.append(' '.join(segmenter.tokenize(raw_ja_text[raw_i])).strip())
                all_en_sents.append(detokenize(raw_en_text[raw_i]))

                prev_raw_i = raw_i

            train_doc_boundaries.append(str(len(train_speakers)))
            all_doc_boundaries.append(str(len(all_speakers)))

all_data = False
if all_data:
    directory = '../../opensubs/en-ja_all/'
    outpath = '../../dialog_corpus/en-ja_all/data/'
    for filename in os.listdir(directory):
        if filename.endswith(".en") and (filename.replace('.en', '-alignment.txt-t') not in set(os.listdir(clean_path))):
            with open(directory+filename, 'r') as src_f, open(directory+filename.replace('.en', '.ja'), 'r') as tgt_f:
                src_text = [line.strip() for line in src_f.read().strip().split('\n')]
                tgt_text = [line.strip() for line in tgt_f.read().strip().split('\n')]

                train_en_sents += src_text
                train_ja_sents += tgt_text
                train_speakers += ['<UNK_SPK>']*len(src_text)
                train_doc_boundaries.append(str(len(train_en_sents)))

                all_en_sents += src_text
                all_ja_sents += tgt_text
                all_speakers += ['<UNK_SPK>']*len(src_text)
                all_doc_boundaries.append(str(len(all_en_sents)))
else:
    outpath = '../../dialog_corpus/en-ja/data/'

write_corpus(outpath, 'all', all_speakers, all_ja_sents, all_en_sents, all_doc_boundaries)
write_corpus(outpath, 'train', train_speakers, train_ja_sents, train_en_sents, train_doc_boundaries)
write_corpus(outpath, 'dev', dev_speakers, dev_ja_sents, dev_en_sents, dev_doc_boundaries)
write_corpus(outpath, 'test', test_speakers, test_ja_sents, test_en_sents, test_doc_boundaries)

