docs = ['train', 'test', 'dev']

for doc in docs:
    line_no_f = open(doc+'.docs',  'r')
    line_no = [int(l.strip()) for l in line_no_f.readlines()]
    with open(doc+'.spk',  'r') as f:
        out_f = open(doc+'_normalized.spk', 'w')
        lines = f.readlines()
        speakers = []
        for i in range(len(lines)):
            if i in line_no:
                speakers = []

            l = lines[i].strip()
            if l == 'UNK_SPK':
                out_f.write('[UNK_SPK]\n')
                continue

            spks = l.split()
            flag = False
            out_spks = []
            for sub_spk in spks:
                for speaker in speakers:
                    if sub_spk in speaker and speaker in l:
                        out_spks.append(str(speakers.index(speaker)))
                        flag = True
                        spks = [spk.strip() for spk in l.split(speaker)]
                        break
                if flag == True:
                    break
            if flag:
                for spk in spks:
                    if spk not in speakers and spk != '':
                        speakers.append(spk)
                    if spk != '':
                        out_spks.append(str(speakers.index(spk)))
            else:
                if l not in speakers: 
                    speakers.append(l)
                out_spks.append(str(speakers.index(l)))
            for spk in out_spks:
                out_l = 'UNK_SPK'
                if spk != 'UNK_SPK':
                    out_l = 'SPK'+spk
                out_f.write('[' + out_l+']')
            out_f.write('\n')
        out_f.close()