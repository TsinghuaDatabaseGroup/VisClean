import util
import re
import random
import program
import math

class Structure(object):
    def __init__(self, struct):
        self.struct = struct

    def __eq__(self, other):
        if len(self.struct) != len(other.struct):
            return False
        for i in range(len(self.struct)):
            if self.struct[i] != other.struct[i]:
                return False
        return True

    def __ne__(self, other):
        if len(self.struct) != len(other.struct):
            return True
        for i in range(len(self.struct)):
            if self.struct[i] != other.struct[i]:
                return True
        return False

    def __hash__(self):
        re = 1009
        for i in self.struct:
            re = re * 9176 + hash(i)
        return re

    def to_string(self):
        strs = ""
        for i in self.struct:
            strs+= util.regex_str[i]
            strs += '+'
        return strs

class Rule(object):

    def __init__(self, left_id, right_id, left_start, left_end, right_start, right_end, attr, data, left_structure=None, right_structure=None):
        self.left_id = left_id
        self.right_id = right_id
        self.left_start = left_start
        self.right_start = right_start
        self.left_end = left_end
        self.right_end = right_end
        self.attr = attr
        if not left_structure:
            self.left_structure = self.calculate_structure(self.get_left_str(data))
            self.right_structure = self.calculate_structure(self.get_right_str(data))
        else:
            self.left_structure = left_structure
            self.right_structure = right_structure

    def reverse_execute(self, left, right):
        return right, left

    def reverse(self, data):
        left_id, right_id = self.reverse_execute(self.left_id, self.right_id)
        left_start, right_start = self.reverse_execute(self.left_start, self.right_start)
        left_end, right_end = self.reverse_execute(self.left_end, self.right_end)
        left_structure, right_structure = self.reverse_execute(self.left_structure, self.right_structure)
        return Rule(left_id, right_id, left_start, left_end, right_start, right_end, self.attr, data,
                    left_structure, right_structure)

    def calculate_structure(self, ss):
        base = 0
        structs = []
        while base < len(ss):
            added = False
            for p in range(len(util.regexes)):
                pattern = util.regexes[p]
                m = re.search(pattern, ss[base : ])
                if m == None:
                    continue
                else:
                    match_str = m.group()
                    structs.append(p)
                    base += len(match_str)
                    added = True
                    break
            if not added:
                base += 1
                structs.append(11)
        return Structure(structs)

    def get_left_struct(self):
        return self.left_structure

    def get_right_struct(self):
        return self.right_structure

    def get_left_str(self, data):
        return str(data.loc[self.left_id, self.attr])[self.left_start: self.left_end]

    def get_right_str(self, data):
        return str(data.loc[self.right_id, self.attr])[self.right_start: self.right_end]

    def compare_structs(self):
        return self.left_structure == self.right_structure

    def compare_length(self):
        return (self.left_end - self.left_start) >= (self.right_end - self.right_start)


class DataRepair(object):
    def __init__(self, data):
        self.data = data.set_index('id')
        self.rules = {}
        self.transforms = {}
        self.transform_group_by_structure = {}
        self.program_paths = {}
        self.question_id = {}
        self.segment_tag = {}
        # indicate whether segment has been changed

    def copy(self, data):
        new_dr = DataRepair(data)
        new_dr.program_paths = self.program_paths
        new_dr.question_id = self.question_id
        new_dr.rules = self.rules
        new_dr.transform_group_by_structure = self.transform_group_by_structure
        new_dr.transforms = self.transforms
        return new_dr

    def construct(self, attrs):
        for attr in attrs:
            self.gen_match_pairs(attr)
            self.select_transformation_1(attr)
            self.group_transformation_by_structure(attr)
            self.group_transformation_by_program(attr)

    def longest_common_subsequence(self, left, right):
        length = [[0 for i in range(len(right)+1)] for j in range(len(left)+1)]
        path = [[(-1, -1) for i in range(len(right)+1)] for j in range(len(left)+1)]
        for i in range(1, len(left)+1):
            for j in range(1, len(right)+1):
                if left[i-1] == right[j-1]:
                    length[i][j] = length[i-1][j-1] + 1
                    path[i][j] = (i-1, j-1)
                else:
                    if length[i-1][j] >= length[i][j-1]:
                        length[i][j] = length[i-1][j]
                        path[i][j] = (i-1, j)
                    else:
                        length[i][j] = length[i][j-1]
                        path[i][j] = (i, j-1)
        i, j = len(left), len(right)
        left_end = len(left)
        right_end = len(right)
        rules = []
        # print length
        # print path
        while i > 0 and j > 0:
            if left[i-1] == right[j-1]:
                left_seg = left[i: left_end]
                right_seg = right[j: right_end]
                if len(left_seg) > 0 or len(right_seg) > 0:
                    rules.append(((i, left_end), (j, right_end)))
                left_end = i - 1
                right_end = j - 1
            i, j = path[i][j]
        left_seg = left[0: left_end]
        right_seg = right[0: right_end]
        if len(left_seg) > 0 or len(right_seg) > 0:
            rules.append(((0, left_end), (0, right_end)))
        return rules

    def segid2pos(self, segs, seg_start, seg_end):
        start = -1
        for i in range(0, seg_start):
            start += len(segs[i])
            start += 1
        start += 1
        length = 0
        for i in range(seg_start, seg_end):
            length += len(segs[i])
            length += 1
        if length > 0:
            length -= 1
        return start, start + length

    def lcs_align(self, left_id, right_id, attr):
        left_str = str(self.data.loc[left_id, attr])
        right_str = str(self.data.loc[right_id, attr])
        rules = []
        for rule in self.longest_common_subsequence(left_str.split(" "), right_str.split(" ")):
            left_start, left_end = self.segid2pos(left_str.split(" "), rule[0][0], rule[0][1])
            right_start, right_end = self.segid2pos(right_str.split(" "), rule[1][0], rule[1][1])
            rules.append(Rule(left_id, right_id, left_start, left_end, right_start, right_end, attr, self.data))
        return rules

    def gen_match_pairs(self, attr):
        '''
        :return: rule set
        '''
        grouped_data = self.data.groupby(['cluster_id']).groups
        self.rules[attr] = []
        # this is a dict {group name -> group labels}
        for k, v in grouped_data.iteritems():
            for i in range(len(v)):
                for j in range(i+1, len(v)):
                    self.rules[attr].extend(self.lcs_align(v[i], v[j], attr))
        print len(self.rules[attr])

    def select_transformation_1(self, attr):
        assert self.rules.has_key(attr)
        self.transforms[attr] = []
        for rule in self.rules[attr]:
            if rule.compare_structs():
                if rule.compare_length():
                    self.transforms[attr].append(rule)
                else:
                    self.transforms[attr].append(rule.reverse(self.data))
            else:
                self.transforms[attr].append(rule.reverse(self.data))
                self.transforms[attr].append(rule)

    def select_transformation_2(self, this, that, attr):
        '''
        find longer one in struct duplicates
        :param this:
        :param that:
        :param attr:
        :return:
        '''
        assert self.transforms.has_key(attr)
        # sample some transform to see which is longer
        sample_size = min(len(this), len(that))
        randIndex = random.sample(range(len(this)), sample_size / 10 + 1)
        left_total, right_total = 0, 0
        for i in randIndex:
            left_total += this[i]
            right_total += that[i]
        return left_total >= right_total

    def group_transformation_by_structure(self, attr):
        assert self.transforms.has_key(attr)
        group = {}
        # all the groups
        struct_tag = {}
        # with tag indicate whether has been dedup
        for tt in range(len(self.transforms[attr])):
            t = self.transforms[attr][tt]
            key = (t.get_left_struct(), t.get_right_struct())
            if group.has_key(key):
                group[key].append(tt)
            else:
                group[key] = [tt]
                struct_tag[key] = 1
        selected_transform_groups = {}
        # final result
        for k, v in struct_tag.iteritems():
            if v == 0:
                continue
            else:
                if k[0] != k[1] and struct_tag.has_key((k[1], k[0])) and struct_tag[(k[1], k[0])] == 1:
                    if self.select_transformation_2(group[k], group[(k[1], k[0])], attr):
                        struct_tag[(k[1], k[0])] = 0
                        selected_transform_groups[k] = group[k]
                    else:
                        struct_tag[k] = 0
                else:
                    selected_transform_groups[k] = group[k]
        self.transform_group_by_structure[attr] = selected_transform_groups


    def compare_group(self, group1, group2):
        if len(group1[1]) < len(group2[1]):
            return 1
        elif len(group1[1]) == len(group2[1]):
            return 0
        else:
            return -1

    def group_transformation_by_program(self, attr):
        print "group_transformation_by_program for attribute " + attr
        assert self.transform_group_by_structure.has_key(attr)
        path_groups = []
        freq_global = {}

        graphs_global = [None for i in range(len(self.transforms[attr]))]
        str_pair_graph_mapping = {}
        for structure, transforms in self.transform_group_by_structure[attr].iteritems():
            for transform in transforms:
                left_str = self.transforms[attr][transform].get_left_str(self.data)
                right_str = self.transforms[attr][transform].get_right_str(self.data)
                if str_pair_graph_mapping.has_key((left_str, right_str)):
                    graphs_global[transform] = graphs_global[str_pair_graph_mapping[(left_str, right_str)][0]].copy(transform)
                    str_pair_graph_mapping[(left_str, right_str)].append(transform)
                else:
                    graphs_global[transform] = program.Graph(transform, left_str, right_str)
                    str_pair_graph_mapping[(left_str, right_str)] = [transform]

        print "Graphs construction completed: " + str(len(graphs_global))

        for g in range(len(graphs_global)):
            graph = graphs_global[g]
            if not graph:
                continue
            for i in range(len(graph.vertices)):
                for edge in graph.edges[i]:
                    for label in edge.labels:
                        if isinstance(label, program.ConstStr):
                            strs = label.get_result()
                            if freq_global.has_key(strs):
                                freq_global[strs] += 1
                            else:
                                freq_global[strs] = 1

        print "Const Term construction completed: " + str(len(freq_global))



        for structure, transforms in self.transform_group_by_structure[attr].iteritems():
            print structure[0].to_string() + "--->" + structure[1].to_string() + " started"
            print len(transforms)
            graphs = []
            current_common_size = {}
            for transform in transforms:
                new_graph = graphs_global[transform]
                graphs.append(new_graph)


            def compare_label(a, b):
                '''
                optimize: ranking const string labels
                :param a:
                :param b:
                :return:
                '''
                if (isinstance(a, program.Prefix) or isinstance(a, program.Suffix)) and not (isinstance(b, program.Prefix) or isinstance(b, program.Suffix)):
                    return -1
                if not (isinstance(a, program.Prefix) or isinstance(a, program.Suffix)) and (isinstance(b, program.Prefix) or isinstance(b, program.Suffix)):
                    return 1
                if isinstance(a, program.SubStr) and isinstance(b, program.SubStr):
                    return 0
                if isinstance(a, program.SubStr) and isinstance(b, program.ConstStr):
                    return -1
                if isinstance(b, program.SubStr) and isinstance(a, program.ConstStr):
                    return 1
                if isinstance(a, program.ConstStr) and isinstance(b, program.ConstStr):
                    score_a = freq_struct[a.get_result()] / math.sqrt(freq_global[a.get_result()] - freq_struct[a.get_result()] + 1)
                    score_b = freq_struct[b.get_result()] / math.sqrt(freq_global[b.get_result()] - freq_struct[b.get_result()] + 1)
                    if score_a > score_b:
                        return -1
                    elif score_a == score_b:
                        return 0
                    else:
                        return 1
                return 0

            freq_struct = {}
            for g in range(len(graphs)):
                graph = graphs[g]
                for i in range(len(graph.vertices)):
                    for edge in graph.edges[i]:
                        for label in edge.labels:
                            if isinstance(label, program.ConstStr):
                                strs = label.get_result()
                                if freq_struct.has_key(strs):
                                    freq_struct[strs] += 1
                                else:
                                    freq_struct[strs] = 1
            print "ConstStr Label Frequency Construction completed"

            local_const_labels = []
            for g in range(len(graphs)):
                for i in range(len(graphs[g].vertices)):
                    for e in range(len(graphs[g].edges[i])):
                        for label in graphs[g].edges[i][e].labels:
                            if isinstance(label, program.ConstStr):
                                local_const_labels.append(label)
            local_const_labels_dedup = list(set(local_const_labels))
            local_const_labels = sorted(local_const_labels_dedup, cmp=compare_label)[0:min(len(local_const_labels_dedup), 10)]
            local_const_labels_map = {}
            for l in local_const_labels:
                local_const_labels_map[l] = True

            for g in range(len(graphs)):
                for i in range(len(graphs[g].vertices)):
                    for e in range(len(graphs[g].edges[i])):
                        labels = []
                        for label in graphs[g].edges[i][e].labels:
                            if isinstance(label, program.ConstStr) and (local_const_labels_map.has_key(label)):
                                labels.append(label)
                            elif not isinstance(label, program.ConstStr):
                                labels.append(label)
                        graphs[g].edges[i][e].labels = sorted(labels, cmp=compare_label)[0:min(len(labels), 3)]
            print "Label Selection completed"

            # Construct Inverse List
            InverseList = {}
            for g in range(len(graphs)):
                graph = graphs[g]
                for i in range(len(graph.vertices)):
                    for edge in graph.edges[i]:
                        for label in edge.labels:
                            if InverseList.has_key(label):
                                InverseList[label].append((graph.id, edge.src, edge.dst))
                            else:
                                InverseList[label] = [(graph.id, edge.src, edge.dst)]
            print "Label Inverse List Construct completed"
            # find pivot path
            paths = {}
            str_pair_path_groups_mapping = {}
            for graph in graphs:
                left_str = self.transforms[attr][graph.id].get_left_str(self.data)
                right_str = self.transforms[attr][graph.id].get_right_str(self.data)
                print (left_str, right_str)
                if str_pair_path_groups_mapping.has_key((left_str, right_str)):
                    continue
                path = program.Path([])
                path_max = program.Path([])
                gragh_with_common_path_max = []
                if len(graph.vertices) > 0:
                    self.search_pivot(path, [], 0, path_max, gragh_with_common_path_max, InverseList, graph, current_common_size)
                paths[path_max] = gragh_with_common_path_max
                print graph.s + "--->" + graph.t
                print path_max.to_string(), len(gragh_with_common_path_max)
                str_pair_path_groups_mapping[(left_str, right_str)] = True
            # graph id in gragh_with_common_path_max is same as corresponding transformation id
            path_groups.extend(paths.items())
            print structure[0].to_string() + "--->" + structure[1].to_string() + " completed"
        self.program_paths[attr] = sorted(path_groups, cmp=self.compare_group)

    def intersect_with_graph_inverse(self, graphs1, graphs2):
        result = []
        left = {}
        for graph1 in graphs1:
            left[(graph1[0], graph1[2])] = 0
        for graph2 in graphs2:
            if left.has_key((graph2[0], graph2[1])):
                result.append((graph2[0], 0, graph2[2]))
        return result

    def get_first_graph_inverse(self, graphs):
        result = []
        for graph in graphs:
            if graph[1] == 0:
                result.append(graph)
        return result

    def search_pivot(self, path, gragh_with_common_path, i, path_max, gragh_with_common_path_max, inverse, graph, current_common_size):
        for edge in graph.edges[i]:
            for label in edge.labels:
                new_path = program.Path(path.path[:])
                new_path.path.append(label)
                if i == 0:
                    new_gragh_with_common_path = self.get_first_graph_inverse(inverse[label])
                else:
                    new_gragh_with_common_path = self.intersect_with_graph_inverse(gragh_with_common_path, inverse[label])
                if len(new_gragh_with_common_path) > len(gragh_with_common_path_max) and\
                        (not current_common_size.has_key(graph.id) or
                                 len(new_gragh_with_common_path) >= current_common_size[graph.id]) and len(path.path) < 7:
                    if edge.dst == len(graph.vertices):
                        path_max.path = new_path.path
                        del gragh_with_common_path_max[:]
                        gragh_with_common_path_max.extend(new_gragh_with_common_path)
                        for entry in gragh_with_common_path_max:
                            if not current_common_size.has_key(entry[0]):
                                current_common_size[entry[0]] = len(gragh_with_common_path_max)
                            elif len(gragh_with_common_path_max) > current_common_size[entry[0]]:
                                current_common_size[entry[0]] = len(gragh_with_common_path_max)
                    else:
                        self.search_pivot(new_path, new_gragh_with_common_path, edge.dst, path_max, gragh_with_common_path_max, inverse, graph, current_common_size)

    def pop_transformation(self, attr):
        '''
        :param attr:
        :return: a pair of path <--> list(graph_id)
        '''
        if not self.question_id.has_key(attr):
            self.question_id[attr] = 0
        if self.program_paths.has_key(attr) and self.question_id[attr] < len(self.program_paths[attr]):
            result = self.program_paths[attr][self.question_id[attr]]
            group_ids = []
            for i in result[1]:
                group_ids.append(i[0])
            self.question_id[attr] += 1
            return result[0], group_ids
        else:
            return None, None

    def apply_transformation(self, group, attr):
        assert group
        for r in group:
            rule = self.transforms[attr][r]
            left_key = rule.left_id
            right_key = rule.right_id
            if self.segment_tag.has_key(left_key) or self.segment_tag.has_key(right_key):
                continue
            self.data.loc[rule.left_id, rule.attr] = str(self.data.loc[rule.left_id, rule.attr])[: rule.left_start] +\
                                                     rule.get_right_str(self.data) +\
                                                     str(self.data.loc[rule.left_id, rule.attr])[rule.left_end :]
            self.segment_tag[rule.left_id] = True
        return self.data.reset_index()
