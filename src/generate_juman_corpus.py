# coding: utf-8
from __future__ import unicode_literals # It is not necessary when you use python3.
from pyknp import Juman
import sys
jumanpp = Juman()   # default is JUMAN++: Juman(jumanpp=True). if you use JUMAN, use Juman(jumanpp=False)

import sys
with open(sys.argv[1], 'r') as in_f:
    in_text = in_f.read().replace('  ', '▁').replace(' ','').replace('▁', ' ').splitlines()

out_text = []
for line in in_text:
    result = jumanpp.analysis(line)
    out_text.append(' '.join([mrph.midasi+'￨'+mrph.bunrui for mrph in result.mrph_list()])+'\n') # 各形態素にアクセス
        # print("見出し:%s, 読み:%s, 原形:%s, 品詞:%s, 品詞細分類:%s, 活用型:%s, 活用形:%s, 意味情報:%s, 代表表記:%s" \
        #         % (mrph.midasi, mrph.yomi, mrph.genkei, mrph.hinsi, mrph.bunrui, mrph.katuyou1, mrph.katuyou2, mrph.imis, mrph.repname))

with open(sys.argv[3], 'r') as spk_f:
    spk_text = [line.split('\t')[0].split() for line in spk_f.read().replace('][', '] [').splitlines()]

spk_feats = []
for line in spk_text:
    spk_feats.append(' '.join([spk+'￨spk' for spk in line]))


with open(sys.argv[2], 'w') as out_f:
    out_f.writelines([spk+' '+out for spk,out in zip(spk_feats, out_text)])