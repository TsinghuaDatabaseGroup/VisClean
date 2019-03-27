import pandas as pd
from collections import Counter
import numpy as np
import time

class MajorityVoting(object):
    def __init__(self, output_path, cluster_table_name, output_table_name, y_axis_name, cluster_id_tag):
        '''
        :param output_path:
        :param cluster_table:
        :param y_axis_name:
        :param cluster_id_tag:
        :return:
        '''
        self.output_path = output_path
        self.cluster_table_name = cluster_table_name
        self.output_table_name = output_table_name
        self.y_axis_name = y_axis_name
        self.cluster_id_tag = cluster_id_tag

    def majority_voting(self):

        df = pd.read_csv(self.output_path + self.cluster_table_name)

        start_time = time.time()
        # df.drop(['id'], axis=1)
        grouped_df = df.groupby(self.cluster_id_tag)
        attrs = list(df.columns.values)
        new_table = []
        for eachgroup in grouped_df:
            record = []
            for each_attr in attrs:
                if each_attr == self.y_axis_name:
                    # 将一个cluster中Citations的均值作为golden records
                    record.append(np.mean(list(map(int, eachgroup[1][self.y_axis_name].fillna(0).tolist()))))
                    # 将一个cluster中Citations中的最大值作为golden records
                    # record.append(max(list(map(int, eachgroup[1]['Citations'].fillna(0).tolist()))))
                else:
                    # 将出现最多的作为golden records
                    majority = Counter(eachgroup[1][each_attr].tolist()).most_common(1)[0][0]
                    record.append(majority)
            new_table.append(record)

        print("Time for majority vote from the cluster: ", time.time() - start_time)
        # Output the golden csv
        pd.DataFrame(new_table, columns=attrs).to_csv(self.output_path + self.output_table_name,index=False)