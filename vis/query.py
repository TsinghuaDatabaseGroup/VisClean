import pandas as pd
import json
import sys
def visQuery(TablePath, GroupByCol, AggCol, AggFuc):
    '''
    :param TablePath: the path of Dataset D for visualization & cleaning
    :param GroupByCol: the group by column
    :param AggCol: the column for aggregate
    :param AggFuc: the aggregate function
    :return: ruturn the aggregate result over Dataset D
    '''
    df = pd.read_csv(TablePath)
    data = {"x_data": [], "y_data": []}
    data["x_data"] = df.groupby('Venue').sum()[['Citations']].index.T.tolist()
    data["y_data"] = df.groupby('Venue').sum()[['Citations']].values.T.tolist()[0]
    # data["x_data"] = df.groupby('Venue').sum()[['Citations']].reset_index().sort_values('Citations',
    #                                                                                     ascending=False).values.T.tolist()[
    #     0]
    # data["y_data"] = df.groupby('Venue').sum()[['Citations']].reset_index().sort_values('Citations',
    #                                                                                     ascending=False).values.T.tolist()[
    #     1]
    #print(len(data["x_data"]))
    print(json.dumps(data))


if __name__ == '__main__':
    # path = '/Users/yuyu/Project/VisClean/dataset/DBConf'
    # table_path = path + '/gold_from_predict.csv'

    visQuery(sys.argv[1], 'Venue', 'Citations','sum')
    # res.to_csv("queryRes.csv")