import unicodedata
from langdetect import DetectorFactory, detect, detect_langs
import re
import tinysegmenter
import spacy


def cjk_detect(texts):
    # korean
    if re.search("[\uac00-\ud7a3]", texts):
        return "ko"
    # japanese
    if re.search("[\u3040-\u30ff]", texts):
        return "ja"
    # chinese
    if re.search("[\u4e00-\u9FFF]", texts):
        return "zh"
    return None

DetectorFactory.seed = 0
segmenter = tinysegmenter.TinySegmenter()
nlp = spacy.load("en_core_web_sm")

def fast_align_split():
    for file in ['test', 'dev', 'train']:
        with open('split/'+file, 'r') as f:
            print('converting '+file+'...')
            text = f
            new_text_en = []
            new_text_ja = []
            new_text = []

            for line in text:
                en = True
                new_line_en = []
                new_line_ja = []
                for token in line.split():
                    #print(token)
                    if en:
                        if cjk_detect(token) == None:
                            new_line_en.append(token)
                        else:
                            en = False
                            new_line_ja.append(token)
                    else:
                        new_line_ja.append(token)

                new_line_en = ' '.join(new_line_en)
                new_line_ja = ' '.join(segmenter.tokenize(' '.join(new_line_ja)))

                new_text_en.append(new_line_en)
                new_text_ja.append(' ||| ' + new_line_ja)

            count = 0
            for sent_en, sent_ja in zip(nlp.pipe(new_text_en), new_text_ja):
                new_text.append(' '.join([token.text for token in sent_en]) + sent_ja)
                count +=1
                if count % 5000 == 0:
                    print(count)

        with open('fast_align/'+file, 'w') as f:
            f.write('\n'.join(new_text))
            print('done')


def tokenize(file, new_file):
    with open(file, 'r') as f:
        text = f.readlines()
        tokenized_text = []
        for sent in nlp.pipe(text):
            tokenized_text.append(' '.join([token.text for token in sent]))

    with open(new_file, 'w') as f:
        f.write(''.join(tokenized_text))


def separate_files():
    for file in ['test', 'dev', 'train']:
        with open('fast_align/'+file, 'r') as f:
            print('converting '+file+'...')
            text = f
            new_text_en = []
            new_text_ja = []
            for line in text:
                en, ja = line.split(' ||| ')
                new_text_en.append(en)
                new_text_ja.append(ja)

        with open('pialign/'+file+'.tok.en', 'w') as f:
            f.write('\n'.join(new_text_en))
            print('en done')

        with open('pialign/'+file+'.tok.ja', 'w') as f:
            f.write(''.join(new_text_ja))
            print('ja done')

def MT_split():
    for file in ['test', 'dev', 'train']:
        with open('split/'+file, 'r') as f:
            print('converting '+file+'...')
            text = f
            new_text_en = []
            new_text_ja = []
            new_text = []

            for line in text:
                en = True
                new_line_en = []
                new_line_ja = []
                for token in line.split():
                    #print(token)
                    if en:
                        if cjk_detect(token) == None:
                            new_line_en.append(token)
                        else:
                            en = False
                            new_line_ja.append(token)
                    else:
                        new_line_ja.append(token)

                new_line_en = ' '.join(new_line_en)
                #new_line_ja = ' '.join(segmenter.tokenize(' '.join(new_line_ja)))

                new_text_en.append(new_line_en)
                #new_text_ja.append(new_line_ja)

        with open('pialign/'+file+'.en', 'w') as f:
            f.write('\n'.join(new_text_en))
            print('en done')

        #with open('pialign/'+file+'.ja', 'w') as f:
            #f.write('\n'.join(new_text_ja))
            #print('ja done')

def swap_src_tgt():
    for file in ['test', 'dev', 'train']:
        with open('fast_align/'+file+'.en-ja', 'r') as f:
            print('converting '+file+'...')
            text = f.readlines()
            new_text = []
            for line in text:
                en, ja = line.split(' ||| ')
                new_text.append(' ||| '.join([ja.strip(),en]))

        with open('fast_align/'+file+'.ja-en', 'w') as f:
            f.write('\n'.join(new_text))
            print('done')


if __name__ == "__main__":
    #MT_split()
    #separate_files()
    #swap_src_tgt()

    tokenize('pialign/test_65000.full_sent.pron.out.en', 'pialign/test_65000.full_sent.pron.out.tok.en')
