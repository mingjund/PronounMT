# Prepare BPE
python subwords.py train \
--model_prefix JESC/pialign/subwords \
--vocab_size 8000 \
--model_type bpe \
--input JESC/pialign/train.en,JESC/pialign/train.ja

# Apply BPE
for split in train dev test
do
    for l in ja en
    do
        python subwords.py segment \
        --model JESC/pialign/subwords.model \
        < JESC/pialign/$split.$l \
        > JESC/pialign/$split.bpe.$l
    done
done