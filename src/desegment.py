import sys

with open(sys.argv[1],'r') as f:
    text = f.readlines()

with open(sys.argv[2], 'w') as f:
    f.write('\n'.join(("".join(sent.split())).replace("▁",  " ").strip().split('| ')[-1] for sent in text))
