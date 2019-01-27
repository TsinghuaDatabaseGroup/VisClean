import pandas as pd
from collections import Counter


class MajVote(object):
    def __init__(self, clusters):
        super(MajVote, self).__init__()
        self.clusters = clusters

    def get_golden(self):
        df = self.clusters
        grouped_df = df.groupby('cluster_id')
        group_num = len(grouped_df)
        attrs = list(df.columns.values)
        new_df = pd.DataFrame(columns=attrs)
        i = 0
        for eachgroup in grouped_df:
            record = []
            for each_attr in attrs:
                majority = Counter(eachgroup[1][each_attr].tolist()).most_common(1)[0][0]
                record.append(majority)
            new_df.loc[i] = record
            i += 1
        return new_df