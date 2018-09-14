import numpy as np
import scipy.io.wavfile as waveio
import librosa
from scipy import signal
import copy
import time
import timeit


def read_voice(file_name, mono=True):
    try:
        y, sr = librosa.load(file_name, mono=mono)
    except FileNotFoundError:
        return None
    return y, sr


def en_frame(*, data, sr: "frequency", win_len: float = 0.03, win_step: float = 0.015
             , max_norm=True):
    """
        en_frame the wave data
        input:
            win_len: frame length
            win_step: overlap between frames
            max_normalization: remove dc component and normalized data default True
        return:
            framed_data: (frame_num,win_len) shape of framed_data
    """
    frame = {}
    if max_norm:
        data = copy.deepcopy(data)
        data = data / np.max(np.abs(signal.detrend(data)))
    data_len = data.shape[0]
    frame["frame_w"] = int(win_len * sr)
    frame["frame_s"] = int(win_step * sr)
    frame["frame_num"] = (data_len - frame["frame_w"]) // frame["frame_s"]
    en_framed_index = np.tile(np.arange(0, frame["frame_w"]), (frame["frame_num"], 1)) + \
                      np.tile(np.arange(0, frame["frame_num"] * frame["frame_s"], frame["frame_s"]), (frame["frame_w"], 1)).T
    en_framed_index = np.array(en_framed_index, dtype=np.int32)
    frame["data"] = data[en_framed_index]
    return frame


def frame2time(enframed, sr):

    win_len = enframed["frame_w"]
    frame_len = enframed["frame_num"]
    frame_to_time = (np.arange(0, frame_len, 1, 'int') * enframed["frame_s"] + win_len // 2) / sr
    return frame_to_time


class Feature(object):
    """chenwang:2018.8.28.
        provide some features of wavefile
    """

    def __init__(self, file_name):
        self.filename = file_name
        self.data = {}
        self.data["y"], self.sr = read_voice(file_name)
        self.framed_data = en_frame(data=self.data["y"], sr=self.sr)
        self.data["x"] = frame2time(self.framed_data, self.sr)

    def st_en(self):
        # short time energy use kaiser window
        short_time_en = []
        en_framed = self.framed_data["data"] * np.kaiser(self.framed_data["frame_w"], 14)
        for frame in range(self.framed_data["frame_num"]):
            short_time_en.append(np.mean(np.square(en_framed[frame])))
        return short_time_en

    def st_zcr(self):
        # short time zero cross rate
        short_time_zcr = []
        en_framed, frame_num = self.framed_data["data"], self.framed_data["frame_num"]
        for frame in range(frame_num):
            count = 0
            for i in range(en_framed.shape[1] - 1):
                if en_framed[frame, i] * en_framed[frame, i + 1] < 0:
                    count += 1
            short_time_zcr.append(count)
        return short_time_zcr


if __name__ == "__main__":
    wave = Feature("E:\VsProject\speech\speech\D4_754.wav")
    en = wave.st_en()
    zcr = wave.st_zcr()
    input("")


