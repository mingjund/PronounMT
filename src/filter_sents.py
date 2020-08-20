import sys
import argparse


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
                'お前', 'おまえ','お前ら','君','きみ','キミ','君たち', '君たち',
                '彼', 'かれ', 'カレ', '彼ら',
                '彼女', 'かのじょ', 'カノジョ', 'かのじょたち', '彼女たち', '彼女達'}


def filter_prodrop(ja_file, en_file, en_file_untok, out_ja_file, out_en_file):
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


def filter_prosents(in_src, in_src_bpe, in_tgt, out_src, out_src_bpe, out_tgt):
    with open(in_src, 'r') as f_src, open(in_src_bpe, 'r') as f_src_bpe, open(in_tgt, 'r') as f_tgt:
        src_lines = f_src.readlines()
        src_bpe_lines = f_src_bpe.readlines()
        tgt_lines = f_tgt.readlines()
        prosent_indices = [i for i, line in enumerate(src_lines) if len(ja_pro.intersection(set(line.split()))) > 0]

    with open(out_src, 'w') as f_src, open(out_src_bpe, 'w') as f_src_bpe, open(out_tgt, 'w') as f_tgt:
        f_src.writelines([src_lines[i] for i in prosent_indices])
        f_src_bpe.writelines([src_bpe_lines[i] for i in prosent_indices])
        f_tgt.writelines([tgt_lines[i] for i in prosent_indices])


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument('--mode', choices=['prodrops', 'prosents'], default='prosents')
    parser.add_argument('--in_src', type=str)
    parser.add_argument('--in_src_bpe', type=str)
    parser.add_argument('--in_tgt', type=str)
    parser.add_argument('--out_src', type=str)
    parser.add_argument('--out_src_bpe', type=str)
    parser.add_argument('--out_tgt', type=str)

    args = parser.parse_args()
    # for ja_file, en_file, en_file_untok, out in [('pialign/train.tok.ja','pialign/train.tok.en', 'pialign/train.en', 'train'),
    #                          ('pialign/dev.tok.ja', 'pialign/dev.tok.en', 'pialign/dev.en', 'dev'),
    #                          ('pialign/test.tok.ja', 'pialign/test.tok.en', 'pialign/test.en', 'test')]:
    #     filter(ja_file, en_file, en_file_untok,'split/'+out+'.pron.tok.ja', 'split/'+out+'.pron.en')

    if args.mode == 'prodrops':
        pass
    elif args.mode == 'prosents':
        filter_prosents(args.in_src, args.in_src_bpe, args.in_tgt, args.out_src, args.out_src_bpe, args.out_tgt)
