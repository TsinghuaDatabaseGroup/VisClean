import pandas as pd

class Precision(object):

    def __init__(self):
        # TODO do init here
        pass

    def get_precision(self, predict):
        total = 0.0
        truth = 0.0
        for index, row in predict.iterrows():
            if row['predicted'] == 1:
                # due to ground truth id
                if row['ltable_cluster_id'] == row['rtable_cluster_id']:
                    truth += 1.0
                total += 1.0
        precision = truth / total
        print("total = ", total, "\ntruth = ", truth, "\nprecision = ", truth/total)
        return precision

    def get_recall(self, predict):
        TP = 0.0
        FP = 0.0
        for index, row in predict.iterrows():
            # due to ground truth id
            if row['ltable_cluster_id'] == row['rtable_cluster_id']:
                if row['predicted'] == 1:
                    TP += 1.0
                else:
                    FP += 1.0
        recall = TP / (TP + FP)
        print("TP = ", TP, "\nFP = ", FP, "\nrecall = ", recall)
        return recall

    def get_F_measure(self, predict):
        P = Precision.get_precision(self, predict)
        R = Precision.get_recall(self, predict)
        F = 2 * P * R / (P + R)
        print('Precision = ', P, '\nRecall = ', R, '\nF-measure = ', F)

