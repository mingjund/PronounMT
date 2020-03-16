import re

for ep in range(156):
    sub_path = '../subs/Amachan/en-ja_sub_alignment/en_txt/Amachan_aligned_{:0>3d}_en.txt'.format(ep+1)
    with open(sub_path, 'r') as f:
        text = f.read()
        text = re.sub(r'\{.*?\}', '', text)
        text = re.sub(r'\\N', ' ', text)

    with open(sub_path, 'w') as f:
        f.write(text)