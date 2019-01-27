import pandas as pd
from collections import Counter
import csv

path = '/Users/yuyu/Project/VisClean/dataset/DBConf'
ltable_path = path + '/DBPublications-input_id.csv'
rtable_path = path + '/DBPublications-input_id.csv'
rf_predict_path = path + '/rf_predict.csv'
output_path = path
apply_table_path = ltable_path

def myPair2Cluster():
    mergeId = []  # [(1,2),(1,4), ...]
    quesId = []
    df = pd.read_csv(rf_predict_path)
    apply_table = pd.read_csv(apply_table_path)

    PredictClusterId = 1314520
    cluster = {}
    print(len(df))
    cnt = 0

    apply_table['predictClusterId'] = None
    # apply_table.to_csv(path+'/test.csv')
    print('Read', apply_table.loc[0, 'predictClusterId'])
    # print(apply_table.loc[34906,'predictClusterId'])
    print(apply_table.head())

    for index, row in df.iterrows():
        if cnt % 500 == 0:
            print('processing:', cnt / len(df), '%')

        # if (row['ltable_id'] != row['rtable_id']) and row['predicted_probs'] > 0.6:
        #     '''for test'''
        #     # mergeId.append((row['ltable_id'], row['rtable_id']))
        #     # print((row['ltable_id'], row['rtable_id']))
        #     if cnt == 0:
        #         apply_table.loc[row['ltable_id'] - 1, 'predictClusterId'] = PredictClusterId
        #         apply_table.loc[row['rtable_id'] - 1, 'predictClusterId'] = PredictClusterId
        #         cnt += 1
        #         # PredictClusterId += 1
        #     else:
        #         if apply_table.loc[row['ltable_id'] - 1, 'predictClusterId'] == None \
        #                 and apply_table.loc[row['rtable_id'] - 1, 'predictClusterId'] != None:
        #             apply_table.loc[row['ltable_id'] - 1, 'predictClusterId'] = PredictClusterId
        #             cnt += 1
        #
        #         if apply_table.loc[row['ltable_id'] - 1, 'predictClusterId'] != None \
        #                 and apply_table.loc[row['rtable_id'] - 1, 'predictClusterId'] == None:
        #             apply_table.loc[row['rtable_id'] - 1, 'predictClusterId'] = PredictClusterId
        #             cnt += 1
        #
        #         # New
        #         if apply_table.loc[row['ltable_id'] - 1, 'predictClusterId'] == None \
        #                 and apply_table.loc[row['rtable_id'] - 1, 'predictClusterId'] == None:
        #             # print((row['ltable_id'], row['rtable_id'], row['predicted_probs']))
        #             PredictClusterId += 1
        #             apply_table.loc[row['ltable_id'] - 1, 'predictClusterId'] = PredictClusterId
        #             apply_table.loc[row['rtable_id'] - 1, 'predictClusterId'] = PredictClusterId
        #             cnt += 1

        if (row['ltable_id'] != row['rtable_id']) and (row['predicted_probs'] <= 0.6 and row['predicted_probs'] >= 0.4):
            cnt += 1
            quesId.append(row.tolist())
            # print(quesId)

    # print(mergeId)
    # print(cluster)
    print(apply_table.head(n=200))
    print(quesId)

    # 虽然效率低，但是搞出来就行了
    with open('training_question_from_predict.csv', 'a+') as file:
        csv.writer(file, lineterminator = '\n').writerows(quesId)

    # apply_table.to_csv(path + '/cluster_from_predict.csv', index=False)

def get_golden():
    '''
    :return: Merge those pairs/ tuples with high predicted probability
    '''
    df = pd.read_csv(path + '/cluster_from_predict.csv')
    # 删除表中含有任何NaN的行
    df = df.dropna(axis=0, how='any')
    print(df.head(n=100))
    grouped_df = df.groupby('predictClusterId')
    group_num = len(grouped_df)
    attrs = list(df.columns.values)
    new_df = pd.DataFrame(columns=attrs)
    i = 0

    for eachgroup in grouped_df:
        print(i)
        # print(eachgroup)
        record = []
        for each_attr in attrs:
            majority = Counter(eachgroup[1][each_attr].tolist()).most_common(1)[0][0]
            record.append(majority)
        new_df.loc[i] = record
        i += 1

    new_df.to_csv(path + '/gold_from_predict.csv', index=False)


if __name__ == '__main__':
    # get_golden()
    myPair2Cluster()