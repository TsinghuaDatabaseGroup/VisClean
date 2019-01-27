import pandas as pd
import numpy as np

from pyecharts import Bar

class Visualization(object):

    def __init__(self, x_data, y_data):
        self.x_data = x_data
        self.y_data = y_data


    def render(self):
        print('render visualization')
        bar = Bar("Title", "Subtitle")
        bar.add("图例名称",
                self.x_data,
                self.y_data,
                is_datazoom_show=True,
                datazoom_type="both",)
        # bar.print_echarts_options() # 该行只为了打印配置项，方便调试时使用
        bar.render(path='../vis/render.html')    # 生成本地 HTML 文件
        bar.render(path='../vis/snapshot.png') # 生成本地 png 文件