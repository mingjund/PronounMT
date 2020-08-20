#%%
import os
import re
import pykakasi
import jaconv
import nltk
import argparse
from tqdm import tqdm
from collections import Counter


kakasi = pykakasi.kakasi()
kakasi.setMode('J', 'H')
kakasi.setMode('K', 'H')
conv = kakasi.getConverter()


def load_script(drama):
    with open(drama.script, 'r') as f:
        script_by_ep = re.split('(?={})'.format(drama.ep_delimiter), f.read())[1:]

    script_by_scene = [re.split('(?={})'.format(drama.scene_delimiter), ep) for ep in script_by_ep]
    script_by_turn = []

    for ep in script_by_scene:
        scenes = []
        for scene in ep:
            scene_title = re.findall(r'^(.*?)\n', scene)
            turns = [tuple(turn.split('「')) for turn in re.findall(r'(.*?「.*?)」', scene)]
            if turns != []:
                scenes.append((scene_title[0], turns))
        if scenes != []:
            script_by_turn.append(scenes)

    return script_by_turn


def load_subs(path):
    with open(path, 'r') as f:
        subs = f.read().split('\n')
    return subs


def normalize_ja(text):
    text = jaconv.h2z(text,ascii=True, digit=True)
    text = conv.do(text)
    text = jaconv.normalize(text)
    text = re.sub(r'[.…｡。!！、\u3000　 ]|\\N|[\（\(].*?[\）\)]', '', text)
    if len(text) < 3:
        text = ' '+text+' '
    return text


def get_ngrams(text, n):
    ngrams = list(nltk.ngrams(text, n))
    return dict(Counter(ngrams)), len(ngrams)


def search_window(sub, episode, prev_turn_no, jump, unmatched, search_range, tri_thres, bi_thres):
    best_count = 0
    best_turn = ('', '')
    turn_no = None
    sub_text = normalize_ja(sub)
    #sub_trigrams, sub_trigrams_len = get_ngrams(sub_text, 3)
    sub_trigrams, sub_trigrams_len = get_ngrams(sub_text, 3)
    sub_bigrams, sub_bigrams_len = get_ngrams(sub_text, 2)

    if sub_trigrams_len == 0:
        unmatched += 1
    else:
        for i in range(*search_range):
            scene = episode[i]
            for j in range(len(scene[1])):
                turn = scene[1][j]
                script_text = normalize_ja(turn[1])
                script_trigrams, script_trigrams_len = get_ngrams(script_text, 3)
                tri_count = 0
                for trigram in sub_trigrams:
                    tri_count += min(sub_trigrams[trigram], script_trigrams.get(trigram, 0))
                if tri_count > best_count:
                    best_count = tri_count
                    best_turn = turn
                    turn_no = (i,j)
        if best_count/sub_trigrams_len < tri_thres:
            # print('bi', best_count/sub_trigrams_len, sub + ' | '+ best_turn[1])
            # unmatched += 1
            # best_turn = ('', '')
            # turn_no = None
        #else:
            bi_count = 0
            script_bigrams, _ = get_ngrams(normalize_ja(best_turn[1]), 2)
            for bigram in sub_bigrams:
                bi_count += min(sub_bigrams[bigram], script_bigrams.get(bigram, 0))
            if bi_count/sub_bigrams_len < bi_thres:
                #print('uni', bi_count/sub_bigrams_len, sub + ' | '+ best_turn[1])
                unmatched += 1
                best_turn = ('', '')
                turn_no = None
            #else:
                #if turn_no[0] > prev_turn_no[0]:
        if turn_no != None:
            # if previously no jump, jump is allowed
            if jump == 0:
                jump = turn_no[0] - prev_turn_no[0]
            # previously jumped and now must return
            else:
                jump = 0

            prev_turn_no = turn_no
            # print('tri', best_count/sub_trigrams_len, sub + ' | '+ best_turn[1])
            # if best_count/sub_trigrams_len < tri_thres:
            #     print('bi', bi_count/sub_bigrams_len, sub + ' | '+ best_turn[1])

    return turn_no, best_turn, prev_turn_no, jump, unmatched


def align_utterances(src_subs, tgt_subs, episode, window, tri_thres, bi_thres):
    matched_script = []
    unmatched = 0
    prev_turn_no = (0, 0)
    script_len = len(episode)
    sub_len = 0
    jump = 0
    for ja_sub, en_sub in zip(src_subs, tgt_subs):
        if len(ja_sub) > 0: 
            #print(jump)
            search_range = (max(prev_turn_no[0]-window-jump, 0), 
                            min(prev_turn_no[0]+window+1-jump, script_len))
            #print(prev_turn_no[0], search_range)
            turn_no, best_turn, prev_turn_no, jump, unmatched = \
                search_window(ja_sub, episode, prev_turn_no, 0, unmatched, search_range, tri_thres, bi_thres)
            matched_script.append((turn_no, best_turn[0], best_turn[1], ja_sub, en_sub))
            #print((turn_no, best_turn[0], best_turn[1], ja_sub, en_sub))
            sub_len += 1
        # else:
        #     matched_script.append((None, '', '', ja_sub, en_sub))
    print('unmatched', unmatched/sub_len)
    # for i in matched_script:
    #     print(i)
    return matched_script, sub_len


def realign(matched_script, episode, tri_thres, bi_thres):
    unmatched = 0
    prev_turn_no = (0,0)
    last_sub = len(matched_script) - 1
    last_scene = len(episode) - 1

    for i in range(len(matched_script)):
        scene_no = None if matched_script[i][0] == None else matched_script[i][0][0]
        prev_scene_no = 0
        next_scene_no = last_scene

        if i > 0:
            k = 1
            while matched_script[i-k][0] == None and i > k:
                k += 1     
            if matched_script[i-k][0] != None:   
                prev_scene_no = matched_script[i-k][0][0]

        if i < last_sub:
            l = 1
            while i+l < last_sub and (matched_script[i+l][0] == None or \
                matched_script[i+l][0][0] < prev_scene_no):
                l += 1
            if matched_script[i+l][0] != None:
                next_scene_no = matched_script[i+l][0][0]
        #print(prev_scene_no, scene_no, next_scene_no)
        if scene_no == None or scene_no < prev_scene_no or scene_no > next_scene_no: 
            ja_sub = matched_script[i][3]
            search_range = prev_scene_no, next_scene_no+1
            turn_no, best_turn, prev_turn_no, _, _ = \
                search_window(ja_sub, episode, prev_turn_no, 0, 0, search_range, tri_thres, bi_thres)
            #print('prev', matched_script[i])
            if turn_no != None:
                matched_script[i] = (turn_no, best_turn[0], best_turn[1], ja_sub, matched_script[i][4])
            # else:
            #     matched_script[i] = (None, '', '', ja_sub, matched_script[i][4])
            #print('curr', matched_script[i])

        #print(matched_script[i])
        unmatched += 1 if matched_script[i][0] == None else 0
        
    print('realigned unmatched:', unmatched/(last_sub+1))
    return matched_script, unmatched


#%%   
if __name__ == '__main__':
    parser = argparse.ArgumentParser()   
    parser.add_argument('--script', type=str, default=None)
    parser.add_argument('--subs', type=str, default=None)
    parser.add_argument('--foreign_subs', type=str, default=None)
    parser.add_argument('--output', type=str, default=None) 
    parser.add_argument('--drama_len', type=int, default=None)
    parser.add_argument('--ep_delimiter', type=str, default='\n\n\n\n\n第.*回\n\n\n\n\n\n')
    parser.add_argument('--scene_delimiter', type=str, default='■')
    parser.add_argument('--window', type=int, default=10)
    parser.add_argument('--tri_thres', type=float, default=0.4)
    parser.add_argument('--bi_thres', type=float, default=0.5)
    args = parser.parse_args()  

    total_unmatched = 0
    total_subs = 0

    print('Aligning', args.script, args.subs)
    script = load_script(args)
    unmatched_subs = 0 

    if not os.path.isdir(args.output):
        os.mkdir(args.output)
    
    for ep in tqdm(range(args.drama_len)):
        src_sub_path = '{}/aligned_ep{}.txt'.format(args.subs, ep+1)
        src_subs = load_subs(src_sub_path)

        if args.foreign_subs != None:
            tgt_sub_path = '{}/aligned_ep{}.txt'.format(args.foreign_subs, ep+1)
            tgt_subs = load_subs(tgt_sub_path)
            assert(len(src_subs) == len(tgt_subs)), "subs and foreign_subs ep{} have different lengths".format(ep+1)
        else:
            tgt_subs = ["" for sub in src_subs]
        episode = script[ep]
        matched_script, sub_len = align_utterances(src_subs, tgt_subs, episode, args.window, args.tri_thres, args.bi_thres)
        matched_script, unmatched_subs = realign(matched_script, episode, args.tri_thres, args.bi_thres)
        total_subs += sub_len
        total_unmatched += unmatched_subs

        with open('{}/speaker-sub_alignment_ep{}.txt'.format(args.output, ep+1), 'w') as f:
            f.write('\n'.join(' | '.join([str(line[0])]+list(line[1:])) for line in matched_script))

#%%     
        print("sub count:", sub_len)
        print("matched subs:", sub_len - unmatched_subs)

    print(args.script, args.subs)
    print("total sub count:", total_subs)
    print("total matched subs:", total_subs - total_unmatched)
    print('total unmatch rate:', total_unmatched/total_subs)