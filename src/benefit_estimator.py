from scipy.stats import wasserstein_distance # known as the earth mover’s distance
from active_learning import ActiveLearning

class BenefitEstimator(object):
    def __init__(self, cur_vis_y, cleaned_vis_y, window):
        self.cur_vis_y = cur_vis_y
        self.cleaned_vis_y = cleaned_vis_y
        self.group_window = window # None for without window

    def window_benefit(self):
        if self.group_window != None:
            return wrongVisDetector(self.cur_vis_y, self.cleaned_vis_y)

    def imputing_benefit(self):
        return wrongVisDetector(self.cur_vis_y, self.cleaned_vis_y)

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


# cur_vis = [100, 2, 300, 42, 230] # y-axis for this tuple
def wrongVisDetector(cur_vis, cleaned_vis):
    '''
    :param cur_vis: current visualization
    :param cleaned_vis: the possible cleaned visualization
    :return: True for wrong visualization / False for possible cleaned visualization
    Note that: we can normalize the cur_vis & cleaned_vis to [0,1]
                the threshold is setting from experience
    '''
    pre_define_threshold = 500
    if wasserstein_distance(cur_vis, cleaned_vis) > pre_define_threshold:
        return True
    else:
        return False