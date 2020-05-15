import sys

with open(sys.argv[1], 'r') as in_f:
    in_text = in_f.read().splitlines()

prev_n = int(sys.argv[3])
next_n = int(sys.argv[4])
text_len = len(in_text)

with open(sys.argv[2], 'w') as out_f:
    for idx, line in enumerate(in_text):
        prev_lines = ' | '.join(in_text[max(idx-prev_n, 0): idx])
        next_lines = ' | '.join(in_text[idx+1: idx+next_n+1])

        out_f.write(prev_lines+' || '+line+' || '+next_lines+'\n')
