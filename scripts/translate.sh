echo src data/test.bpe.$3
echo tgt $2.bpe.out.$4
echo docs data/test.$5

if [ ! -f $2.out.$4 ] && [ ! -f $2.bpe.out.$4 ]; then 
  CUDA_VISIBLE_DEVICES=$1 \
  python3 /home/mingjund/PronounMT/HAN_NMT/full_source/translate.py \
    -model $2.pt \
    -src data/test.bpe.$3 \
    -doc data/test.$5 \
    -output $2.bpe.out.$4 \
    -translate_part all \
    -batch_size 100 \
    -gpu 0
fi

if [ ! -f $2.out.$4 ]; then
python3 /home/mingjund/PronounMT/code/src/desegment.py  $2.bpe.out.$4  $2.out.$4
fi

echo $2 >> $6
cat $2.out.$4 | sacrebleu -w 2 data/test.$4 >> $6
