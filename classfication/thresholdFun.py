import numpy as np


def threshold(class_feature, threshold_val1=1.2, threshold_val2=1.6):
    """
    get 20 frame of features as noise estimate
    for feature len is 1:
    :param feature:
    :param threshold_val1: percent of noise to estimate if  out of noise (smaller)
    :param threshold_val2: percent of noise to ensure get in voice(bigger)
    :return: array with dimension as frames
    for feature len is 2:
    st_en and st_corr as features
    """
    feature = dict()
    x = None
    for fea in class_feature.keys():
        feature[fea] = class_feature[fea]["y"]
        x = class_feature[fea]["x"]
    if len(feature) == 1:
        frame_mark = dict()
        feature_signal = list(feature.values())[0]
        try:
            noise_estimate = sum(feature_signal[0:20])/20
        except IndexError:
            pass
        threshold1 = noise_estimate*threshold_val1
        threshold2 = noise_estimate*threshold_val2
        statue = 0
        count = 0
        max_count = 10
        frame_mark['y'] = np.zeros(len(feature_signal))
        frame_mark['x'] = x
        begin, end = 0, 0
        for frame, val in enumerate(feature_signal):
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
                frame_mark['y'][begin:end] = 1
                statue = 0
                end = 0
                begin = 0

        return frame_mark
    elif len(feature) == 2:
        en = list(feature.values())[0]
        corr = list(feature.values())[1]
        try:
            average_en = sum(en[0:20])/20
            average_corr = sum(corr[0:20])/20
        except IndexError:
            pass
        threshold1 = average_en*threshold_val1
        threshold2 = average_en*threshold_val2
        statue = 0
        count = 0
        max_count = 10
        frame_mark = dict()
        frame_mark['y'] = np.zeros(len(en))
        frame_mark['x'] = x
        begin, end = 0, 0
        for frame, val in enumerate(en):
            cor = corr[frame]
            if statue == 0:
                if val < threshold1:
                    count = 0
                    continue
                elif val > threshold1 or cor > average_corr:
                    count += 1
                    if count > max_count and val > threshold2:
                        begin = frame - count
                        statue = 1
                        count = 0

            if statue == 1:
                if val > threshold2 or cor > average_corr:
                    count = 0
                    continue
                elif val < threshold2:
                    count += 1
                    if count > max_count:
                        end = frame - count
                        statue = 2

            if statue == 2:
                frame_mark['y'][begin:end] = 1
                statue = 0
                end = 0
                begin = 0
        return frame_mark
