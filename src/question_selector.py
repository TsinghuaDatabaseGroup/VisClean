import pandas as pd
import sys
import json
import ast
import os
from pprint import pprint
from sliding_window import SlidingWindow
from entity_matching import EntityMatching

def jaccard_similarity(list1, list2):
    s1 = set(list1)
    s2 = set(list2)
    return len(s1.intersection(s2)) / len(s1.union(s2))

def slide_window(path, table_name):
    myWindow = SlidingWindow(path, table_name, x_axis_name="Venue", y_axis_name="Citations")
    df, cand_xData, cand_yData = myWindow.get_data()

    # read and get the question_status from the file.
    with open(path + '/question_status.json') as f:
        question_status = json.load(f)

    # 第一次对这个数据集进行 compute string similarity
    if question_status['Window']['IsFirstSimMatching'] == True:
        # print('True')
        # !!! 只有在第一次计算similarity的时候执行这个函数
        top_groups = myWindow.compute_string_similarity(cand_xData, cand_yData)
        cand_string = myWindow.auto_cleaning_string(df, top_groups)

        # pprint(cand_string[:15])
        # compute and return the window
        window = myWindow.compute_window(cand_string, cand_xData, cand_yData)
        print(json.dumps(window))

        # save the temp string file
        # myWindow.write_string_sim_set(cand_string)
        # update the question_status in the JSON file.
        # question_status['Window']['IsFirstSimMatching'] = False
        # with open(path + '/question_status.json', 'w') as f:
        #     json.dump(question_status, f)

    # 不是第一次；即可以从上次缓存的数据文件中读取。
    else:
        # read and get the string similarity set from the temp file
        cand_string = myWindow.read_string_sim_set('/string_similarity_set.txt')
        # convert the string-list into the nested list
        cand_string = ast.literal_eval(cand_string)
        # compute and return the window
        window = myWindow.compute_window(cand_string, cand_xData, cand_yData)
        print(json.dumps(window))

# 选择滑动窗口
def slide_window_old(path, table_name):
    '''
    :param table_path: D'的路径，其中D'是指每轮迭代更新之后的数据集
    :return: 返回滑动窗口的数据，这里把所有数据都返回，前端的slide window直接取其前十个即可
    应该从candidate bars中select top-10 most benefit bars and then return to the user
    '''
    '''
    【假设】
    这里在用一个启发式规则，因为dirty data的long tail效应，我们most benefit bars往往是在top-50 candidate bars中产生的
    '''
    df = pd.read_csv(path + table_name)
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



# get the training pair question candidate set.
def ques_training(table_path):
    # read and get the question_status and the pair index from the file.
    path = os.path.abspath(
        os.path.join(os.path.dirname(os.path.abspath(__file__)), '../dataset/DBConf/expr_tmp/'))
    with open(path + '/question_status.json') as f:
        question_status = json.load(f)

    if question_status["Training"]["IsFirstTraining"] == True:
        # TODO 如果是第一次训练模型，那么得标注数据，初始化EM模型
        pass
    else:
        # TDOO 如果已经有一次训练好的模型，那么可以从EM模型预测的结果中，挑选Prob为0.6的给用户去标注。
        # Read training pair based on the pair index.
        pair_index = question_status["Training"]["PairIndex"]
        df = pd.read_csv(table_path)
        print(df.loc[pair_index].to_json())
        # TODO modify the JSON style according to the requirement of front-end table

        # update the question_status in the JSON file.
        question_status['Training']['PairIndex'] = pair_index+100
        with open(path + '/question_status.json', 'w') as f:
            json.dump(question_status, f)

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

    if sys.argv[1] == 'slide_window':
        slide_window(sys.argv[2], sys.argv[3])

    if sys.argv[1] == 'ans_slide_window':
        # default setting
        path = '/Users/yuyu/Documents/GitHub/VisClean/dataset/DBConf/expr_tmp'
        ltable_path = path + '/DBPublications-input_id.csv'
        rtable_path = path + '/DBPublications-input_id.csv'
        output_path = path
        key_attr = 'Title'
        l_output_attrs = r_output_attrs = ['Title', 'Authors', 'Venue', 'Year']
        attrs_from_table = []
        for var in l_output_attrs:
            attrs_from_table.append('ltable_' + var)
        for var in r_output_attrs:
            attrs_from_table.append('rtable_' + var)

        myEm = EntityMatching(ltable_path, rtable_path, output_path, key_attr,
                              l_output_attrs, r_output_attrs, attrs_from_table,
                              is_blocking=True, is_save_candidate_feature = True, is_need_label = False)

        # Phase 1: Update directly in window-based pipeline
        # TODO [ok] call consolidation 直接更新gold_from_predict.csv
        myWindow = SlidingWindow(sys.argv[2], sys.argv[3],
                                 x_axis_name="Venue", y_axis_name="Citations")
        myWindow.consolidation(sys.argv[4])

        # Phase 2: update in the EM pipline
        # TODO [] 修改Candidate_feature.csv and entire dataset A,B
        answer = sys.argv[4].split(',')
        group_answer = []
        for each in answer:
            group_answer.append(each.split('+'))


        myEm.update_CandFeature_AB('/candidate_feature.csv', 'Venue', group_answer)

        print(json.dumps({"successfuly": 1}))
        # TODO 修改label.csv
        myEm.update_label('/labeled.csv', mode='Window', x_axis_name='Venue', transformation=group_answer)

        # TODO Retrain the EM model
        myEm.entity_matching()
    # if sys.argv[1] == 'update_candidate_feature_AB':






    if sys.argv[1] == 'ques_training':
        # TODO 根据pair的cluster信息，对齐一些non-standardization values (e.g., )

        # TODO update the label.csv dataset

        # TODO Retrain the EM model
        ques_training(sys.argv[2])


    if sys.argv[1] == 'req_resort':
        resort(sys.argv[2])