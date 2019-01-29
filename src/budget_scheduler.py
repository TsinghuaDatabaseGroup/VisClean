from src.util.queue import *
from src.util.operation import *
from queue import Queue
import math
import random

class BudgetScheduler(object):

    def __init__(self, cluster_precision, cluster_recall, gr_accuracy, operations):
        self.cluster_recall = cluster_recall
        self.cluster_precision = cluster_precision
        self.gr_accuracy = gr_accuracy
        self.threshold = 0.5
        self.cluster_recall_inc = 1.0
        self.cluster_precision_inc = 1.0
        self.gr_accuracy_inc = 1.0
        self.operation_queue = Queue(operations)

    def get_budgets(self, total_budgets, need_gr_columns):
        part = total_budgets / 12
        n_em = part * 5
        n_dc = part * 1
        n_gr = part * 6
        columns_num = len(need_gr_columns)
        column_budgets = {}
        for n in need_gr_columns:
            column_budgets[n] = n_gr / columns_num
            n_gr = n_gr - column_budgets[n]
            columns_num -= 1
        return n_em, n_dc, column_budgets

    def change_feature(self, cluster_precision, cluster_recall, gr_accuracy):
        self.cluster_recall_inc = cluster_precision - self.cluster_precision
        self.cluster_precision_inc = cluster_recall - self.cluster_recall
        self.gr_accuracy_inc = gr_accuracy - self.gr_accuracy
        if self.cluster_recall_inc < 0.0:
            self.cluster_recall_inc = 0.0
        if self.cluster_precision_inc < 0.0:
            self.cluster_precision_inc = 0.0
        if self.gr_accuracy_inc < 0.0:
            self.gr_accuracy_inc = 0.0
        self.cluster_recall = cluster_recall
        self.cluster_precision = cluster_precision
        self.gr_accuracy = gr_accuracy

    def get_budgets_2(self):
        current = self.operation_queue.get_head()
        for i in range(2):
            if current.name == 'em':
                if i == 0:
                    if self.cluster_recall_inc <= self.threshold:
                        current = self.operation_queue.dequeue()
                        self.operation_queue.enqueue(current)
                        self.threshold = (self.cluster_recall_inc + self.cluster_precision_inc + self.gr_accuracy_inc) / (3 * 2)
                return current.number, 0, {}
            elif current.name == 'dc':
                if i == 0 and self.cluster_precision_inc <= self.threshold:
                    current = self.operation_queue.dequeue()
                    self.operation_queue.enqueue(current)
                return 0, current.number, {}
            else:
                if i == 0 and self.gr_accuracy_inc <= self.threshold:
                    current = self.operation_queue.dequeue()
                    self.operation_queue.enqueue(current)
                return 0, 0, {current.column: current.number}

    def get_budgets_manually(self):#手动选
        print(self.cluster_precision, self.cluster_recall, self.gr_accuracy)
        while True:
            op = self.operation_queue.get_head()
            print(op.name, op.column)
            choice = eval(input('1. Pick this!\n0. Show me next one!\n'))
            if choice == 1:
                number = eval(input('Enter question number\n'))
                if op.name == 'em':
                    return number, 0, {}, 0
                elif op.name == 'dc':
                    return 0, number, {}, 0
                elif op.name == 'rf':
                    return 0, 0, {}, 1
                else:
                    return 0, 0, {op.column: number}, 0
            elif choice == 0:
                op = self.operation_queue.dequeue()
                self.operation_queue.enqueue(op)
            else:
                pass



