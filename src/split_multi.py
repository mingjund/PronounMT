import sys

with open(sys.argv[1], 'r') as f:
    text = f.readlines()

task = []
trans = []
for i, sent in enumerate(text):
    if i%2 == 0:
        task.append(sent)
    else:
        trans.append(sent)
        
with open(sys.argv[2], 'w') as f:
    f.writelines(task+trans)