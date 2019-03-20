#coding:utf-8
import random
import py_entitymatching as em
import pandas as pd
import pandas_profiling
import os
from collections import Counter
from scipy.stats import wasserstein_distance # known as the earth mover’s distance
import numpy as np
import time
import json

class EntityMatching(object):
    def __init__(self,
                 ltable_path,
                 rtable_path,
                 output_path,
                 key_attr,
                 l_output_attrs,
                 r_output_attrs,
                 attrs_from_table,
                 is_blocking = False, is_save_candidate_feature = False, is_need_label = True):
        '''
        :param ltable_path: the left table path
        :param rtable_path: the right table path
        :param output_path: the output file path (e.g., candidate set, labeled set, predict set, feature set)
        :param key_attr: the key attributes of left/right table for entity matching
        :param l_output_attrs: the output attributes of left table
        :param r_output_attrs: the output attributes of right table
        :param attrs_from_table: similar to l_output_attrs, just add prefix "ltable_"
        :param is_blocking: denoted the input table (left/right table) is need to block or not
        :param is_save_candidate_feature: denoted if save the candidate set C into the disk or not
        :param is_need_label: denoted if have the initialized label dataset or not
        '''
        self.ltable_path = ltable_path
        self.rtable_path = rtable_path
        self.output_path = output_path
        self.key_attr = key_attr
        self.l_output_attrs = l_output_attrs
        self.r_output_attrs = r_output_attrs
        self.attrs_from_table = attrs_from_table
        self.is_blocking = is_blocking
        self.is_save_candidate_feature = is_save_candidate_feature
        self.is_need_label = is_need_label

    def get_blocking(self):
        '''
        :Input: input the left and right table, denoted by A & B
        :return: return the blocking set of A & B (dateaframe)
        '''
        pass

    def update_CandFeature_AB(self, Cand_feature_name, x_axis_name, transformation):
        '''
        :param Cand_feature_name: the file name of candidate feature of blocking candidate set.
        :param x_axis_name: the name of x-axis (e.g., Venue)
        :param transformation: the transformation getting from value standaridization window.
        :return: return None; Just for update. Just save two changed dataset.
        '''
        # 读取原始table A, B; A == B
        A = pd.read_csv(self.ltable_path)
        em.set_key(A,'id')
        # # apply用户反馈的transformation到这些tuple pair上 (直接改原始的数据，py_EM是只读原始的数据的)
        A.loc[A[x_axis_name].isin(transformation[0][1:]), x_axis_name] = transformation[0][0]
        B = A
        # TODO 保存新的entire dataset A,B
        A.to_csv(self.ltable_path, index=False)

        # 读取Blocking 后的candidate set
        Cand_feature = pd.read_csv(self.output_path + Cand_feature_name)

        em.set_key(Cand_feature, '_id')
        em.set_ltable(Cand_feature, A)
        em.set_rtable(Cand_feature, B)
        em.set_fk_ltable(Cand_feature, 'ltable_id')
        em.set_fk_rtable(Cand_feature, 'rtable_id')

        # 获得符合条件的tuple pair index
        to_del_ind = Cand_feature[
            Cand_feature['ltable_'+x_axis_name].isin(transformation[0][1:]) | Cand_feature['rtable_'+x_axis_name].isin(
                transformation[0][1:])].index

        ### 当找到这些满足条件的，然后重新更新Feature
        if len(to_del_ind.tolist()) > 0:
            # print('to_del_ind', to_del_ind)
            # 根据index 将这部分tuple pair单独抽出来成一个dataframe --> to_update_df && 顺便根据user feedback修改一下
            to_update_df = Cand_feature.loc[to_del_ind,:]
            to_update_df.loc[to_update_df['ltable_' + x_axis_name].isin(transformation[0][1:]), 'ltable_' + x_axis_name] = transformation[0][0]
            to_update_df.loc[to_update_df['rtable_' + x_axis_name].isin(transformation[0][1:]), 'rtable_' + x_axis_name] = transformation[0][0]

            # 并且从原来的 Candidate_feature中删除这部分需要被更新的变量
            Cand_feature = Cand_feature.drop(to_del_ind)

            # 对新的 to_update_df 进行相关设定
            em.set_key(to_update_df, '_id')
            em.set_ltable(to_update_df, A)
            em.set_rtable(to_update_df, B)
            em.set_fk_ltable(to_update_df, 'ltable_id')
            em.set_fk_rtable(to_update_df, 'rtable_id')
            l_output_attrs = r_output_attrs = self.l_output_attrs
            attrs_from_table = []
            for var in l_output_attrs:
                attrs_from_table.append('ltable_' + var)
            for var in r_output_attrs:
                attrs_from_table.append('rtable_' + var)

            # 对新的tuple pair计算feature vectors
            feature_table = em.get_features_for_matching(A, B, validate_inferred_attr_types=False)
            updated_L = em.extract_feature_vecs(to_update_df, feature_table=feature_table,
                                                attrs_before=attrs_from_table,
                                                show_progress=True, n_jobs=-1)

            # 将新的feature vectors拼接到Cand_feature上
            Cand_feature = Cand_feature.append(updated_L)
            Cand_feature.sort_index(inplace=True)

            # TODO 保存新的 Cand_feature
            Cand_feature.to_csv(self.output_path + Cand_feature_name, index=False)

        print(json.dumps({"successfuly": 1}))


    def entity_matching(self):
        # Read table from file.
        A = em.read_csv_metadata(self.ltable_path, key='id')
        B = em.read_csv_metadata(self.rtable_path, key='id')
        print(A.head())
        print(B.head())

        # Blocking
        if self.is_blocking == True:
            #TODO Read C from disk
            print("To read C from disk")
            C = pd.read_csv(self.output_path+'/C.csv')
            em.set_key(C, '_id')
            em.set_ltable(C, A)
            em.set_rtable(C, B)
            em.set_fk_ltable(C, 'ltable_id')
            em.set_fk_rtable(C, 'rtable_id')
            print(C.head())
            print("Have read Candidate set from disk")
        else:
            # It's the fist time, so we need block the dataset
            time_block_start = time.time()
            print("Block tables to get candidate set... ...[start]")
            ob = em.OverlapBlocker()
            C = ob.block_tables(A, B, self.key_attr, self.key_attr,
                                l_output_attrs=self.l_output_attrs,
                                r_output_attrs=self.r_output_attrs,
                                overlap_size=5, show_progress=True)
            print('Get candidate set:\n', C.columns.values.tolist())
            print(C.head())
            print("The size of candidate dataset C: len(C) = ", len(C))
            em.to_csv_metadata(C, self.output_path + '/C.csv')
            print("Block tables to get candidate set... ...[end]")
            print("###### Time for Blocking: ", time.time() - time_block_start,"S #####")
        if self.is_need_label == True:
            # Sampling and labeling the candidate set
            print("Sampling and labeling the candidate set")
            S = em.sample_table(C, 50)
            # Label S
            G = em.label_table(S, 'gold')
            G.to_csv(self.output_path + '/labeled.csv', index=False, header=False)
        else:
            # TODO Get Golden directly from file.
            G = em.read_csv_metadata(self.output_path + '/labeled.csv',
                                     key='_id',
                                     ltable=A, rtable=B,
                                     fk_ltable='ltable_id', fk_rtable='rtable_id')

        # Train matcher using labeled data
        '''
        First, we need to create a set of features.
        py_entitymatching provides a way to automatically generate features
        based on the attributes in the input tables.
        For the purposes of this guide, we use the automatically generated features.
        '''
        # Generate features automatically
        time_start_generate_features = time.time()
        feature_table = em.get_features_for_matching(A, B, validate_inferred_attr_types=False)
        # print("Check the output of get_features_for_matching", feature_table)
        # feature_table.to_csv('./feature_table.csv')
        # Select the attrs. to be included in the feature vector table
        # attrs_from_table = ['ltable_name', 'ltable_addr', 'ltable_city', 'ltable_phone',
        #                     'rtable_name', 'rtable_addr', 'rtable_city', 'rtable_phone']
        print("# Convert the labeled data to feature vectors using the feature table")

        H = em.extract_feature_vecs(G,
                                    feature_table=feature_table,
                                    attrs_before=self.attrs_from_table,
                                    attrs_after='gold',
                                    show_progress=False)
        print("###### Time for Feature Extraction:", time.time() - time_start_generate_features, "S ######")
        # Save the feature of label data to csv
        # H.to_csv(self.output_path + '/label_feature.csv', index=False, mode='a', header=True)
        # print("Check the feature of label data\n", H)
        '''
        Imputing Missing Values due to the sk-learn
        '''
        H.fillna(value=0, inplace=True)
        # Impute feature vectors with the mean of the column values.
        # H = em.impute_table(H,
        #                     exclude_attrs=['_id', 'ltable_id', 'rtable_id', 'label'],
        #                     strategy='mean')

        print("# Instantiate the RF Matcher")
        rf = em.RFMatcher()
        print("# Get the attributes to be projected while training")
        attrs_to_be_excluded = []
        attrs_to_be_excluded.extend(['_id', 'ltable_id', 'rtable_id', 'gold'])
        attrs_to_be_excluded.extend(self.attrs_from_table)
        # Train using feature vectors from the labeled data.
        rf.fit(table=H, exclude_attrs=attrs_to_be_excluded, target_attr='gold')

        print("# Predict the matches in the candidate set using trained matcher")
        # Select the attrs. to be included in the feature vector table

        if self.is_save_candidate_feature == True:
            '''
            一般对一个数据集就Blocking一次, 所以只有一个candidate_feature，在多轮Active Learning的周期都是不变的
            但是当apply string transformation后，需要去更新数据源。
            '''
            print("# Read the candidate C feature vector from disk.")
            # Read feature vector of candidate set from csv
            L = pd.read_csv(self.output_path + '/candidate_feature.csv')
            L.fillna(value=0, inplace=True)
            em.set_key(L, '_id')
        else:
            time_extract_feature_from_candidate = time.time()
            # Convert the candidate set to feature vectors using the feature table
            print("# Convert the candidate set to feature vectors using the feature table")
            L = em.extract_feature_vecs(C, feature_table=feature_table,
                                        attrs_before=self.attrs_from_table,
                                        show_progress=True, n_jobs=-1)
            print("# Imputing Missing Values due to the sk-learn")
            L.fillna(value=0, inplace=True)
            L.to_csv(self.output_path + '/candidate_feature.csv', index=False, header=True)
            print("###### Time for feature vectors from C:", time.time() - time_extract_feature_from_candidate, "S ######")

        # Get the attributes to be excluded while predicting
        attrs_to_be_excluded = []
        attrs_to_be_excluded.extend(['_id', 'ltable_id', 'rtable_id'])
        attrs_to_be_excluded.extend(self.attrs_from_table)
        # Predict the matches
        print("Predict the matches")
        time_predict = time.time()
        # return_probs (boolean) prediction probabilities need to be returned
        predictions = rf.predict(table=L, exclude_attrs=attrs_to_be_excluded,
                                 append=True, target_attr='predicted', probs_attr='predicted_probs', return_probs=True,
                                 inplace=False)
        # predictions = svm.predict(table=L, exclude_attrs=attrs_to_be_excluded,
        #                          append=True, target_attr='predicted', inplace=False)
        print(predictions.head())

        # Finally, project the attributes and the predictions from the predicted table.
        # Get the attributes to be projected out
        attrs_proj = []
        attrs_proj.extend(['_id', 'ltable_id', 'rtable_id'])
        attrs_proj.extend(self.attrs_from_table)
        attrs_proj.append('predicted')
        attrs_proj.append('predicted_probs')

        # Project the attributes
        predictions = predictions[attrs_proj]
        print(predictions.head())
        # output the predictions data
        A0 = pd.DataFrame(predictions)
        # em.set_key(A0, 'id')
        print('output the candidate repairs to csv file')
        em.to_csv_metadata(A0, self.output_path + '/rf_predict.csv')

        print("###### Time for predict C and output:", time.time() - time_predict, "S ######")