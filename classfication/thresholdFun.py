import numpy as np


def threshold(feature, threshold_val1, threshold_val2):
    """
    get 20 frame of features as noise estimate
    :param feature:
    :param threshold_val1: percent of noise to estimate if  out of noise (smaller)
    :param threshold_val2: percent of noise to ensure get in voice(bigger)
    :return: array with dimension as frames
    """
    try:
        noise_estimate = sum(feature[0:20])/20
    except IndexError:
        pass
    threshold1 = noise_estimate*threshold_val1
    threshold2 = noise_estimate*threshold_val2
    statue = 0
    count = 0
    max_count = 10
    frame_mark = np.zeros(len(feature))
    begin, end = 0, 0
    for frame, val in enumerate(feature):
        if statue == 0:
            if val < threshold1:
                count = 0
                continue
            elif val > threshold1:
                count += 1
                if count > max_count and val > threshold2:
                    begin = frame - count
                    statue = 1
                    count = 0

        if statue == 1:
            if val > threshold2:
                count = 0
                continue
            elif val < threshold2:
                count += 1
                if count > max_count:
                    end = frame - count
                    statue = 2

        if statue == 2:
            frame_mark[begin:end] = 1
            statue = 0
            end = 0
            begin = 0

    return frame_mark
