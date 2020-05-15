# Apply BPE
for split in back_trans_e22_train.out #train dev test
do
    for l in $3 $4
    do
        python3 /home/mingjund/PronounMT/code/src/subwords.py segment \
        --model $1/subwords.model \
        < $2/$split.$l \
        > $2/$split.bpe.$l
    done
done
