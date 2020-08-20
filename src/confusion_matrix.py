import sys
from sklearn.metrics import confusion_matrix

with open(sys.argv[1], 'r') as y_f, open(sys.argv[2], 'r') as fx_f:
    y_true = y_f.read().split()
    y_pred = fx_f.read().split()

    assert(len(y_true) == len(y_pred))

    labels = sorted(set(y_true+y_pred))
    matrix = confusion_matrix(y_true, y_pred, labels=labels)

    for true in range(len(matrix)):
        for pred in range(len(matrix[0])):
            if matrix[true][pred] != 0:
                print(labels[true], labels[pred], matrix[true][pred])
            
