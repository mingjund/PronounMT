for f in  $(ls -r $2/*.pt);
do 
  echo $f 
  bash /home/mingjund/PronounMT/code/scripts/translate.sh $1 ${f:0:-3} $3 $4 $5 $6
done
