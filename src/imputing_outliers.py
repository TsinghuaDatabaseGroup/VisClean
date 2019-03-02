"""Detect outliers from the table"""
import pandas as pd
import numpy as np

'''
We assume that the data is follow the normal distribution.
Our approach was to detect the outlier points by eliminating any points that
were above (Mean + 2*SD) and any points below (Mean - 2*SD) before plotting the frequencies.
'''

class Outlier(object):
    def __init__(self):
        pass

    def outlier_detection(self):
        pass


if __name__ == "__main__":
    path = '/Users/yuyu/Documents/GitHub/VisClean/dataset/DBConf/expr_tmp/DBPublications-input_id.csv'
    df = pd.read_csv(path)
    # print(df.head())

    detect_attr = 'Citations'

    # '''Delete those tuples that the detect_attr is missing'''
    #  the current auto ignore the null value in pandas
    # df = df.dropna(subset=[detect_attr])

    # compute the mean mu, and the standard deviation for normal distribution.
    mu = np.mean(df[detect_attr])  # 57.326
    sigma = np.std(df[detect_attr])  # 174.042  # 标准差
    print(mu, sigma)

    # Detect the outlier based on the mu/sigma
    for index, row in df.iterrows():
        if row[detect_attr] > mu + 3 * sigma:
            print('the outlier citations:', row[detect_attr], 'the df index:',
                  index, 'get the outlier citations by df.loc', df.loc[index][detect_attr])
        if row[detect_attr] < mu - 3 * sigma:
            print(row)

    # In the next, it should get the index, and generate the outlier question.



