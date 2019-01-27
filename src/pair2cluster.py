import pandas as pd

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
        for _, row in self.A_table.iterrows():
            # if count % 100 == 0:
                # print str(count)+'/'+str(A_table_size)
            id = int(row['id'])
            self.nodes.append(Node(id))
            self.ids_pointer[id] = len(self.nodes) - 1
            count += 1
        # construct higher level nodes
        apply_table_size = len(self.apply_table)
        count = 0
        for _, row in self.apply_table.iterrows():
            ltable_id = int(row['l_id'])
            rtable_id = int(row['r_id'])
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
        cluster_id = []
        print ("generate cluster_id")
        count = 0
        for _, row in self.A_table.iterrows():
            id = int(row['id'])
            ids.append(row['id'])
            cluster_id.append(self.ids_pointer[id])
            count += 1
        cluster_table = pd.DataFrame(data={'id': ids, 'cluster_id': cluster_id})
        print ( "join with origin table")
        result = cluster_table.join(self.A_table.set_index('id'), how='inner', on='id', lsuffix='', rsuffix='_r')
        if 'cluster_id_r' in result.columns:
            result.drop('cluster_id_r', axis=1, inplace=True)
        return result