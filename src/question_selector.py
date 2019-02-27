import pandas as pd
import sys
import json

def jaccard_similarity(list1, list2):
    s1 = set(list1)
    s2 = set(list2)
    return len(s1.intersection(s2)) / len(s1.union(s2))

# 选择滑动窗口
def slide_window(table_path):
    '''
    :param table_path: D'的路径，其中D'是指每轮迭代更新之后的数据集
    :return: 返回滑动窗口的数据，这里把所有数据都返回，前端的slide window直接取其前十个即可
    应该从candidate bars中select top-10 most benefit bars and then return to the user
    '''
    '''
    【假设】
    这里在用一个启发式规则，因为dirty data的long tail效应，我们most benefit bars往往是在top-50 candidate bars中产生的
    '''
    df = pd.read_csv(table_path)
    data = {"x_data": [], "y_data": []}
    data["x_data"] = \
        df.groupby('Venue').sum()[['Citations']].reset_index().sort_values('Citations',
                                                                           ascending=False).values.T.tolist()[0]
    data["y_data"] = \
        df.groupby('Venue').sum()[['Citations']].reset_index().sort_values('Citations',
                                                                           ascending=False).values.T.tolist()[1]
    # 启发式地取前十个进行比较
    cand_xData = data["x_data"][:50]
    cand_yData = data["y_data"][:50]

    candset_index = {}  # key = (i,j,cand_xData[i],cand_xData[j]) value = res
    # 在计算similarity的时候，要注意把一些公有的lexicon给去掉，例如'Conference','on','of','International'
    remove_lexicon = ['proceedings', 'of', 'on', 'international', 'conference', 'the', 'acm', 'ieee', 'and']
    for i in range(len(cand_xData)):
        for j in range(i + 1, len(cand_xData)):
            conf_1 = cand_xData[i].strip().lower().split(' ')
            conf_2 = cand_xData[j].strip().lower().split(' ')
            conf_1 = [x for x in conf_1 if x != remove_lexicon[0] and x != remove_lexicon[1] and x != remove_lexicon[2]
                      and x != remove_lexicon[3] and x != remove_lexicon[4] and x != remove_lexicon[5] and
                      x != remove_lexicon[6] and x != remove_lexicon[7] and x != remove_lexicon[8]]
            sim = jaccard_similarity(conf_1, conf_2)
            res = sim * (cand_yData[i] + cand_yData[j])  # compute a weighted score
            if res != 0:
                candset_index[(i, j), (cand_xData[i], cand_xData[j])] = res
    # print (res,' , (',cand_xData[i],',',cand_yData[i],') , (',cand_xData[j],',',cand_yData[j],')')

    top_groups = sorted(candset_index.items(), key=lambda x: x[1], reverse=True)

    '''
    Currently, we let the group_size = 1;
    It means that all bars in a window are possible the same entity. (e.g., sigmod conf, sigmod, sigmod'18)
    '''
    # from top_group to get grouped bars
    grouped_bars = []  # [[group1], [group2], [group3]]
    grouped_bars += [list(top_groups[0][0][0])]

    # Let Window Size == 10
    window_size = 10
    bar_cnt = 2

    # [begin] this code block is for selecting one group in a window
    for i in range(1, len(top_groups)):
        if bar_cnt > window_size:
            break
        ifUpdate = False
        for j in range(0, len(grouped_bars)):
            if len(set(grouped_bars[j]) & set(top_groups[i][0][0])) != 0:
                # Update the group_cnt
                if len(set(grouped_bars[j]) & set(top_groups[i][0][0])) > len(grouped_bars[j]) or len(
                                set(grouped_bars[j]) & set(top_groups[i][0][0])) == 1:
                    bar_cnt += len(set(grouped_bars[j]) & set(top_groups[i][0][0]))
                # append value into the same group
                update_group = set(grouped_bars[j]) | set(top_groups[i][0][0])
                grouped_bars[j] = list(update_group)
                ifUpdate = True
            if bar_cnt > window_size:
                break
        if ifUpdate == False:
            # append new value (add a new group)
            pass

    # [end] this code block is for selecting one group in a window

    # [begin] this code block is for selecting several groups in a window
    # for i in range(1,len(top_groups)):
    #     if bar_cnt > window_size:
    #         break
    #     ifUpdate = False
    #     for j in range(0,len(grouped_bars)):
    #         if len(set(grouped_bars[j]) & set(top_groups[i][0][0])) != 0:
    #             # Update the group_cnt
    #             if len(set(grouped_bars[j]) & set(top_groups[i][0][0])) > len(grouped_bars[j]) or len(set(grouped_bars[j]) & set(top_groups[i][0][0])) == 1:
    #                  bar_cnt += len(set(grouped_bars[j]) & set(top_groups[i][0][0]))
    #             # append value into the same group
    #             update_group = set(grouped_bars[j]) | set(top_groups[i][0][0])
    #             grouped_bars[j] = list(update_group)
    #             ifUpdate = True
    #         if bar_cnt > window_size:
    #             break
    #     if ifUpdate == False:
    #         # append new value
    #         update_bar_cnt = bar_cnt + len(list(top_groups[i][0][0]))
    #         if update_bar_cnt <= window_size + 2:
    #             grouped_bars += [list(top_groups[i][0][0])]
    #             group_cnt = update_bar_cnt
    #         if group_cnt > window_size:
    #             break
    # [end] this code block is for selecting several groups in a window

    data["x_data"] = []
    data["y_data"] = []
    for i in range(0, len(grouped_bars)):
        data["x_data"].append([])
        data["y_data"].append([])
        for each_value in grouped_bars[i]:
            data["x_data"][i] += [cand_xData[each_value]]
            data["y_data"][i] += [cand_yData[each_value]]

    # print(len(data["x_data"]))
    print(json.dumps(data))


# 在这个version，ans_slide_window主要是做data consolidation的工作。
# Apply the answer from users
# 根据用户在window里面的interaction来进行数据集的更新  // 直接更新gold_from_predict.csv
def consolidation(table_path, answer):
    def value_cleaning(x):
        for li in group_answer:
            if x in li[1:]:
                return li[0]
        return x

    # answer = sigmod+sigmod Conf,Vldb+VLDB,Tkde+IEEE TKDE
    answer = answer.split(',')

    group_answer = []

    for each in answer:
        group_answer.append(each.split('+'))

    df = pd.read_csv(table_path)
    df['Venue'] = df['Venue'].map(value_cleaning)

    # output csv
    df.to_csv(table_path, index=False)
    print(json.dumps({"successfuly": 1}))

# get the training pair question candidate set.
def ques_training(table_path):
    df = pd.read_csv(table_path)
    print(df.loc[0].to_json())

# resort the bar of each bar chart.
def resort(table_path):
    df = pd.read_csv(table_path)
    data = {"x_data": [], "y_data": []}
    data["x_data"] = \
        df.groupby('Venue').sum()[['Citations']].reset_index().sort_values('Venue',
                                                                           ascending=True).values.T.tolist()[0]
    data["y_data"] = \
        df.groupby('Venue').sum()[['Citations']].reset_index().sort_values('Venue',
                                                                           ascending=True).values.T.tolist()[1]
    # print(len(data["x_data"]))
    print(json.dumps(data))

if __name__ == '__main__':
    # path = '/Users/yuyu/Project/VisClean/dataset/DBConf'
    # table_path = path + '/gold_from_predict.csv'
    # slide_window(table_path)
    # table_path = path + '/training_question_from_predict.csv'
    # ques_training(table_path)

    if sys.argv[1] == 'slide_window':
        slide_window(sys.argv[2])

    # if sys.argv[1] == 'ans_slide_window':
    #     ans_slide_window(sys.argv[2])

    if sys.argv[1] == 'ans_slide_window':
        consolidation(sys.argv[2], sys.argv[3])

    if sys.argv[1] == 'ques_training':
        ques_training(sys.argv[2])

    if sys.argv[1] == 'req_resort':
        resort(sys.argv[2])