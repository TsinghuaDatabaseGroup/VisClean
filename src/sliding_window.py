import py_stringmatching as sm
import pandas as pd
import json
import ast
from pprint import pprint

class SlidingWindow(object):
    def __init__(self,
                 path = '/Users/yuyu/Documents/GitHub/VisClean/dataset/DBConf/expr_tmp',
                 table_name = '/gold_from_predict.csv',
                 x_axis_name="Venue",
                 y_axis_name="Citations"
                 ):
        self.path = path
        self.table_name = table_name
        self.x_axis_name = x_axis_name
        self.y_axis_name = y_axis_name

    def get_data(self):
        df = pd.read_csv(self.path + self.table_name)
        data = {"x_data": [], "y_data": []}
        '''
        Sort the data by y-axis value
        '''
        data["x_data"] = \
            df.groupby(self.x_axis_name).sum()[[self.y_axis_name]].reset_index().sort_values(self.y_axis_name,
                                                                                   ascending=False).values.T.tolist()[0]
        data["y_data"] = \
            df.groupby(self.x_axis_name).sum()[[self.y_axis_name]].reset_index().sort_values(self.y_axis_name,
                                                                                   ascending=False).values.T.tolist()[1]
        cand_xData = data["x_data"]
        cand_yData = data["y_data"]

        return df, cand_xData, cand_yData

    def compute_string_similarity(self, cand_xData, cand_yData):
        '''
        We use the expensive method to compute the similarity string from two sets (e.g., Conference.)
        Some optimizations can be used:
        1. Blocking
        2. Inverted index over string.
        3. Size filter (not suitable here)
        4. prefix filter (not suitable here)
        '''

        '''
        Tokenize all strings in tables A and B only once;
        Store the output of tokenizing in some Python structure
        '''
        # create an alphabetical tokenizer that returns a set of tokens
        alphabet_tok_set = sm.AlphabeticTokenizer(return_set=True)
        string_set = []
        for i in range(len(cand_xData)):
            string_set.append(alphabet_tok_set.tokenize(cand_xData[i].lower()))

        '''
        Call the similarity measure to compute similarity scores
        '''
        generalized_jaccard = sm.GeneralizedJaccard()
        jaccard = sm.Jaccard()
        candset_index = {}  # key = (i,j,cand_xData[i],cand_xData[j]) value = res
        for i in range(len(string_set)):
            for j in range(i + 1, len(string_set)):
                # sim = generalized_jaccard.get_sim_score(string_set[i], string_set[j])
                sim = jaccard.get_sim_score(string_set[i], string_set[j])
                # if the pair sim(str1, str2) > 0.65; we consider it as the same entity(string)
                if sim > 0.7:
                    # compute a weighted score ; 高度为0的柱子不考虑(不考虑也不行呀，不考虑的话会一直都不合并这个柱子)
                    # if cand_yData[i] != 0 and cand_yData[j] != 0:
                    weighted_score = sim * (cand_yData[i] + cand_yData[j])
                    candset_index[(i, j), (cand_xData[i], cand_xData[j]), sim] = weighted_score

        top_groups = sorted(candset_index.items(), key=lambda x: x[1], reverse=True)

        return top_groups

    def auto_cleaning_string(self, df, top_groups):
        '''
        # !!! 只有在第一次计算similarity的时候执行这个函数
        # 考虑字符串大小写问题，自动统一大小写不一致的问题。 ==> automatically cleaning by machine algo.
        #  -- 1.在计算similarity socre的时候，将string全部转成小写
        #  -- 2.在自动统一大小写问题（e.g., SIGMOD; Sigmod）时，自动统一成（SIGMOD / Sigmod ？）
        #  -- 3.然后把automatically cleaning的string pair从candidate set -- top_groups中排除掉
        '''
        cand_string = []  # 更新后的candidate string pairs set
        for i in range(0, len(top_groups)):
            string1 = top_groups[i][0][1][0]
            string2 = top_groups[i][0][1][1]
            string1_standard = string1.strip().lower()
            string2_standard = string2.strip().lower()
            # print(string1, '==>', string2)
            if string1_standard == string2_standard:
                #  -- 1.在计算similarity socre的时候，将string全部转成小写
                #  -- 2.在自动统一大小写问题（e.g., SIGMOD; Sigmod）时，自动统一成（SIGMOD / Sigmod？）
                string1_index = df[self.x_axis_name][df[self.x_axis_name] == string1].index.values.tolist()  # list [1,23,52,35,4241]
                string2_index = df[self.x_axis_name][df[self.x_axis_name] == string2].index.values.tolist()
                # print(string1_index, string2_index)
                for i in string1_index:
                    df.loc[i, self.x_axis_name] = string1.strip()
                for i in string2_index:
                    df.loc[i, self.x_axis_name] = string1.strip()

                    # print(df.iloc[string1_index][x_axis_name], '===', df.iloc[string2_index][x_axis_name])
                    # print(top_groups[i][0][0][0], '==>', top_groups[i][0][0][1])

            else:
                # 3.然后把automatically cleaning的string pair从candidate set -- top_groups中排除掉
                cand_string.append(top_groups[i])

        '''
        将automatically cleaning by machine algo.后更新的数据dataframe保存下来
        '''
        df.to_csv(self.path + self.table_name, index=False)

        return cand_string

    def write_string_sim_set(self, cand_string):
        '''
        !!! 只有在第一次计算好similarity string set后执行这个函数。
        !!! 将计算开销大的stirng_matching 结果存成文件形式。
        Storage the candidate similarity string to the file
        :param str_sim_set:
        :return:
        '''
        fp = open(self.path + '/string_similarity_set.txt', 'w+')
        fp.write(str(cand_string))
        fp.close()

    def read_string_sim_set(self, string_set_name):
        with open(self.path + string_set_name) as f:
            return f.read()


    def compute_window(self, cand_string, cand_xData, cand_yData):
        '''
        Currently, we let the group_size = 1;
        It means that all bars in a window are possible the same entity. (e.g., sigmod conf, sigmod, sigmod'18)
        '''
        # from top_group to get grouped bars
        grouped_bars = []  # [[group1], [group2], [group3]]
        if cand_string != []:
            grouped_bars += [list(cand_string[0][0][0])]  # for the selected bar

        # Let Window Size == 10
        window_size = 10
        bar_cnt = 2

        # [begin] this code block is for selecting one group in a window
        for i in range(1, len(cand_string)):
            if bar_cnt > window_size:
                break
            ifUpdate = False
            for j in range(0, len(grouped_bars)):
                if len(set(grouped_bars[j]) & set(cand_string[i][0][0])) != 0:
                    # Update the group_cnt
                    if len(set(grouped_bars[j]) & set(cand_string[i][0][0])) > len(grouped_bars[j]) or len(
                                    set(grouped_bars[j]) & set(cand_string[i][0][0])) == 1:
                        bar_cnt += len(set(grouped_bars[j]) & set(cand_string[i][0][0]))
                    # append value into the same group
                    update_group = set(grouped_bars[j]) | set(cand_string[i][0][0])
                    grouped_bars[j] = list(update_group)
                    ifUpdate = True
                if bar_cnt > window_size:
                    break
            if ifUpdate == False:
                # append new value (add a new group)
                pass

        window = {"x_data": [], "y_data": []}
        for i in range(0, len(grouped_bars)):
            window["x_data"].append([])
            window["y_data"].append([])
            for j in range(0, len(grouped_bars[i])):
                # window["x_data"][i] += [cand_xData[grouped_bars[i][j]]]
                # window["y_data"][i] += [cand_yData[grouped_bars[i][j]]]

                # 将y-data最大的放在数组首位 TODO bugs
                if j > 0:
                    if cand_yData[grouped_bars[i][j]] > window["y_data"][0][0]:
                        window["x_data"][i] = [cand_xData[grouped_bars[i][j]]] + window["x_data"][i]
                        window["y_data"][i] = [cand_yData[grouped_bars[i][j]]] + window["y_data"][i]
                    else:
                        window["x_data"][i] += [cand_xData[grouped_bars[i][j]]]
                        window["y_data"][i] += [cand_yData[grouped_bars[i][j]]]
                else:
                    window["x_data"][i] += [cand_xData[grouped_bars[i][j]]]
                    window["y_data"][i] += [cand_yData[grouped_bars[i][j]]]

        return window

    # 在这个version，ans_slide_window主要是做data consolidation的工作。
    # Apply the answer from users
    # 根据用户在window里面的interaction来进行数据集的更新  // 直接更新gold_from_predict.csv
    def consolidation(self, answer):
        '''
        直接更新 [gold_from_predict.csv]
        :param table_path: path for 'gold_from_predict.csv'
        :param answer: the user answer (e.g., 'sigmod+sigmod Conf,Vldb+VLDB,Tkde+IEEE TKDE')
        :return: return successful or failed
        '''

        def value_cleaning(x):
            for li in group_answer:
                if x in li[1:]:
                    return li[0]
            return x

        # answer = sigmod+sigmod Conf,Vldb+VLDB,Tkde+IEEE TKDE
        # Update the cleaning dataset from the user answer.
        answer = answer.split(',')
        group_answer = []
        for each in answer:
            group_answer.append(each.split('+'))

        # read the processing cleaning dataset -- gold_from_predict.csv here.
        df = pd.read_csv(self.path+self.table_name)
        df[self.x_axis_name] = df[self.x_axis_name].map(value_cleaning)
        # update and output the new csv
        df.to_csv(self.path+self.table_name, index=False)
        # TODO read the question_status, and check if necessary to update the string_similarity_set.JSON



# Test the class here
if __name__ == "__main__":
    path = '/Users/yuyu/Documents/GitHub/VisClean/dataset/DBConf/expr_tmp'
    table_name = '/gold_from_predict.csv'

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

        # compute and return the window
        window = myWindow.compute_window(cand_string, cand_xData, cand_yData)
        print(json.dumps(window))

        # save the temp string file
        myWindow.write_string_sim_set(cand_string)
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