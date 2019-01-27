'''
Positional functions
'''
import re
import util
import kmp


class ConstPos(object):
    def __init__(self, k):
        self.k = k

    def get_result(self, s):
        if 0 < self.k <= len(s):
            return self.k - 1
        elif 0 > self.k >= -len(s):
            return len(s) + self.k
        else:
            raise RuntimeError('Invalid K in ConstPos')

    def __hash__(self):
        res = 1009
        res = (res + 2) * 9176
        res = res + self.k
        return res

    def __eq__(self, other):
        if not isinstance(other, ConstPos):
            return False
        if other.k != self.k:
            return False
        return True

    def __ne__(self, other):
        if not isinstance(other, ConstPos):
            return True
        if other.k != self.k:
            return True
        return False

    def to_string(self):
        return "ConstPos(" + str(self.k) + ")"

class MatchPos(object):
    def __init__(self, term, k, dir):
        self.term = term
        self.k = k
        self.dir = dir

    def __hash__(self):
        res = 1009
        res = (res + 1) * 9176
        res = (res + hash(self.term)) * 9176
        res = (res + self.k) * 9176
        res += hash(dir)
        return res

    def __eq__(self, other):
        if not isinstance(other, MatchPos):
            return False
        if other.k != self.k:
            return False
        if other.term != self.term:
            return False
        if other.dir != self.dir:
            return False
        return True

    def __ne__(self, other):
        if not isinstance(other, MatchPos):
            return True
        if other.k != self.k:
            return True
        if other.term != self.term:
            return True
        if other.dir != self.dir:
            return True
        return False

    def get_result(self, s):
        matches = re.finditer(self.term, s)
        if not matches:
            return -1
        starts = []
        match_strs = []
        for i in matches:
            starts.append(i.start())
            match_strs.append(i.group())
        m = len(starts)
        if 0 < self.k <= m and bool(dir):
            return starts[self.k - 1]
        elif 0 < self.k <= m and not bool(dir):
            return starts[self.k - 1] + len(match_strs[self.k - 1])
        elif -m <= self.k < 0 and bool(dir):
            return starts[m + self.k]
        elif -m <= self.k < 0 and not bool(dir):
            return starts[m + self.k] + len(match_strs[m + self.k])

    def to_string(self):
        return "MatchPos(" + str(self.term) + "," + str(self.k) + "," + str(self.dir) + ")"


'''
String Functions
'''
class ConstStr(object):
    def __init__(self, x):
        if len(x) < 2:
            a = 1
        self.x = x

    def get_result(self):
        return self.x

    def __hash__(self):
        return hash(self.x)

    def __eq__(self, other):
        if not isinstance(other, ConstStr):
            return False
        if other.x != self.x:
            return False
        return True

    def __ne__(self, other):
        if not isinstance(other, ConstStr):
            return True
        if other.x != self.x:
            return True
        return False

    def to_string(self):
        return "ConstStr(" + self.x + ")"


class SubStr(object):
    def __init__(self, l, r):
        self.l = l
        self.r = r

    def __hash__(self):
        return hash(self.l) * 13 + hash(self.r)

    def __eq__(self, other):
        if not isinstance(other, SubStr):
            return False
        if other.l != self.l or other.r != self.r:
            return False
        return True

    def __ne__(self, other):
        if not isinstance(other, SubStr):
            return False
        if other.l != self.l or other.r != self.r:
            return False
        return True

    def get_result(self, s):
        return s[self.l.get_result(): self.r.get_result()]

    def to_string(self):
        return "SubStr(" + self.l.to_string() + "," + self.r.to_string() + ")"


class Prefix(object):
    def __init__(self, term, k):
        self.term = term
        self.k = k

    def __hash__(self):
        return hash(self.term) * 13 + hash(self.k)

    def __eq__(self, other):
        if not isinstance(other, Prefix):
            return False
        if other.term != self.term or other.k != self.k:
            return False
        return True

    def __ne__(self, other):
        if not isinstance(other, Prefix):
            return True
        if other.term != self.term or other.k != self.k:
            return True
        return False

    def to_string(self):
        return "Prefix(" + self.term + "," + str(self.k) + ")"

class Suffix(object):
    def __init__(self, term, k):
        self.term = term
        self.k = k

    def __hash__(self):
        return hash(self.term) * 13 + hash(self.k)

    def __eq__(self, other):
        if not isinstance(other, Suffix):
            return False
        if other.term != self.term or other.k != self.k:
            return False
        return True

    def __ne__(self, other):
        if not isinstance(other, Suffix):
            return True
        if other.term != self.term or other.k != self.k:
            return True
        return False

    def to_string(self):
        return "Suffix(" + self.term + "," + str(self.k) + ")"

'''
DAG Structure
'''
class Path(object):
    def __init__(self, path):
        self.path = path

    def __hash__(self):
        res = 1009
        for p in self.path:
            res = (res + hash(p)) * 9176
        return res

    def __eq__(self, other):
        if len(self.path) != len(other.path):
            return False
        for i in range(len(self.path)):
            if self.path[i] != other.path[i]:
                return False
        return True

    def __ne__(self, other):
        if len(self.path) != len(other.path):
            return True
        for i in range(len(self.path)):
            if self.path[i] != other.path[i]:
                return True
        return False

    def to_string(self):
        re = ''
        for p in self.path:
            re += '(' + p.to_string() + ')' + '+'
        return re

class Edge(object):
    def __init__(self, src, dst, labels):
        self.src = src
        self.dst = dst
        self.labels = labels

    def add_label(self, label):
        self.labels.append(label)

    def to_string(self):
        res = str(self.src) + ',' + str(self.dst)
        for label in self.labels:
            res += ','
            res += label.to_string()
        return res


class Vertice(object):
    def __init__(self, ch):
        self.name = ch
    def to_string(self):
        return self.name


class Graph(object):

    def __init__(self, id, s, t, rebuild=True):
        self.id = id
        self.vertices = []
        self.edges = []
        self.s = s
        self.t = t
        self.MAX_CONST_LENGTH = 10
        if rebuild:
            self.build_transformation_graph(s, t)

    def copy(self, id):
        new_graph = Graph(id, self.s, self.t, rebuild=False)
        new_graph.vertices = self.vertices
        new_graph.edges = self.edges
        return new_graph

    def add_edge(self, edge, src):
        self.edges[src].append(edge)

    def to_string(self):
        str = "----------------------------------------------------------\nVertices: "
        for v in self.vertices:
            str += v.to_string() + ','
        str += '\nEdges: '
        for es in self.edges:
            for e in es:
                str += e.to_string() + '\n'
        str += "----------------------------------------------------------"
        return str

    def build_transformation_graph(self, s, t):
        '''
        :param s: left str
        :param t: right str
        :return:
        '''
        def compare_pos_function(a, b):
            '''
            :param self:
            :param a:
            :param b:
            :return:
            '''
            if isinstance(a, MatchPos) and isinstance(b, ConstPos):
                return -1
            elif isinstance(b, MatchPos) and isinstance(a, ConstPos):
                return 1
            elif isinstance(a, MatchPos) and isinstance(b, MatchPos):
                left_length = MatchPos(a.term, a.k, False).get_result(s) - MatchPos(a.term, a.k, True).get_result(s)
                right_length = MatchPos(b.term, b.k, False).get_result(s) - MatchPos(b.term, b.k, True).get_result(s)
                if left_length > right_length:
                    return -1
                elif left_length == right_length:
                    return 0
                else:
                    return 1
            else:
                return 0

        P = [[] for i in range(len(s) + 1)]
        for reg in util.regexes_2:
            matches = re.finditer(reg, s)
            if matches:
                k = 1
                starts = []
                strs = []
                for m in matches:
                    starts.append(m.start())
                    strs.append(m.group())
                c_t = len(starts)
                for i in range(c_t):
                    x = starts[i]
                    y = starts[i] + len(strs[i])
                    P[x].append(MatchPos(reg, k, True))
                    P[x].append(MatchPos(reg, k - c_t - 1, True))
                    P[y].append(MatchPos(reg, k, False))
                    P[y].append(MatchPos(reg, k - c_t - 1, False))
                    k += 1
        for k in range(1, len(s) + 1):
            P[k-1].append(ConstPos(k))
            P[k-1].append(ConstPos(k - len(s) - 1))

        # Ranking the pos function
        for f in range(len(s) + 1):
            P[f] = sorted(P[f], cmp=compare_pos_function)
            P[f] = P[f][0:min(len(P[f]), 2)]

        '''for i in P:
            for j in i:
                print j.to_string()'''

        for c in t:
            self.vertices.append(Vertice(c))
        self.edges = [[] for i in range(len(self.vertices))]

        for i in range(len(t)):
            for j in range(i + 1, len(t)+1):
                edge = Edge(i, j, [])
                # add ConstStr
                if j - i + 1 < self.MAX_CONST_LENGTH:
                    edge.add_label(ConstStr(t[i:j]))
                # add prefix and suffix
                for term in util.regexes_2:
                    starts = []
                    strs = []
                    matches = re.finditer(term, s)
                    for m in matches:
                        starts.append(m.start())
                        strs.append(m.group())
                    c = len(starts)
                    for k in range(1, len(starts) + 1):
                        if j - i < len(strs[k-1]):
                            if t[i:j] == strs[k-1][:j-i] and (j == len(t)-1 or t[i:j+1] != strs[k-1][:j+1-i]):
                                edge.add_label(Prefix(term, k))
                                edge.add_label(Prefix(term, k - c - 1))
                            if t[i:j] == strs[k-1][len(strs[k-1])-j+i:] and (i == 0 or t[i-1:j] != strs[k-1][len(strs[k-1])-j+i-1:]):
                                edge.add_label(Suffix(term, k))
                                edge.add_label(Suffix(term, k - c - 1))
                # add SubStr
                for start in kmp.kmpAllMatches(t[i:j], s):
                    x = start
                    y = start + len(t[i:j])
                    if s[x:y] == t[i:j]:
                        for f in P[x]:
                            for g in P[y]:
                                edge.add_label(SubStr(f, g))
                self.add_edge(edge, i)
        # print s + "--->" + t + '[Completed]'
