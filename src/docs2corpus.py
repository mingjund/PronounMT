import os
import sys
from collections import defaultdict

def docs2corpus(input_dir,  output_dir, src_ext, tgt_ext):
    src_sents = defaultdict(list)
    tgt_sents = defaultdict(list)
    doc_boundaries = defaultdict(list)

    splits = ['dev', 'test', 'train']
    idx = 0

    for filename in os.listdir(input_dir)[::-1]:
        if filename.endswith(src_ext) :
            with open(input_dir+filename, 'r') as raw_src, \
                open(input_dir+filename.replace(src_ext, tgt_ext), 'r') as raw_tgt:

                src_doc = raw_src.read().strip().split('\n')
                tgt_doc = raw_tgt.read().strip().split('\n')

                assert(len(src_doc) == len(tgt_doc))

                doc_boundaries[splits[idx]].append(str(len(tgt_sents[splits[idx]])))
                src_sents[splits[idx]] += src_doc              
                tgt_sents[splits[idx]] += tgt_doc

                if splits[idx] != 'train' and len(tgt_sents[splits[idx]]) > 2000:
                    idx += 1


    for split in splits:
        with open(output_dir+split+'.'+src_ext, 'w') as src_out,\
            open(output_dir+split+'.'+tgt_ext, 'w') as tgt_out,\
            open(output_dir+split+'.docs', 'w') as docs_out:
            src_out.write('\n'.join(src_sents[split]))
            tgt_out.write('\n'.join(tgt_sents[split]))
            docs_out.write('\n'.join(doc_boundaries[split]))

docs2corpus(sys.argv[1], sys.argv[2], sys.argv[3], sys.argv[4])