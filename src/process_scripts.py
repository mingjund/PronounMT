#%%
import re
import pykakasi
import mojimoji
import jaconv
import pysrt
import pysubs2
from tqdm import tqdm
from collections import Counter


kakasi = pykakasi.kakasi()
kakasi.setMode('J', 'H')
kakasi.setMode('K', 'H')
conv = kakasi.getConverter()


class Drama:
    def __init__(self, name, ep_delimiter, scene_delimiter, sub_style, drama_len, window, bi_thres, uni_thres):
        self.name = name
        self.ep_delimiter = ep_delimiter
        self.scene_delimiter = scene_delimiter
        self.sub_style = sub_style
        self.drama_len = drama_len
        self.window = window
        self.bi_thres = bi_thres
        self.uni_thres = uni_thres


def load_script(drama):
    path = '../subs/{name}/{name}-script.txt'.format(name=drama.name)
    with open(path, 'r') as f:
        script_by_ep = re.split('(?=\n\n\n\n\n{}\n\n\n\n\n\n)'.format(drama.ep_delimiter), f.read())[1:]

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


def load_sub(path):
    with open(path, 'r') as f:
        subs = f.readlines()

    dialogue = []
    for line in subs:
        sub = line.split(',')
        if sub[0] == 'Dialogue: 0' and sub[3] == 'Aki JP':
            dialogue.append((sub[1], sub[2], sub[-1][:-1]))

    return dialogue


def load_subs(path):
    with open(path, 'r') as f:
        subs = f.read().split('\n')
    return subs


def load_ass(path, drama):
    subs_raw = pysubs2.load(path)
    subs_clean = []

    p = re.compile('\(.*?\)')
    for sub in subs_raw:
        if (sub.type == "Dialogue" and sub.style in set(drama.sub_style)):
            sub.text = p.sub('', sub.text)
            subs_clean.append(sub)

    return subs_clean


def split_script(path, script_name):
    full_script = load_script(path)
    for i in range(len(full_script)):
        ep_script_path = '{}_script_ep{:03d}.txt'.format(script_name, i+1)
        ep_speakers_path = '{}_speakers_ep{:03d}.txt'.format(script_name, i+1)
        with open(ep_script_path, 'w') as script_f, open(ep_speakers_path, 'w') as speakers_f:
            print('writing to', ep_script_path)
            for scene in full_script[i]:
                scene_name = scene[0]
                scene_text = list(zip(*scene[1]))
                speakers = scene_text[0]
                utterances = scene_text[1]
                #scene_script = '\n\n['+scene[0]+']\n\n'+'\n'.join(utterances)
                #scene_speakers = '\n\n['+scene[0]+']\n\n'+'\n'.join(speakers)
                scene_script = '\n'.join(utterances)
                scene_speakers = '\n'.join(speakers)
                script_f.write(scene_script)
                speakers_f.write(scene_speakers)
            #ep_script = ''.join(['\n\n['+scene[0]+']\n\n'+'\n'.join(list(zip(*scene[1][1]))[1]) for scene in full_script[i]])


def normalize_ja(text):
    text = jaconv.h2z(text,ascii=True, digit=True)
    text = conv.do(text)
    text = jaconv.normalize(text)
    text = re.sub(r'[.…｡。!！、\u3000　 ]|\\N|[\（\(].*?[\）\)]', '', text)
    return text


def get_bigrams(text):
    text = normalize_ja(text)
    bigrams = []
    if len(text) > 0:
        bigrams.append(' '+text[0])
        for i in range(len(text)):
            bigrams.append(text[i:i+2])
        bigrams[-1] = bigrams[-1]+' '
    return dict(Counter(bigrams)), len(bigrams)


def get_unigrams(text):
    unigrams = normalize_ja(text)
    return dict(Counter(unigrams)), len(unigrams)


def search_window(sub, episode, prev_turn_no, unmatched, search_range, bi_thres, uni_thres):
    best_count = 0
    best_turn = ('', '')
    turn_no = None
    sub_bigrams, sub_bigrams_len = get_bigrams(sub)
    sub_unigrams, sub_unigrams_len = get_unigrams(sub)

    if sub_unigrams_len == 0:
        unmatched += 1
    else:
        for i in range(*search_range):
            scene = episode[i]
            for j in range(len(scene[1])):
                turn = scene[1][j]
                script_bigrams, script_bigrams_len = get_bigrams(turn[1])
                bi_count = 0
                for bigram in sub_bigrams:
                    bi_count += min(sub_bigrams[bigram], script_bigrams.get(bigram, 0))
                if bi_count > best_count:
                    best_count = bi_count
                    best_turn = turn
                    turn_no = (i,j)
        if best_count/sub_bigrams_len < bi_thres:
            #print('bi', best_count/sub_bigrams_len, sub + ' | '+ best_turn[1])
            unmatched += 1
            best_turn = ('', '')
            turn_no = None
        else:
            uni_count = 0
            script_unigrams, _ = get_unigrams(best_turn[1])
            for unigram in sub_unigrams:
                uni_count += min(sub_unigrams[unigram], script_unigrams.get(unigram, 0))
            if uni_count/sub_unigrams_len < uni_thres:
                #print('uni', uni_count/sub_unigrams_len, sub + ' | '+ best_turn[1])
                unmatched += 1
                best_turn = ('', '')
                turn_no = None
            else:
                prev_turn_no = turn_no
                #print('bi', best_count/sub_bigrams_len, sub + ' | '+ best_turn[1])
                #print('uni', uni_count/sub_unigrams_len, sub + ' | '+ best_turn[1])

    return turn_no, best_turn, prev_turn_no, unmatched


def align_utterances(ja_subs, en_subs, episode, window, bi_thres, uni_thres):
    matched_script = []
    unmatched = 0
    prev_turn_no = (0, 0)
    script_len = len(episode)
    for ja_sub, en_sub in zip(ja_subs, en_subs):
        if len(ja_sub) > 0: 
            search_range = (max(prev_turn_no[0]+window[0], 0), 
                            min(prev_turn_no[0]+window[1]+1, script_len))
            turn_no, best_turn, prev_turn_no, unmatched = \
                search_window(ja_sub, episode, prev_turn_no, unmatched, search_range, bi_thres, uni_thres)
            matched_script.append((turn_no, best_turn[0], best_turn[1], ja_sub, en_sub))
        else:
            matched_script.append((None, '', '', ja_sub, en_sub))
    print('unmatched', unmatched/len(ja_subs))
    # for i in matched_script:
    #     print(i)
    return matched_script


def alignbybleu(subs, episode, window, bleu_thres):
    matched_script = []
    unmatched = 0
    prev_turn_no = (0, 0)
    for sub in subs:
        best_bleu = 0
        best_turn = ''
        sub_text = list(normalize_ja(sub[2]))
        for i in range(max(prev_turn_no[0]+window[0], 0), min(prev_turn_no[0]+window[1]+1, len(episode))):
            scene = episode[i]
            for j in range(len(scene[1])):
                turn = scene[1][j]
                script_text = list(normalize_ja(turn[1]))
                bleu = noBP_bleu(script_text, sub_text, (0.01,0.99))
                if bleu > best_bleu:
                    best_bleu = bleu
                    best_turn = turn[1]
                    turn_no = (i,j)       
        if best_bleu < bleu_thres:
            print('bi', best_bleu, sub[2] + ' | '+ best_turn)
            unmatched += 1
            best_turn = ''
            turn_no = None
        else:
            prev_turn_no = turn_no
        matched_script.append((turn_no, sub[2], best_turn))

    print('unmatched', unmatched/len(subs))
    return matched_script


def realign(matched_script, episode, bi_thres, uni_thres):
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
            while matched_script[i-k][0] == None and i >= k:
                k += 1     
            if matched_script[i-k][0] != None:   
                prev_scene_no = matched_script[i-k][0][0]

        if i < last_sub:
            l = 1
            while i+l < last_sub and (matched_script[i+l][0] == None or matched_script[i+l][0][0] < prev_scene_no):
                l += 1
            if matched_script[i+l][0] != None:
                next_scene_no = matched_script[i+l][0][0]
        #print(prev_scene_no, scene_no, next_scene_no)
        if scene_no == None or scene_no < prev_scene_no or scene_no > next_scene_no: 
            ja_sub = matched_script[i][3]
            search_range = prev_scene_no, next_scene_no+1
            turn_no, best_turn, prev_turn_no, _ = \
                search_window(ja_sub, episode, prev_turn_no, 0, search_range, bi_thres, uni_thres)
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


def process_spt(spt_path):
    scenes = []
    with open(spt_path, 'r') as f:
        spt = f.read().splitlines()
        scene = []
        prev_speaker = ''
        for line in spt:
            if line[:4] == 'S#1.':
                scene = []
            elif line[:2] == 'S#':
                scenes.append(scene)
                scene = []
                prev_speaker = ''
            else:
                speaker, utterance = extract_speaker(line)
#                 if line == '':
#                     prev_speaker = ''
#                 elif speaker == '':
                if speaker == '':
                    if prev_speaker != '':
                        last_line = scene.pop(-1)
                        new_line = (last_line[0] +' '+line, last_line[1])
                        scene.append(new_line)
#                         scene.append((line, prev_speaker))
#                         prev_speaker = ''
                else:
                    scene.append((utterance, speaker))
                    prev_speaker = speaker
        scenes.append(scene)
    return scenes


def process(line):
    words = line.split()
    words = [word.strip('.,?!~_-') for word in words]
    return ' '.join(words)


def process_srt(srt_path):
    srt = pysrt.open('Descendants1.srt')
    srt = [process(line.text) for line in srt]
    srt = [s for s in srt if '<i>' not in s and s != '']
    return srt


def extract_speaker(line):
#     2 spaces
    words = line.split('  ')
    illegal_symbols = ':(<-'
    if len(words) < 2 or any(i in words[0] for i in illegal_symbols):
        return ('', '')
    utterance = ''.join([word for word in words[1:] if word != '']).lstrip()
    return (words[0], utterance)

#%%   
if __name__ == '__main__':

    Amachan = Drama('Amachan', '第.*回', '■', ['Aki JP'], 156, (-3,3), 0.12, 0.26)
    Yutori = Drama('Yutori', '１　.*' , '\n\n\n\n\n[０-９0-9]*　.*\n\n\n\n\n\n', ['Subtitle', 'Default'], 10, (-10,10), 0.3, 0.4)
    Nigehaji = Drama('Nigehaji', '１　.*' , '\n\n\n\n\n[０-９0-9]*　.*\n\n\n\n\n\n', ['Default'], 11, (-10,10), 0.3, 0.4)
    drama = Yutori
    

    for drama in [Amachan, Yutori, Nigehaji]:
        print('Aligning', drama.name)
        script = load_script(drama)
        unmatched_subs = 0 
        sub_count = 0
        
        for ep in tqdm(range(drama.drama_len)):
            ja_sub_path = '../subs/{name}/en-ja_alignment/ja_subs/{name}_aligned_{ep:0>3d}.ja'.format(name=drama.name, ep=ep+1)
            en_sub_path = '../subs/{name}/en-ja_alignment/en_subs/{name}_aligned_{ep:0>3d}.en'.format(name=drama.name, ep=ep+1)
            ja_subs = load_subs(ja_sub_path)
            en_subs = load_subs(en_sub_path)
            assert(len(ja_subs) == len(en_subs))
            sub_count += len(ja_subs)
            episode = script[ep]
            matched_script = align_utterances(ja_subs, en_subs, episode, drama.window, drama.bi_thres, drama.uni_thres)
            unmatched_subs += realign(matched_script, episode, drama.bi_thres, drama.uni_thres)[1]

            with open('../subs/{}/script-sub_alignment/{:03d}_speaker-alignment.txt'.format(drama.name, ep+1), 'w') as f:
                f.write('\n'.join(' | '.join([str(line[0])]+list(line[1:])) for line in matched_script))

#%%
    print(sub_count)
    print('total unmatch rate:', unmatched_subs/sub_count)

