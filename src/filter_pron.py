import spacy
import sys

nlp = spacy.load("en_core_web_sm")

en_pro = {'i', 'my', 'me', 'mine', 'myself',
                'we', 'us', 'our', 'ours', 'ourselves',
                'you', 'your', 'yours', 'yourself', 'yourselves',
                'he', 'him', 'his', 'himself',
                'she', 'her', 'hers', 'herself',
                'they', 'them', 'their', 'theirs', 'themself', 'themselves',
                'it', 'its', 'itself'}

ja_pro = {'私', 'わたし', 'ワタシ', '私達', '僕', 'ぼく',
                'ボク', '僕ら', '俺', 'おれ', 'オレ', '俺ら',
                'あなた', 'あなた達', '貴方', 'あんた','貴様', '手前',
                'お前', 'おまえ','お前ら','君','きみ','キミ','君たち', '君たち',
                '彼', 'かれ', 'カレ', '彼ら',
                '彼女', 'かのじょ', 'カノジョ', '彼女たち', '彼女達'}


def filter(ja_file, en_file, en_file_untok, out_ja_file, out_en_file):
    with open(ja_file, 'r') as ja, open(en_file, 'r') as en, open(en_file_untok, 'r') as en_untok:
        ja_sents = ja.readlines()
        en_sents = en.readlines()
        en_untok_sents = en_untok.readlines()

    filtered_ja = []
    filtered_en = []

    for ja_sent, en_sent, en_untok_sent in zip(ja_sents, en_sents, en_untok_sents):
        if len(ja_pro.intersection(set(ja_sent.split()))) == 0:
            en_tok_count = 0
            for en_token in en_sent.split():
                if en_token in en_pro:
                    en_tok_count += 1
                    if en_tok_count > 1:
                        break
            if en_tok_count == 1:
                filtered_ja.append(ja_sent)
                filtered_en.append(en_untok_sent)

    assert(len(filtered_en) == len(filtered_ja))

    with open(out_ja_file, 'w') as f:
        f.write(''.join(filtered_ja))

    with open(out_en_file, 'w') as f:
        f.write(''.join(filtered_en))


def output_pronouns(readfile, outfile, single=False):
    output = []

    with open(readfile, 'r') as f:
        text = f.readlines()
        tokenized_text = []
        for sent in nlp.pipe(text):
            line_prons = []
            for token in sent:
                if token.text.lower() in en_pro:
                    line_prons.append(token.text.lower())
            if single:
                if len(line_prons) > 0:
                    output.append(line_prons[0])
                else:
                    output.append('error')
            else:
                output.append(' '.join(line_prons))

    with open(outfile, 'w') as f:
        f.write('\n'.join(output))


if __name__ == "__main__":
    # for ja_file, en_file, en_file_untok, out in [('pialign/train.tok.ja','pialign/train.tok.en', 'pialign/train.en', 'train'),
    #                          ('pialign/dev.tok.ja', 'pialign/dev.tok.en', 'pialign/dev.en', 'dev'),
    #                          ('pialign/test.tok.ja', 'pialign/test.tok.en', 'pialign/test.en', 'test')]:
    #     filter(ja_file, en_file, en_file_untok,'split/'+out+'.pron.tok.ja', 'split/'+out+'.pron.en')
    output_pronouns(sys.argv[1], sys.argv[2])
