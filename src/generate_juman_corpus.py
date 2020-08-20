# coding: utf-8
from __future__ import unicode_literals # It is not necessary when you use python3.
from pyknp import Juman
import sys
import argparse
jumanpp = Juman()   # default is JUMAN++: Juman(jumanpp=True). if you use JUMAN, use Juman(jumanpp=False)

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument('--text_file', type=str, default="data/test.ja")
    parser.add_argument('--spk_file', type=str, default="data/test.bpe.spk_ja")
    parser.add_argument('--out_file', type=str, default="data/test.bpe.multi_juman_ja")
    parser.add_argument('--feat_only', action='store_true')

    args = parser.parse_args()

    with open(args.text_file, 'r') as in_f:
        in_text = in_f.read().replace('  ', '▁').replace(' ','').replace('▁', ' ').splitlines()

    with open(args.spk_file, 'r') as spk_f:
        spk_text = [line.split('\t')[0].split() for line in spk_f.read().replace('][', '] [').splitlines()]


    if args.feat_only:
        feats = []
        raw_text = []

        for line in in_text:
            result = jumanpp.analysis(line)
            if 'train' in args.text_file:
                feats.append(' '.join([mrph.bunrui for mrph in result.mrph_list()])+'\n')       
            raw_text.append(' '.join([mrph.midasi for mrph in result.mrph_list()])+'\n')    

        # for spk,out in zip(spk_text, feats):
        #     print(spk, out)

        spk_text = [' '.join([spk for spk in line]) for line in spk_text]
        # if feats != []:
        #     feats = [spk+' '+out for spk,out in zip(spk_text, feats)]
        raw_text = [spk+' '+out for spk,out in zip(spk_text, raw_text)]

        with open(args.out_file, 'w') as out_f:
            if 'train' in args.text_file:
                out_f.writelines(['[MULTI] '+line for line in raw_text]+['[TRANS] '+line for line in raw_text])
            else:
                out_f.writelines(['[TRANS] '+line for line in raw_text])

        if 'train' in args.text_file:
            with open(args.out_file.replace('ja', 'feats'), 'w') as out_f:
                out_f.writelines(feats)
        
    else:
        out_text = []
        for line in in_text:
            result = jumanpp.analysis(line)
            out_text.append(' '.join([mrph.midasi+'￨'+mrph.bunrui for mrph in result.mrph_list()])+'\n') # 各形態素にアクセス
                # print("見出し:%s, 読み:%s, 原形:%s, 品詞:%s, 品詞細分類:%s, 活用型:%s, 活用形:%s, 意味情報:%s, 代表表記:%s" \
                #         % (mrph.midasi, mrph.yomi, mrph.genkei, mrph.hinsi, mrph.bunrui, mrph.katuyou1, mrph.katuyou2, mrph.imis, mrph.repname))

        spk_feats = []
        for line in spk_text:
            spk_feats.append(' '.join([spk+'￨spk' for spk in line]))
        

        with open(args.out_file, 'w') as out_f:
            out_f.writelines([spk+' '+out for spk,out in zip(spk_feats, out_text)])

            
