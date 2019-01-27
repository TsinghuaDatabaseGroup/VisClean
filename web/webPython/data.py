#coding:utf-8
import os
import sys
import numpy as np
import pandas as pd
import json

def getTable(path, limit, offset):
    # print('getTable')
    table = pd.read_csv(path)
    data = {"total": len(table)}
    data["rows"] = json.loads(table[int(offset): (int(offset)+int(limit))].to_json(orient='records'))
    # print(type(data['rows']))
    print(json.dumps(data))
    # print(table[(int(limit) * int(offset)): ((int(offset) + 1) * int(limit))].to_json(orient='records'))

if __name__ == '__main__':
    # argv = [
    # '/Users/yuyu/Project/VisClean/dataset/DBConf/DBPublications-input_id.csv',
    # '15',
    # '0']
    # getTable(argv[0],argv[1],argv[2])
    getTable(sys.argv[1], sys.argv[2], sys.argv[3])