import pandas as pd
import time

class Node(object):
    def __init__(self, id="", node1=None, node2=None):
        if node1 != None:
            self.ids = []
            self.ids.extend(node1.ids)
            self.ids.extend(node2.ids)
        else:
            self.ids = [id]

    def get_ids(self):
        return self.ids

class Pair2cluster(object):
    '''
    :param A_table: the entire dataset
    :param apply_table: the predict dataset
    '''
    def __init__(self, A_table, B_table, apply_table):
        self.A_table = A_table
        self.B_table = B_table
        self.apply_table = apply_table
        self.nodes = [] # all the nodes, new node appended behind
        self.ids_pointer = {} # point to the current node containing its id, id->node_position

    def constructCluster(self):
        # construct leaf node
        A_table_size = len(self.A_table)
        count = 0
        for row in self.A_table.itertuples():
            # if count % 100 == 0:
                # print str(count)+'/'+str(A_table_size)
            id = int(getattr(row,'id'))
            self.nodes.append(Node(id))
            self.ids_pointer[id] = len(self.nodes) - 1
            count += 1
        # construct higher level nodes
        apply_table_size = len(self.apply_table)
        count = 0
        for row in self.apply_table.itertuples():
            ltable_id = int(getattr(row,'ltable_id'))
            rtable_id = int(getattr(row,'rtable_id'))
            left_node_id = self.ids_pointer[ltable_id]
            right_node_id = self.ids_pointer[rtable_id]
            if left_node_id != right_node_id:
                self.nodes.append(Node("", self.nodes[left_node_id], self.nodes[right_node_id]))
                for ii in self.nodes[left_node_id].get_ids():
                    self.ids_pointer[int(ii)] = len(self.nodes) - 1
                for ii in self.nodes[right_node_id].get_ids():
                    self.ids_pointer[int(ii)] = len(self.nodes) - 1
            count += 1
        ids = []
        cluster_id = {}
        cluster_id_ordered = []
        print ("generate cluster_id")
        count = 0
        for row in self.A_table.itertuples():
            id = int(getattr(row, 'id'))
            cluster_id[id] = self.ids_pointer[id]
            count += 1
        #print (self.A_table.dtypes)
        print ("join with origin table")
        result = self.A_table.copy()
        length = len(result)
        cnt = 0
        for row in result.itertuples():
#             if cnt % 1000 == 0:
#                 print (cnt, '/', length)
            cluster_id_ordered.append(cluster_id[int(row.id)])
            cnt += 1
        result['cluster_id'] = pd.Series(cluster_id_ordered).values
        return result

if __name__ == '__main__':
    path = '/Users/yuyu/Documents/GitHub/VisClean/dataset/DBConf/expr_tmp'
    apply_table_path = path + '/rf_predict.csv'
    A_table_path = path + '/DBPublications-input_id.csv'
    A_table = B_table = pd.read_csv(A_table_path)
    apply_table = pd.read_csv(apply_table_path)
    # 过滤出 predicted = 1的tuple pair 认为（ > 0.6才是1）
    apply_table = apply_table[apply_table['predicted_probs'] >= 0.6]

    start_time = time.time()
    myPair2Cluster = Pair2cluster(A_table, B_table, apply_table)
    result = myPair2Cluster.constructCluster()
    result.to_csv(path + '/cluster_from_predict.csv', index=False)
    print("Time for getting cluster from matching pairs:", time.time() - start_time)