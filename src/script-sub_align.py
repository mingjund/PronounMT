import pysubs2
import pickle
import re
from tqdm import tqdm


eng_folder = "../subs/Nigehaji/Nigehaji_en/"
jap_folder = "../subs/Nigehaji/Nigehaji_ja/"
out_folder = "../subs/Nigehaji/Nigehaji_aligned_jap_eng/"
out_en_folder = "../subs/Nigehaji/en-ja_alignment/eng_txt/"
out_jp_folder = "../subs/Nigehaji/en-ja_alignment/jp_txt/"
ja_dia_style = ["Default"]
eng_dia_style = ["Default", "Past"]


def process_file(path_jp, path_eng, outpath):
    eng_sub_raw = pysubs2.load(eng_folder + path_eng)
    jap_subs_raw = pysubs2.load(jap_folder + path_jp)


    eng_pointer = 0
    jap_pointer = 0

    eng_subs = []
    jap_subs = []

    for sub in eng_sub_raw:
        if (sub.type == "Dialogue" and sub.style in eng_dia_style):
            sub.text = re.sub(r'\{.*?\}', '', sub.text)
            sub.text = re.sub(r'\\N', ' ', sub.text)
            eng_subs.append(sub)

    for sub in jap_subs_raw:
        if (sub.type == "Dialogue" and sub.style in ja_dia_style):
            sub.text = re.sub(r'\（.*?\）', '', sub.text)
            sub.text = re.sub(r'\\N', ' ', sub.text)
            jap_subs.append(sub)
    print("File1: %s, file2: %s, outpath: %s" %(path_jp, path_eng, outpath))
    print("num eng subs ", len(eng_subs))
    print("num jap subs ", len(jap_subs))

    # for each line of japanese text, match one or more english text
    unmatched_jap = list(range(len(jap_subs)))
    unmatched_eng = list(range(len(eng_subs)))
    match_dict = dict()
    for i in range(len(unmatched_jap)):
        jap_sub = jap_subs[i]
        aligned_eng = []

        for j in range(len(unmatched_eng)):
            eng_num = unmatched_eng[j]
            eng_sub = eng_subs[eng_num]
            if (eng_sub.start > jap_sub.end):
                break
            if (eng_sub.start > jap_sub.start - 1000 and \
                eng_sub.end < jap_sub.end + 1000):
                aligned_eng.append(eng_num)
        
        if (len(aligned_eng) != 0):
            match_dict[i] = aligned_eng
        for j in aligned_eng:
            unmatched_eng.remove(j)
    
    all_ja = open(out_jp_folder + outpath + "_jp.txt", "w", encoding='utf-8')
    all_eng = open(out_en_folder + outpath + "_en.txt", "w", encoding='utf-8')
    #eng_matched_subs = pysubs2.load("blank.ass")
    linecount = 0
    for i in range(len(jap_subs)):
        if (not i in match_dict):
            all_ja.write(jap_subs[i].text + "\n")
            all_eng.write("\n")
            continue
        else:
            eng_sub = eng_subs[match_dict[i][0]]
            if (len(match_dict[i]) > 1):
                for j in match_dict[i][1:]:
                    new_sub = eng_subs[j]
                    if (new_sub.end > eng_sub.end):
                        eng_sub.end = new_sub.end
                    eng_sub.text = eng_sub.text + " " + new_sub.text

            #eng_matched_subs.insert(linecount, jap_subs[i])
            #eng_matched_subs.insert(linecount+1, eng_sub)
            linecount += 2
            all_ja.write(jap_subs[i].text + "\n")
            out_en = eng_sub.text.replace("\n", " ")
            all_eng.write(out_en + "\n")
    all_ja.close()
    all_eng.close()
        
    #eng_matched_subs.save(out_folder + outpath+"_jap_eng.ass")
    return linecount/2
    

#ja_allfilenames = open("ja_filenames.txt", "r").readlines()
total_lines = 0
for i in tqdm(range(1, 12)):
    jap_filename = "Nigehaji_ja_ep{}.ass".format(i)
    eng_filename = "Nigeru wa Haji da ga Yaku ni Tatsu ep{:0>2d} (848x480 x264).ass".format(i)
    print("jp filename: %s, eng_filename: %s" %(jap_filename, eng_filename))
    out_filename = "Nigehaji_aligned_{:0>3d}".format(i)
    total_lines += process_file(jap_filename, eng_filename, out_filename)

print(total_lines)




