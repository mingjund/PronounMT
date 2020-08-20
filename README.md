# Improving Pronoun Translation for Prodrop Languages

## Script-Sub-Sub Alignment for Speaker Labeling
This repo provides code for aligning subtitles in the `.ass` format of two different languages based on timestamps - **sub-sub alignment** and aligning scripts to subtitles for multiple episodes of TV series - **script-sub alignment**.

Required Python libraries: `pysubs2`, `pykakasi`, `jaconv`, `nltk`.

### Sub-Sub Alignment
ASS format subtitles of two different languages can be aligned based on timestamps using the command below. Successfully aligned subtitles will appear at the same line number in their respective output files.

Example:

```
python src/sub-sub_align.py \
    --src_subs Nigehaji_en \        # source language subtitle dir 
    --tgt_subs Nigehaji_ja \        # target language subtitle dir
    --drama_len 11 \                # total number of episodes (number of subtitle files per language)
    --src_out test_en_aligned \     # aligned src_subs output dir
    --tgt_out test_ja_aligned \     # aligned tgt_subs output dir
    --src_sub_style Default,Past \  # src_sub subtitle style(s) 
    --tgt_sub_style Default         # tgt_sub subtitle style(s) 
```

Files in `src_subs` and `tgt_subs` should be named *raw_ep1.ass*, *raw_ep2.ass*, *raw_ep3.ass*...

### Script-Sub Alignment
The script of a full TV series can be aligned to the subtitles of each episide using the command below.

Example:
```
python src/script-sub_align.py \
    --script Nigehaji-script.txt \                              # path to script file
    --subs test_ja_aligned \                                    # subtitles dir
    --foreign_subs test_en_aligned \                            # foreign language subtitles dir (optional)
    --output test_alignment \                                   # alignment output dir
    --drama_len 11 \                                            # total number of episodes   
    --ep_delimiter '\n\n\n\n\n１　.*\n\n\n\n\n\n' \              # regex delimiter betweeen episodes in script
    --scene_delimiter '\n\n\n\n\n[０-９0-9]*　.*\n\n\n\n\n\n' \  # regex delimiter betweeen scenes in script
    --window_k 30 \                                             # size of window: look for next matching sentence within +/- window_k number of sentences
    --tri_thres 0.4 \                                           # minimum proportion of trigram token matches between script and sub
    --bi_thres 0.5                                              # minimum proportion of bigram token matches between script and sub
```