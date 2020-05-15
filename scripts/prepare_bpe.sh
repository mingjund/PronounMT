# Prepare BPE
python3 /home/mingjund/PronounMT/code/src/subwords.py train \
--model_prefix $1/subwords \
--vocab_size $4 \
--model_type bpe \
--input $1/train.$2,$1/train.$3

# Apply BPE
for split in train dev test
do
    for l in $2 $3
    do
        python3 /home/mingjund/PronounMT/code/src/subwords.py segment \
        --model $1/subwords.model \
        < $1/$split.$l \
        > $1/$split.bpe.$l
    done
done
