import pysubs2
import pickle
import re
from tqdm import tqdm
import argparse
import os


def process_file(path_src, path_tgt, outpath, args):
    src_subs_raw = pysubs2.load(args.src_subs + '/' + path_src)
    tgt_subs_raw = pysubs2.load(args.tgt_subs + '/' + path_tgt)


    src_pointer = 0
    tgt_pointer = 0

    src_subs = []
    tgt_subs = []

    for sub in src_subs_raw:
        if (sub.type == "Dialogue" and sub.style in args.src_sub_style.split(',')):
            sub.text = re.sub(r'\{.*?\}', '', sub.text)
            sub.text = re.sub(r'\\N', ' ', sub.text)
            src_subs.append(sub)

    for sub in tgt_subs_raw:
        if (sub.type == "Dialogue" and sub.style in args.tgt_sub_style.split(',')):
            sub.text = re.sub(r'\（.*?\）', '', sub.text)
            sub.text = re.sub(r'\\N', ' ', sub.text)
            tgt_subs.append(sub)
    print("File1: %s, file2: %s, outpath: %s" %(path_tgt, path_src, outpath))
    print("num src subs ", len(src_subs))
    print("num tgt subs ", len(tgt_subs))

    # for each line of japanese text, match one or more english text
    unmatched_tgt = list(range(len(tgt_subs)))
    unmatched_src = list(range(len(src_subs)))
    match_dict = dict()
    for i in range(len(unmatched_tgt)):
        tgt_sub = tgt_subs[i]
        aligned_src = []

        for j in range(len(unmatched_src)):
            src_num = unmatched_src[j]
            src_sub = src_subs[src_num]
            if (src_sub.start > tgt_sub.end):
                break
            if (src_sub.start > tgt_sub.start - 1000 and \
                src_sub.end < tgt_sub.end + 1000):
                aligned_src.append(src_num)
        
        if (len(aligned_src) != 0):
            match_dict[i] = aligned_src
        for j in aligned_src:
            unmatched_src.remove(j)
    
    all_tgt = open(args.tgt_out + '/' + outpath, "w", encoding='utf-8')
    all_src = open(args.src_out + '/' + outpath, "w", encoding='utf-8')
    #src_matched_subs = pysubs2.load("blank.ass")
    linecount = 0
    for i in range(len(tgt_subs)):
        if (not i in match_dict):
            all_tgt.write(tgt_subs[i].text + "\n")
            all_src.write("\n")
            continue
        else:
            src_sub = src_subs[match_dict[i][0]]
            if (len(match_dict[i]) > 1):
                for j in match_dict[i][1:]:
                    new_sub = src_subs[j]
                    if (new_sub.end > src_sub.end):
                        src_sub.end = new_sub.end
                    src_sub.text = src_sub.text + " " + new_sub.text

            #src_matched_subs.insert(linecount, tgt_subs[i])
            #src_matched_subs.insert(linecount+1, src_sub)
            linecount += 2
            all_tgt.write(tgt_subs[i].text + "\n")
            src_out = src_sub.text.replace("\n", " ")
            all_src.write(src_out + "\n")
    all_tgt.close()
    all_src.close()
        
    return linecount/2
    
# args.src_subs = "../subs/Nigehaji/Nigehaji_src/"
# args.tgt_subs = "../subs/Nigehaji/Nigehaji_tgt/"
# args.src_out = "../subs/Nigehaji/en-ja_alignment/src_txt/"
# args.tgt_out = "../subs/Nigehaji/en-ja_alignment/jp_txt/"
# args.tgt_sub_style = ["Default"]
# args.src_sub_style = ["Default", "Past"]

if __name__ == '__main__':
    parser = argparse.ArgumentParser()   
    parser.add_argument('--src_subs', type=str, required=True)
    parser.add_argument('--tgt_subs', type=str, required=True)
    parser.add_argument('--drama_len', type=int, required=True)
    parser.add_argument('--src_out', type=str, default='aligned_src') 
    parser.add_argument('--tgt_out', type=str, default='aligned_tgt')
    parser.add_argument('--src_sub_style', type=str, default="Default")
    parser.add_argument('--tgt_sub_style', type=str, default="Default")
    args = parser.parse_args()  

    if not os.path.isdir(args.src_out):
        os.mkdir(args.src_out)

    if not os.path.isdir(args.tgt_out):
        os.mkdir(args.tgt_out)

    #ja_allfilenames = open("ja_filenames.txt", "r").readlines()
    total_lines = 0
    for i in tqdm(range(1, args.drama_len+1)):
        src_filename = "Nigeru wa Haji da ga Yaku ni Tatsu ep{:0>2d} (848x480 x264).ass".format(i)
        tgt_filename = "Nigehaji_ja_ep{}.ass".format(i)
        print("src_filename: {}, tgt_filename: {}".format(src_filename, tgt_filename))
        out_filename = "aligned_ep{}.txt".format(i)
        total_lines += process_file(src_filename, tgt_filename, out_filename, args)

    print(total_lines)

