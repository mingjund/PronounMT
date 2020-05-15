import spacy
import sys
import numpy as np
from sklearn.metrics import classification_report

en_pro = {'i', 'my', 'me', 'mine', 'myself',
                'we', 'us', 'our', 'ours', 'ourselves',
                'you', 'your', 'yours', 'yourself', 'yourselves',
                'he', 'him', 'his', 'himself',
                'she', 'her', 'hers', 'herself',
                'they', 'them', 'their', 'theirs', 'themself', 'themselves',
                'it', 'its', 'itself'}

ja_pro = {'私', 'わたし', 'ワタシ', '私達', '僕', 'ぼく',
                'ボク', '僕ら', '俺', 'おれ', 'オレ', '俺ら',
                'あなた', 'あなた達', '貴方', 'あんた','貴様', '手前',
                'お前', 'おまえ','お前ら','君','きみ','キミ','君たち', '君たち',
                '彼', 'かれ', 'カレ', '彼ら',
                '彼女', 'かのじょ', 'カノジョ', '彼女たち', '彼女達'}

zh_pro = {'我', '我们', '咱', '咱们',
          '你', '你们',
          '他', '他们', '她', '她们', '它', '它们'}

nlp = spacy.load("en_core_web_sm")

#pronoun frequency by language
def frequency(file, size):
    with open(file, 'r') as f:
        pro_list = ja_pro if file.split('.')[-1] == 'ja' else en_pro
        tokens = f.read().split()
        total = 0
        stats = [file]
        for pro in pro_list:
            count = tokens.count(pro)
            total += count
            stats.append(pro+' '+str(count))
        # for token in tokens:
        #     if token in pro_list:
        #         count += 1
        stats.append('average no. of pronouns per sentence:'+str(total/size))

    with open(file+'.freq', 'w') as freq:
        freq.write('\n'.join(stats))


def freq_ratio(fileA, fileB, size):
    with open(fileA, 'r') as fA, open(fileB, 'r') as fB:
        pro_list = ja_pro if fileA.split('.')[-1] == 'ja' else en_pro
        tokensA = fA.read().split()
        tokensB = fB.read().split()
        totalA = 0
        totalB = 0
        stats = [fileA+' & '+ fileB]
        for pro in pro_list:
            countA = tokensA.count(pro)
            countB = tokensB.count(pro)
            totalA += countA
            totalB += countB
            ratio = countB/countA if countA != 0 else 0
            stats.append(pro+' | '+str(countA)+' | '+str(countB)+' | '+str(ratio))
        # for token in tokens:
        #     if token in pro_list:
        #         count += 1
        stats.append('average no. of pronouns per sentence:'+' | '+str(totalA/size)+' | '+str(totalB/size)+' | '+str(totalB/totalA))
        stats.append('pronoun probability: '+str(totalA/len(tokensA))+' | '+str(totalB/len(tokensB))+' | '+str((totalB/len(tokensB))/(totalA/len(tokensA))))
        stats.append('average sentence length: '+str(len(tokensA)/size)+' | '+str(len(tokensB)/size)+' | '+str(len(tokensB)/len(tokensA)))

    with open(fileB+'.freq', 'w') as freq:
        freq.write('\n'.join(stats))


def pronoun_pt(pt_file, pro_pt_file):
    with open(pt_file, 'r') as pt:
        #list all phrases with english pronouns
        phrases = pt.readlines()
        en_pronouns = []
        ja_pronouns = []
        for pronoun in en_pro:
            en_pronouns.append(pronoun+'\n')
            for phrase in phrases:
                en_phrase = set(phrase.split('|||')[1].split())
                if pronoun in en_phrase:
                    en_pronouns.append(phrase)

        #list all phrases with japanese pronouns
        for pronoun in ja_pro:
            ja_pronouns.append(pronoun+'\n')
            for phrase in phrases:
                ja_phrase = set(phrase.split('|||')[0].split())
                if pronoun in ja_phrase:
                    ja_pronouns.append(phrase)

    with open(pro_pt_file + '.en_pro.pt', 'w') as en_pt:
        en_pt.write(''.join(en_pronouns))

    with open(pro_pt_file + '.ja_pro.pt', 'w') as ja_pt:
        ja_pt.write(''.join(ja_pronouns))


def pron_eval(ref_file, out_file):
    if '.pron.' in out_file:  
        print(cls_report(ref_file, out_file))
    else:
        with open(ref_file, 'r') as ref, open(out_file, 'r') as out:
            ref_text = ref.readlines()
            out_text = out.readlines()
            out_text = out_text[:len(ref_text)]

            precision_scores = []
            recall_scores = []
            f1_scores = []

            # for ref_line, out_line in zip(nlp.pipe(ref_text), nlp.pipe(out_text)):
            #     ref_pronouns = []
            #     out_pronouns = []
            #     for token in ref_line:
            #         if token.pos_ == "PRON" :
            #             ref_pronouns.append(token.text)


            #     for token in out_line:
            #         if token.pos_ == "PRON" :
            #             out_pronouns.append(token.text)

            if 'en' in ref_file:     
                for ref_line, out_line in zip(nlp.pipe(ref_text), nlp.pipe(out_text)):
                    ref_pronouns = []
                    out_pronouns = []
                    for token in ref_line:
                        word = token.text.lower()
                        if word in en_pro:
                            ref_pronouns.append(word)

                    #if len(ref_pronouns) == 0:
                    #    continue

                    for token in out_line:
                        word = token.text.lower()
                        if word in en_pro:
                            out_pronouns.append(word)

                    #print('ref:', ref_pronouns, 'out:', out_pronouns)
                    #precision
                    out_hit = 0
                    for pron in out_pronouns:
                        if pron in ref_pronouns:
                            ref_pronouns.remove(pron)
                            out_hit += 1

                    precision = out_hit/len(out_pronouns) if len(out_pronouns) != 0 else 1
                    precision_scores.append(precision)

                    #recall
                    ref_hit = 0
                    for pron in ref_pronouns:
                        if pron in out_pronouns:
                            out_pronouns.remove(pron)
                            ref_hit += 1

                    recall = ref_hit/len(ref_pronouns) if len(ref_pronouns) != 0 else 1
                    recall_scores.append(recall)

                    f1 = 2*precision*recall/(precision+recall) if precision+recall != 0 else 0
                    f1_scores.append(f1)
                    #print('precision:', precision, 'recall:', recall, 'f1:', f1)

            elif 'zh' in ref_file:  
                for ref_line, out_line in zip(ref_text, out_text):
                    ref_pronouns = []
                    out_pronouns = []
                    for token in ref_line.split():
                        if token in zh_pro:
                            ref_pronouns.append(token)

                    #if len(ref_pronouns) == 0:
                    #    continue

                    for token in out_line.split():
                        if token in zh_pro:
                            out_pronouns.append(token)

                    #print('ref:', ref_pronouns, 'out:', out_pronouns)
                    #precision
                    out_hit = 0
                    for pron in out_pronouns:
                        if pron in ref_pronouns:
                            ref_pronouns.remove(pron)
                            out_hit += 1

                    precision = out_hit/len(out_pronouns) if len(out_pronouns) != 0 else 1
                    precision_scores.append(precision)

                    #recall
                    ref_hit = 0
                    for pron in ref_pronouns:
                        if pron in out_pronouns:
                            out_pronouns.remove(pron)
                            ref_hit += 1

                    recall = ref_hit/len(ref_pronouns) if len(ref_pronouns) != 0 else 1
                    recall_scores.append(recall)

                    f1 = 2*precision*recall/(precision+recall) if precision+recall != 0 else 0
                    f1_scores.append(f1)
                    #print('precision:', precision, 'recall:', recall, 'f1:', f1)

            average_precision = sum(precision_scores)/len(precision_scores)
            average_recall = sum(recall_scores)/len(recall_scores)
            total_f1 = 2*average_precision*average_recall/(average_precision+average_recall)
            average_f1 = sum(f1_scores)/len(f1_scores)
            print('AVERAGE precision:', average_precision, 'recall:', average_recall, 'f1:', total_f1, 'average f1:', average_f1)


def cls_report(file_true, file_pred):
        y_true = np.loadtxt(file_true, dtype=str)
        y_pred = np.loadtxt(file_pred, dtype=str)
        return classification_report(y_true, y_pred)


if __name__ == "__main__":
    #frequency('train.tok.ja', 2797387)
    #frequency('train.tok.en', 2797387)
    #frequency('test.tok.ja', 2000)
    #frequency('test.tok.en', 2000)

    #pronoun_pt('test.align.1.pt', 'test')

    #frequency('test_165000.out.tok.en', 2000)

    #pronoun_pt('test_165000.out.tok.en.align.1.pt', 'test_165000.out.tok.en')
    #freq_ratio('../split/test.pron.tok.en', 'pron_only/test_65000.out.en', 643)
    #pron_eval('../split/test.pron.en', 'test_65000.full_sent.pron.out.tok.en', "full_sent.pron_eval.stats")

    #print('baseline:\n', cls_report('../split/test.pronword.en', 'test_165000.pronword.out.en'))
    #print('full_sent:\n', cls_report('../split/test.pronword.en', 'full_sent/test_65000.full_sent.pronword.out.en'))
    #print('pron_only:\n', cls_report('../split/test.pronword.en', 'pron_only/test_65000.out.en'))
    #print(sys.argv[2])
    pron_eval(sys.argv[1], sys.argv[2])
    #print(cls_report(sys.argv[1], sys.argv[2]))
#'../../dialog_corpus/en-ja/data/test.turn'
#'../../dialog_corpus/en-ja_turns/vocab_8000_HAN_base/dialog_acc_87.80_ppl_1.40_e3.out.turn'