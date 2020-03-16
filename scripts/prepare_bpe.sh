# Prepare BPE
python3 src/subwords.py train \
--model_prefix OpenSubtitles/en-ko/data/subwords \
--vocab_size 8000 \
--model_type bpe \
--input OpenSubtitles/en-ko/data/train.en,OpenSubtitles/en-ko/data/train.ko

# Apply BPE
for split in train dev test
do
    for l in ko en
    do
        python3 src/subwords.py segment \
        --model OpenSubtitles/en-ko/data/subwords.model \
        < OpenSubtitles/en-ko/data/$split.$l \
        > OpenSubtitles/en-ko/data/$split.bpe.$l
    done
done
