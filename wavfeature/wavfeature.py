import numpy as np
import scipy.io.wavfile as waveio
from scipy import signal
import copy
import time
import timeit


def read_voice(file_name, channel=1):
    try:
        sr, data = waveio.read(file_name)
        channels = 1 if len(data.shape) == 1 else data.shape[1]
        if channel == 1:
            return sr, data
        elif channel > 1 & channels >= channel:
            data = data[0:channel, :]
            return sr, data
    except FileNotFoundError:
            pass


def en_frame(*, data, sr: "frequency", win_len: float = 0.03, win_step: float = 0.015
             , max_norm=True):
    """
        en_frame the wave data
        input:
            win_len: frame length
            win_step: overlap between frames
            max_normalization: remove dc component and normalized data default True
        return:
            en_framed: (frame_num,win_len) shape of en_framed
            frame_num: number of frame
    """
    if max_norm:
        data = copy.deepcopy(data)
        data = data / np.max(np.abs(signal.detrend(data)))
    data_len = data.shape[0]
    frame_w = int(win_len * sr)
    frame_s = int(win_step * sr)
    frame_num = (data_len - frame_w) // frame_s
    en_framed_index = np.tile(np.arange(0, frame_w), (frame_num, 1)) + \
                      np.tile(np.arange(0, frame_num * frame_s, frame_s), (frame_w, 1)).T
    en_framed_index = np.array(en_framed_index, dtype=np.int32)
    en_framed = data[en_framed_index]
    return en_framed, frame_num


def frame2time(fs, inc, nf, nw):
    """
    :param fs: 信号采样频率
    :param inc:  分帧帧移
    :param nf: 帧数
    :param nw: 窗长
    :return: 每一帧的时间
    """
    frame_time = (np.arange(0, nf, 1, 'int') * inc + nw / 2) / fs
    return frame_time


class Feature(object):
    """chenwang:2018.8.28.
        provide some features of wavefile
    """

    def __init__(self, file_name):
        self.filename = file_name
        self.sr, self.data = read_voice(file_name)
        self.en_framed, self.frame_num = en_frame(data=self.data, sr=self.sr)

    def st_en(self):
        # short time energy use kaiser window
        short_time_en = []
        # en_framed, frame_num = _en_frame(data=self.data, sr=self.sr)
        en_framed = self.en_framed * np.kaiser(self.en_framed.shape[1], 14)
        for frame in range(self.frame_num):
            short_time_en.append(np.mean(np.square(en_framed[frame])))
        return short_time_en

    def st_zcr(self):
        # short time zero cross rate
        short_time_zcr = []
        en_framed, frame_num = en_frame(data=self.data, sr=self.sr)
        for frame in range(frame_num):
            count = 0
            for i in range(en_framed.shape[1] - 1):
                if en_framed[frame, i] * en_framed[frame, i + 1] < 0:
                    count += 1
            short_time_zcr.append(count)
        return short_time_zcr

    def st_corr(self):
        # short time correlate
        st_corr = []
        for frame in range(self.frame_num):
            corr = signal.correlate(self.en_framed[frame], self.en_framed[frame], mode="same")
            st_corr.append(corr)
        return st_corr



if __name__ == "__main__":
    wave = Feature("E:\VsProject\speech\speech\D4_754.wav")
    en = wave.st_en()
    zcr = wave.st_zcr()
    st_cor = wave.st_corr()

    input("")


