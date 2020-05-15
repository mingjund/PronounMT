import sys

with open(sys.argv[1], 'r') as src, open(sys.argv[2], 'r') as tgt:
    src_text = src.readlines()
    tgt_text = tgt.read().lower().splitlines()

    new_src, new_tgt = zip(*set(zip(src_text, tgt_text)))

with open(sys.argv[3], 'w') as new_src_f, open(sys.argv[4], 'w') as new_tgt_f:
    new_src_f.writelines(new_src)
    new_tgt_f.write('\n'.join(new_tgt))