mkdir pron_masked/vocab_all_HAN_enc

CUDA_VISIBLE_DEVICES=0 \
python3.5  /home2/mingjund/PronounMT/HAN_NMT/full_source/train.py \
    -data pron_masked/vocab_all_HAN/model \
    -save_model pron_masked/vocab_all_HAN_enc/model \
    -train_from pron_masked/vocab_all_HAN_base/model_acc_54.54_ppl_9.88_e22.pt \
    -encoder_type transformer \
    -decoder_type transformer \
    -enc_layers 6 \
    -dec_layers 6 \
    -label_smoothing 0.1 \
    -src_word_vec_size 512 \
    -tgt_word_vec_size 512 \
    -rnn_size 512 \
    -position_encoding \
    -dropout 0.1 \
    -batch_size 1024 \
    -start_decay_at 20 \
    -report_every 500 \
    -epochs 50 \
    -gpuid 0 \
    -max_generator_batches 32 \
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
    -param_init_glorot \
    -train_part all \
    -context_type HAN_enc \
    -context_size 3 

mkdir pron_masked/vocab_all_HAN_join

CUDA_VISIBLE_DEVICES=0 \
python3.5 /home2/mingjund/PronounMT/HAN_NMT/full_source/train.py \
    -data pron_masked/vocab_all_HAN/model \
    -save_model pron_masked/vocab_all_HAN_join/model \
    -train_from pron_masked/vocab_all_HAN_enc/model_acc_54.95_ppl_9.99_e11.pt \
    -encoder_type transformer \
    -decoder_type transformer \
    -enc_layers 6 \
    -dec_layers 6 \
    -label_smoothing 0.1 \
    -src_word_vec_size 512 \
    -tgt_word_vec_size 512 \
    -rnn_size 512 \
    -position_encoding \
    -dropout 0.1 \
    -batch_size 1024 \
    -start_decay_at 20 \
    -report_every 500 \
    -epochs 50 \
    -gpuid 0 \
    -max_generator_batches 32 \
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
    -param_init_glorot \
    -train_part all \
    -context_type HAN_join \
    -context_size 3 