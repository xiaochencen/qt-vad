import numpy as np
import scipy.io.wavfile as wave
import librosa
import copy
from scipy import signal
import os
import logging
import time
from sklearn import preprocessing


# I should have defined a  voice data class to handle the data, but i didn't
# think about that at the beginning
from sympy.physics.units import frequency

log_filename = "logging.log"
logging.basicConfig(level=logging.DEBUG,
                    format='[%(asctime)s] %(levelname)s [%(funcName)s: %(filename)s, %(lineno)d] %(message)s',
                    datefmt='%Y-%m-%d %H:%M:%S',
                    filemode='a')


def read_voice(file_name):
    """
    read voice file
    :param file_name: full path of file
    :return: tuple(y,sr) data and sample rate
    """
    try:
        # resample use kaiser_best by default
        # to use scipy.signal.resample set res_type = "scipy"
        sr, y = wave.read(file_name)
        y = y - np.mean(y)
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


def sample2time(data, sr):
    """
    sample data to time
    :param data: the data we have read
    :param sr: voice file sample rate
    :return: time of sample
    """
    sample_time = np.zeros(len(data))
    for i in range(len(data)):
        sample_time[i] = i / sr
    return sample_time


def frame2time(enframed, sr):
    """
    Assign time to each frame
    :param enframed: enframed voice data
    :param sr: voice file sample rate
    :return: time of each frame
    """
    win_len = enframed["frame_w"]
    frame_len = enframed["frame_num"]
    frame_to_time = (np.arange(0, frame_len, 1, 'int') * enframed["frame_s"] + win_len // 2) / sr
    return frame_to_time


def calculate_accuracy(standard, test):
    """
    calculate accuracy of speech active
    :param standard: no noise speech detective result
    :param test: noise speech detective result
    :return: score of accuracy
    """
    if len(standard) != len(test):
        raise ValueError
        return 0
    marks = np.array(standard) == np.array(test)
    score = marks.sum()/len(test)
    return score


def add_noise(speech, noise, snr, output=True):
    """
    Add noise as signal-noise-rate with snr
    :param speech: path of speech
    :param noise: path of noise
    :param output: write data to file
    :param snr: snr(db) of you want to add (you should know when snr = 0 that S/N = 1)
    """
    speech_wave, sr_speech = librosa.load(speech, sr=16000)
    speech_name = speech.split('/')[-1].split('.')[0]
    noise_wave, sr_noise = librosa.load(noise, sr=16000)
    noise_name = noise.split('/')[-1].split('.')[0]
    if len(noise_wave) > len(speech_wave):
        noise_wave = noise_wave[0:len(speech_wave)]
    noise_wave = noise_wave-np.mean(noise_wave)
    speech_power = sum(np.square(speech_wave))/len(speech_wave)
    noise_power_e = speech_power/(10**(snr/10))  # noise power
    # 由于噪声信号做了均值化处理，这里的标准差就相当于是能量的开方
    noise_e = np.sqrt(noise_power_e)/np.std(noise_wave)*noise_wave
    real_wave = speech_wave+noise_e
    new_wave_name = speech_name+"+"+noise_name+str(snr)+"db.wav"
    if output:
        if os.path.exists(new_wave_name):
            logging.warning("File %s already exists" % new_wave_name)
        else:
            wave.write(new_wave_name, 16000, real_wave)
    return real_wave


if __name__ == "__main__":
    add_noise('E:/PycharmPro/D4_754.wav', 'E:/PycharmPro/babble.wav', -5)
    pass