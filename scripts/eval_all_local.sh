for f in $(ls -r $1);
do
  echo $2 $f
  cat $f | sacrebleu -w 2 $2
  python3 /Users/mingjunduan/Documents/CMU/S20/PronounMT/code/src/pronoun_stats.py $2 $f
done
