#coding:utf-8
import sys
# TODO set the path
sys.path.append('/Users/yuyu/Project/[VLDB19]VaClean')
import random
import py_entitymatching as em
import pandas as pd
import pandas_profiling
import os
from collections import Counter
from scipy.stats import wasserstein_distance # known as the earth mover’s distance
import numpy as np


class EntityMatching(object):
    def __init__(self,
                 ltable_path,
                 rtable_path,
                 output_path,
                 key_attr,
                 l_output_attrs,
                 r_output_attrs,
                 attrs_from_table,
                 is_blocking, is_save_candidate_feature, is_need_label):
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

    def update_feature(self):
        '''
        :return: update the feature of candidate set by id
        '''
        pass

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
        else: # It's the fist time, so we need block the dataset
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
        
        if self.is_need_label == True:
            # Sampling and labeling the candidate set
            print("Sampling and labeling the candidate set")
            S = em.sample_table(C, 10)
            # Label S
            G = em.label_table(S, 'gold')
            G.to_csv(self.output_path + '/labeled.csv', index=False, mode='a', header=False)
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
        feature_table = em.get_features_for_matching(A, B, validate_inferred_attr_types=False)
        # print("Check the output of get_features_for_matching", feature_table)
        # Select the attrs. to be included in the feature vector table
        # attrs_from_table = ['ltable_name', 'ltable_addr', 'ltable_city', 'ltable_phone',
        #                     'rtable_name', 'rtable_addr', 'rtable_city', 'rtable_phone']
        print("# Convert the labeled data to feature vectors using the feature table")
        H = em.extract_feature_vecs(G,
                                    feature_table=feature_table,
                                    attrs_before=self.attrs_from_table,
                                    attrs_after='gold',
                                    show_progress=False)
        # Save the feature of label data to csv
        # H.to_csv(self.output_path + '/label_feature.csv', index=False, mode='a', header=True)
        # print("Check the feature of label data\n", H)
        # Imputing Missing Values due to the sk-learn
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
            # Read feature vector of candidate set from csv
            L = pd.read_csv(self.output_path + '/candidate_feature.csv')
            em.set_key(L, '_id')
        else:
            # Convert the candidate set to feature vectors using the feature table
            print("# Convert the candidate set to feature vectors using the feature table")
            L = em.extract_feature_vecs(C, feature_table=feature_table,
                                        attrs_before=self.attrs_from_table,
                                        show_progress=True, n_jobs=-1)
            print("# Imputing Missing Values due to the sk-learn")
            L.fillna(value=0, inplace=True)
            L.to_csv(self.output_path + '/candidate_feature.csv', index=False, mode='a', header=True)
        # Get the attributes to be excluded while predicting
        attrs_to_be_excluded = []
        attrs_to_be_excluded.extend(['_id', 'ltable_id', 'rtable_id'])
        attrs_to_be_excluded.extend(self.attrs_from_table)
        # Predict the matches
        print("Predict the matches")
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



