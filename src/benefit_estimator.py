from scipy.stats import wasserstein_distance as EMD # known as the earth mover’s distance
from active_learning import ActiveLearning
import numpy as np
import os

class BenefitEstimator(object):
    def __init__(self, current_vis, cleaned_vis, window):
        self.current_vis = current_vis
        self.cleaned_vis = cleaned_vis
        self.group_window = window # None for without window

    def window_benefit(self):
        if self.group_window != None:
            return wrongVisDetector(self.current_vis, self.cleaned_vis)

    def imputing_benefit(self):
        return wrongVisDetector(self.current_vis, self.cleaned_vis)

    '''
    local-global benefit framework -- still in development
    '''
    def local_benefit(self):
        pass

    def global_benefit(self):
        pass

    def rank_local_benefit(self):
        pass

    def rank_global_benefit(self):
        pass


# current_vis = [100, 2, 300, 42, 230] # y-axis for this tuple
def wrongVisDetector(current_vis, cleaned_vis):
    '''
    :param current_vis: current visualization
    :param cleaned_vis: the possible cleaned visualization
    :return: True for wrong visualization / False for possible cleaned visualization
    Note that: we can normalize the current_vis & cleaned_vis to [0,1]
                the threshold is setting from experience
    '''
    pre_define_threshold = 0.006 # an empirical value

    if EMD(current_vis, cleaned_vis) > pre_define_threshold:
        return True
    else:
        return False

if __name__ == '__main__':
    vis_path = os.path.abspath(
        os.path.join(os.path.dirname(os.path.abspath(__file__)), '../dataset/DBConf/expr_tmp/vis'))
    current_vis = np.loadtxt(vis_path + "/current_vis.txt")
    cleaned_vis = np.loadtxt(vis_path + "/cleaned_vis.txt")
    # normalize the data
    nor_current_vis = current_vis / np.sum(current_vis)
    nor_cleaned_vis = cleaned_vis / np.sum(cleaned_vis)
    print(len(nor_cleaned_vis))
    print(len(nor_current_vis))
    '''fill the empty value.'''
    if len(nor_cleaned_vis) > len(nor_current_vis):
        nor_current_vis = np.append(np.zeros(len(nor_cleaned_vis) - len(nor_current_vis)), nor_current_vis)
    else:
        print(type(nor_current_vis))
        nor_cleaned_vis = np.append(np.zeros(len(nor_current_vis) - len(nor_cleaned_vis)), nor_cleaned_vis)

    # for test the EMD
    print(EMD(np.array(nor_current_vis), np.array(nor_cleaned_vis)))


    # Test for EMD
    # dirty = [181374, 132937, 76897, 75532, 69253, 58021, 53129, 47906, 47589, 37597]
    # q_5 = [193994,183594, 155851,111884,70712,40215,36857,45458,29282,26124]
    # q_10 = [371899,258783,227188,150085,85671,76387,71720,45073,32455,18929]
    # q_15 = [353946,300745,190920,177925,126299,102393,51458,42877,38241,29265]
    # g_t = [333946,290745,130920,117925,96299,70204,45458,43877,36241,27265]
    #
    # dirty = dirty / np.sum(dirty)
    # q_5 = q_5 / np.sum(q_5)
    # q_10 = q_10 / np.sum(q_10)
    # q_15 = q_15 / np.sum(q_15)
    # g_t = g_t / np.sum(g_t)
    #
    # print(EMD(dirty,g_t))
    # print(EMD(q_5, g_t))
    # print(EMD(q_10, g_t))
    # print(EMD(q_15, g_t))
    #
    # print()
    #
    # print(EMD(dirty, q_5))
    # print(EMD(q_5, q_10))
    # print(EMD(q_10, q_15))
    # print(EMD(q_15, g_t))


