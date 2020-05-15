import os
import sys

def docs2corpus(input_dir,  output_prefix, src_ext, tgt_ext):
    src_texts = []
    tgt_texts = []
    docs = ['0']

    for filename in os.listdir(input_dir):
        if filename.endswith(".np.tk.qb.es.zh") :
            with open(input_dir+filename, 'r') as raw_src, \
                open(input_dir+filename.replace(".np.tk.qb.es.zh", ".qb.np.tk.lc.en"), 'r') as raw_tgt:

                src_doc = raw_src.read().strip().split('\n')
                tgt_doc = raw_tgt.read().strip().split('\n')

                assert(len(src_doc) == len(tgt_doc))

                src_texts += src_doc              
                tgt_texts += tgt_doc
                docs.append(str(len(tgt_texts)))

    with open(output_prefix+'.'+src_ext, 'w') as src_all,\
        open(output_prefix+'.'+tgt_ext, 'w') as tgt_all,\
        open(output_prefix+'.docs', 'w') as docs_all:
        src_all.write('\n'.join(src_texts))
        tgt_all.write('\n'.join(tgt_texts))
        docs_all.write('\n'.join(docs))

docs2corpus(sys.argv[1], sys.argv[2], sys.argv[3], sys.argv[4])