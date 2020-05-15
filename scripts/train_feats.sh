mkdir -p $2

onmt_preprocess \
    -train_src data/train.$3 \
    -train_tgt data/train.bpe.$4 \
    -valid_src data/dev.$3 \
    -valid_tgt data/dev.bpe.$4 \
    -save_data $2/model \
    -src_vocab_size 0 \
    -src_words_min_frequency 2 \
    -tgt_vocab_size 8100 \
    #-src_seq_length 80 \
    #-tgt_seq_length 80

mkdir -p ${2}_base

CUDA_VISIBLE_DEVICES=$1 \
onmt_train \
    -data ${2}/model \
    -save_model ${2}_base/model \
    -encoder_type transformer \
    -decoder_type transformer \
    -feat_vec_size 3 \
    -enc_layers 6 \
    -dec_layers 6 \
    -label_smoothing 0.1 \
    -src_word_vec_size 512 \
    -tgt_word_vec_size 512 \
    -rnn_size 512 \
    -position_encoding \
    -dropout 0.1 \
    -batch_size 4096 \
    -report_every 500 \
    -train_steps 1000000 \
    -max_generator_batches 16 \
    -batch_type tokens \
    -normalization tokens \
    -accum_count 4 \
    -optim adam \
    -adam_beta2 0.998 \
    -decay_method noam \
    -warmup_steps 8000 \
    -learning_rate 2 \
    -max_grad_norm 0 \
    -param_init 0 \
    -param_init_glorot  \
    -early_stopping 5 \
    -valid_steps 5000 \
    -report_every 100 \
    -save_checkpoint_steps 5000 \
    -keep_checkpoint 5 
