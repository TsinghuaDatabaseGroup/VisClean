import pandas as pd
import json
import numpy as np
import sys
import os

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
    # data["x_data"] = df.groupby('Venue').sum()[['Citations']].index.T.tolist()
    # data["y_data"] = df.groupby('Venue').sum()[['Citations']].values.T.tolist()[0]
    data["x_data"] = df.groupby('Venue').sum()[['Citations']].reset_index().sort_values('Citations',
                                                                                        ascending=False).values.T.tolist()[
        0]
    data["y_data"] = df.groupby('Venue').sum()[['Citations']].reset_index().sort_values('Citations',
                                                                                        ascending=False).values.T.tolist()[
        1]
    #print(len(data["x_data"]))

    '''
    Write data["y_data"] to the txt file as the visualization, which for compute the dist later.
    current_vis ==interaction==> cleaned_vis
    '''
    vis_path = os.path.abspath(
        os.path.join(os.path.dirname(os.path.abspath(__file__)), '../dataset/DBConf/expr_tmp/vis'))
    # copy current_vis.txt to cleaned_vis.txt
    current_vis = np.loadtxt(vis_path + "/current_vis.txt")
    np.savetxt(vis_path + "/cleaned_vis.txt", np.sort(current_vis, axis = None))
    # save new possible visualization as the current_vis.txt
    np.savetxt(vis_path + "/current_vis.txt", np.sort(data["y_data"], axis = None))

    print(json.dumps(data))


if __name__ == '__main__':
    # path = '/Users/yuyu/Documents/GitHub/VisClean/dataset/DBConf' + '/expr_tmp'
    # table_path = path + '/DBPublications-input_id.csv' # origin table -- dirty table
    # visQuery(table_path, 'Venue', 'Citations', 'sum')

    visQuery(sys.argv[1], 'Venue', 'Citations','sum')
    # res.to_csv("queryRes.csv")