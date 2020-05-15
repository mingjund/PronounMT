import sys
import tinysegmenter
import pkuseg
from sklearn.model_selection import train_test_split

ja_seg = tinysegmenter.TinySegmenter()
zh_seg = pkuseg.pkuseg() 

filename = sys.argv[1]
out_path = sys.argv[2]
src_ext = sys.argv[3]
tgt_ext = sys.argv[4]
tok = sys.argv[5]
    

with open(filename+'.'+src_ext, 'r') as src, open(filename+'.'+tgt_ext, 'r') as tgt:
    X = [' '.join(ja_seg.tokenize(line)).strip() for line in src.readlines()]
    y = [' '.join(zh_seg.cut(line)).strip() for line in tgt.readlines()]

    X_train_dev, X_test, y_train_dev, y_test = train_test_split(X, y, test_size=2000)
    X_train, X_dev, y_train, y_dev = train_test_split(X_train_dev, y_train_dev, test_size=2000)

if tok == 'tok':
    src_ext = 'tok.'+src_ext
    tgt_ext = 'tok.'+tgt_ext
    
with open(out_path+'train.'+src_ext, 'w') as train_src, open(out_path+'train.'+tgt_ext, 'w') as train_tgt:
    train_src.write('\n'.join(X_train))
    train_tgt.write('\n'.join(y_train))

with open(out_path+'dev.'+src_ext, 'w') as dev_src, open(out_path+'dev.'+tgt_ext, 'w') as dev_tgt:
    dev_src.write('\n'.join(X_dev))
    dev_tgt.write('\n'.join(y_dev))

with open(out_path+'test.'+src_ext, 'w') as test_src, open(out_path+'test.'+tgt_ext, 'w') as test_tgt:
    test_src.write('\n'.join(X_test))
    test_tgt.write('\n'.join(y_test))
