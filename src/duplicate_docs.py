import sys

with open(sys.argv[1], 'r') as f:
    docs = f.readlines()
    new_docs = []

    for i in docs:
        new_docs.append('\n'+str(int(i)+152473))

with open(sys.argv[2], 'w') as f:
    f.writelines(docs+new_docs)