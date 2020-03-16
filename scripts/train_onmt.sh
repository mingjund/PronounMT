onmt_preprocess \
    -train_src data/train.bpe.ko \
    -train_tgt data/train.bpe.en \
    -valid_src data/dev.bpe.ko \
    -valid_tgt data/dev.bpe.en \
    -save_data vocab_8000/ \
    -share_vocab \
    -src_vocab_size 8000 \
    -tgt_vocab_size 8000 \
    -share_vocab \
    -src_seq_length 1000 \
    -tgt_seq_length 1000 


CUDA_VISIBLE_DEVICES=1 
onmt_train \
    -data vocab_8000/ \
    -save_model vocab_8000_transformer/ \
    -train_from vocab_8000_transformer/_step_30000.pt \
    -word_vec_size 512 \
    -rnn_size 512 \
    -transformer_ff 2048 \
    -share_decoder_embeddings \
    -share_embeddings \
    -position_encoding \
    -encoder_type transformer \
    -decoder_type transformer \
    -layers 6 \
    -heads 8 \
    -param_init_glorot \
    -batch_size 8000 \
    -batch_type tokens \
    -max_generator_batches 2 \
    -train_steps 300000 \
    -dropout 0.1 \
    -normalization tokens \
    -optim adam \
    -adam_beta2 0.998 \
    -decay_method noam \
    -warmup_steps 16000 \
    -learning_rate 2 \
    -max_grad_norm 0 \
    -param_init 0 \
    -label_smoothing 0.1 \
    -early_stopping 5 \
    -valid_steps 5000 \
    -report_every 100 \
    -save_checkpoint_steps 5000 \
    -keep_checkpoint 4 \
    -log_file vocab_8000_transformer/training.log \
    -early_stopping_criteria accuracy \
    -gpu_ranks 0


onmt_translate \
    -gpu 0 \
    -model vocab_8000_transformer/_step_115000.pt \
    -src data/test.bpe.ko \
    -output vocab_8000_transformer/test_115000.bpe.out.en \
    -max_length 200 


python3 ../../src/desegment.py vocab_8000_transformer/test_115000.bpe.out.en vocab_8000_transformer/test_115000.out.en 


cat vocab_8000_transformer/test_115000.out.en | sacrebleu -w 2 data/test.en 