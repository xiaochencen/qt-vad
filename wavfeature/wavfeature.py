import numpy as np
import until
import librosa


class Feature(object):
    """chenwang:2018.8.28.
        provide some features of wavefile
    """

    def __init__(self, file_name):
        self.filename = file_name
        self.data = {}
        self.data["y"], self.sr = until.read_voice(file_name)
        self.framed_data = until.en_frame(data=self.data["y"], sr=self.sr)
        self.data["x"] = until.sample2time(self.data["y"], self.sr)
        self.frame_time = until.frame2time(self.framed_data, self.sr)

    def st_en(self):
        # short time energy use kaiser window
        st_energy = dict()
        st_energy["y"] = np.zeros(self.framed_data["frame_num"])
        en_framed = self.framed_data["data"] * np.kaiser(self.framed_data["frame_w"], 14)
        for frame in range(self.framed_data["frame_num"]):
            st_energy["y"][frame] = np.mean(np.square(en_framed[frame]))
        st_energy["x"] = self.frame_time
        return st_energy

    def st_zcr(self):
        # short time zero cross rate
        short_time_zcr = dict()
        short_time_zcr["y"] = np.zeros(self.framed_data["frame_num"])
        en_framed, frame_num = self.framed_data["data"], self.framed_data["frame_num"]
        for frame in range(frame_num):
            count = 0
            for i in range(en_framed.shape[1] - 1):
                if en_framed[frame, i] * en_framed[frame, i + 1] < 0:
                    count += 1
            short_time_zcr["y"][frame] = count
        short_time_zcr["x"] = self.frame_time
        return short_time_zcr

    def pre_emphasis(self, win):
        """
        pre-emphasis the voice to raise the high frequency
        :param win:
        :return: pre-emphasised voice data
        """

        pass


if __name__ == "__main__":
    wave = Feature("E:\PycharmPro\chenwang.wav")
    en = wave.st_en()
    zcr = wave.st_zcr()
    input("")


