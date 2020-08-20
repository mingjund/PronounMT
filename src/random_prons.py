import sys
import re
import random

en_pro = ['i', 'my', 'me', 'mine', 'myself',
                'we', 'us', 'our', 'ours', 'ourselves',
                'you', 'your', 'yours', 'yourself', 'yourselves',
                'he', 'him', 'his', 'himself',
                'she', 'her', 'hers', 'herself',
                'they', 'them', 'their', 'theirs', 'themself', 'themselves',
                'it', 'its', 'itself']

with open(sys.argv[1], 'r') as f:
    text = f.read()
    while '[MASK]' in text:
        text = re.sub('\[MASK\]', random.choice(en_pro), text, 1)

with open(sys.argv[1].replace('.pron_masked_en','.random_pron_en'), 'w') as f:
    f.write(text)