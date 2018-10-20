import sys
from PyQt5 import QtCore, QtGui
import PyQt5.QtWidgets as QWidgets
import copy
from PyQt5.QtWidgets import QApplication
import matplotlib
import matplotlib.pyplot as plt
import PyQt5.QtMultimedia as Qmedia
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from classfication import thresholdFun as thd
from wavfeature import wavfeature as wf
import until
matplotlib.use("Qt5Agg")


class MyMainWindow(QWidgets.QMainWindow):

    def __init__(self):
        super().__init__()
        # 主窗口初始化
        self.setWindowTitle("Qt test")
        self.setWindowIcon(QtGui.QIcon("source/voicesearch_128px_526004_easyicon.net.ico"))
        # 主窗口部件初始化
        # 状态栏初始化
        self.status = self.statusBar()
        self.setStatusBar(self.status)
        self.file_dict = {}  # 语音特征对象Feature
        self.middle_data = {}  # 存储中间计算出来的特征以及结果
        self.current_file = None  # 当前选中语音文件的文件名
        self.class_feature_data = dict()  # 分类方法使用的语音特征字典
        self.current_data = None  # 当前选中的绘图使用的数据，通常是一个字典
        # menu初始化
        self.menu_bar = self.menuBar()
        self.menu1_file = QWidgets.QMenu("文件")
        self.menu2_data = QWidgets.QMenu("数据")
        self.menu3_tools = QWidgets.QMenu("工具")
        self.data_action = QWidgets.QAction("特征数据", self.menu2_data)
        self.open_file = QWidgets.QAction("打开文件", self.menu1_file)
        self.add_noise = QWidgets.QAction("加噪", self.menu3_tools)
        self.data_action.setShortcut("Ctrl+D")
        self.open_file.setShortcut("Ctrl+O")
        self.data_action.triggered.connect(self.show_feature_list)
        self.open_file.triggered.connect(self.get_file)
        self.add_noise.triggered.connect(self.add_noises)
        self.menu2_data.addAction(self.data_action)
        self.menu1_file.addAction(self.open_file)
        self.menu3_tools.addAction(self.add_noise)

        self.menu_bar.addMenu(self.menu1_file)
        self.menu_bar.addMenu(self.menu2_data)
        self.menu_bar.addMenu(self.menu3_tools)
        self.middle_data_dock = QWidgets.QDockWidget("MiddleData", self)
        self.middle_data_listwidget = QWidgets.QListWidget()
        self.right_click_menu = QWidgets.QMenu(self.middle_data_listwidget)
        self.middle_data_listwidget.itemDoubleClicked.connect(self.get_current_data)
        self.clear_mid_data = QWidgets.QPushButton
        self.middle_data_dock.setWidget(self.middle_data_listwidget)
        self.addDockWidget(QtCore.Qt.RightDockWidgetArea, self.middle_data_dock)
        self.init_dock()
        # 主窗口载入
        self.main_window = MyWindow()
        self.main_window.list_file.clicked.connect(self.get_item)
        self.main_window.list_file.doubleClicked.connect(self.get_voice_data)
        self.setCentralWidget(self.main_window)
        # main_window逻辑
        self.main_window.plot_button.clicked.connect(self.__plot)
        self.main_window.features_combobox.activated.connect(self.choose_features_fun)
        self.main_window.classfication_combobox.activated.connect(self.choose_classfun)
        self.main_window.clear_button.clicked.connect(self.clear_plot)
        # player model
        self.player = Qmedia.QMediaPlayer()
        self.recoder = Qmedia.QAudioRecorder()
        self.current_playlist = Qmedia.QMediaPlaylist()
        self.init_player_recoder()
        self.status_player = -1  # 1-播放 2-暂停 0-停止
        self.status_recoder = -1  # 1-录音 2-暂停 0-停止
        self.main_window.play_button.clicked.connect(self.play_voice)
        self.main_window.stop_button.clicked.connect(self.stop_play)
        self.main_window.pause_button.clicked.connect(self.pause_play)
        self.main_window.recoder_button.clicked.connect(self.recoder_voice)

    def add_noises(self):
        voice_path, ok_press = QWidgets.QFileDialog.getOpenFileName(self, "ChooseVoice", '.\\', '*.wav')
        if ok_press:
            voice = voice_path
        else:
            return 0
        noise_path, ok_press = QWidgets.QFileDialog.getOpenFileName(self, "Choose", '.\\', '*.wav')
        if ok_press:
            noise = noise_path
        else:
            return 0
        snr_value, ok_press = QWidgets.QInputDialog.getInt(self, "Input SNR", "SNR:", 0, -10, 20, 1)
        if ok_press:
            snr = snr_value
        else:
            return 0
        until.add_noise(voice, noise, snr)

    def closeEvent(self, a0: QtGui.QCloseEvent):
        reply = QWidgets.QMessageBox.question(self, 'Message', 'Pres Yes to Close.',
                                              QWidgets.QMessageBox.Yes | QWidgets.QMessageBox.No,
                                              QWidgets.QMessageBox.Yes)

        if reply == QWidgets.QMessageBox.Yes:
            app.quit()
        else:
            try:
                a0.ignore()
            except AttributeError:
                pass

    def init_player_recoder(self):
        self.player.setVolume(60)
        self.player.stateChanged.connect(self.my_state_change)
        self.player.mediaStatusChanged.connect(self.my_statues_change)
        self.recoder.audioSettings().setCodec('audio/x-wav')
        self.recoder.audioSettings().setChannelCount(1)
        self.recoder.defaultAudioInput()
        self.current_playlist.setPlaybackMode(Qmedia.QMediaPlaylist.CurrentItemOnce)

    def my_statues_change(self):
        # 当输出设备更换时得处理方式
        if self.player.mediaStatus() == Qmedia.QMediaPlayer.LoadedMedia and self.status_player == 1:
            self.player.play()

    def my_state_change(self):
        if self.player.state() == Qmedia.QMediaPlayer.StoppedState:
            self.player.stop()

    def get_file(self):
        file_dialog = QWidgets.QFileDialog()
        f, _ = file_dialog.getOpenFileNames(self, "OpenFiles", ".\\", "*.wav")
        for file in f:
            file_name = file.split('/')[-1]
            if file_name not in set(self.file_dict.keys()):
                self.file_dict[file_name] = wf.Feature(file)
                self.main_window.list_file.addItem(file_name)
            else:
                QWidgets.QMessageBox.information(self, "Warring", "文件"+file_name+"已读取",
                                                 QWidgets.QMessageBox.Yes | QWidgets.QMessageBox.No,
                                                 QWidgets.QMessageBox.Yes)

    def get_item(self):
        # set current_file ,please note that current_file is a item object
        self.current_file = self.main_window.list_file.currentItem().text()
        self.status.showMessage("当前文件:"+self.current_file, 5000)

    def get_voice_data(self):
        if self.current_file is None:
            self.current_file = self.main_window.list_file.currentItem().text()
            self.status.showMessage("当前文件:" + self.current_file, 5000)
        current_item = self.file_dict[self.current_file]
        self.current_data = current_item.data

    def get_current_data(self):
        data_name = self.middle_data_listwidget.currentItem().text()
        self.current_data = self.middle_data[data_name]

    def __plot(self):
        subplot = self.main_window.subplot_lineEdit.text()
        hold_on = self.main_window.is_holdOn.isChecked()
        y = self.current_data['y']
        if len(subplot) == 0:
            subplot = "111"
        if len(subplot) != 3:
            QWidgets.QMessageBox.warning(self, '参数错误', 'subplot参数错误')
            return 0
        ax = self.main_window.figure.add_subplot(subplot)
        #ax.set_xlim(min(self.current_data['x']), )
        if len(self.current_data) > 1:
            x = self.current_data['x']
            if hold_on is False:
                plt.cla()
                ax.plot(x, y)
            else:
                ax.plot(x, y)
        else:
            ax.plot(y)
        self.main_window.canvas.draw()

    def clear_plot(self):
        self.main_window.figure.clear()
        self.main_window.canvas.draw()

    def init_dock(self):
        self.middle_data_dock.setAllowedAreas(QtCore.Qt.RightDockWidgetArea)
        self.middle_data_dock.setFeatures(QWidgets.QDockWidget.AllDockWidgetFeatures)
        add_item_to_class = self.right_click_menu.addAction("添加特征")
        del_item_from_class = self.right_click_menu.addAction("删除特征")
        del_middle_data = self.right_click_menu.addAction("删除数据")
        add_item_to_class.triggered.connect(self.add_to_class_feature)
        del_item_from_class.triggered.connect(self.del_from_class_feature)
        del_middle_data.triggered.connect(self.del_current_middle_data)
        self.middle_data_listwidget.setContextMenuPolicy(QtCore.Qt.CustomContextMenu)
        self.middle_data_listwidget.customContextMenuRequested.connect(self.show_dock_context_menu)

    def show_dock_context_menu(self):
        self.right_click_menu.move(QtGui.QCursor.pos())
        self.right_click_menu.show()

    def add_to_class_feature(self):
        name = self.middle_data_listwidget.currentItem().text()
        self.class_feature_data[name] = copy.deepcopy(self.middle_data[name])
        text = self.main_window.threshold_lineedit.text() + name + "  "
        self.main_window.threshold_lineedit.setText(text)
        pass

    def del_from_class_feature(self):
        name = self.middle_data_listwidget.currentItem().text()
        try:
            self.class_feature_data.pop(name)
            text = self.main_window.threshold_lineedit.text().replace(name+"  ", "")
            self.main_window.threshold_lineedit.setText(text)
        except IndexError:
            pass
        pass

    def del_current_middle_data(self):
        name = self.middle_data_listwidget.currentItem().text()
        row = self.middle_data_listwidget.currentRow()
        try:
            self.middle_data.pop(name)
            self.middle_data_listwidget.takeItem(row)
        except IndexError:
            QWidgets.QMessageBox.warning(self, '删除错误', 'MiddleDate中没有该值')

    def show_feature_list(self):
        state = self.middle_data_dock.isVisible()
        if state:
            self.middle_data_dock.close()
        else:
            self.middle_data_dock.show()

    def choose_features_fun(self):
        # todo : 执行特征提取函数，将特征存入feature_data字典中
        # todo : 更新docklistitem，并显示docklist
        feature = self.main_window.features_combobox.currentText()
        if feature == "ST_energy":
            name = self.current_file+"stenergy"
            current_obj = self.file_dict[self.current_file]
            st_energy = current_obj.st_en()
            self.middle_data[name] = st_energy
            self.middle_data_listwidget.addItem(name)
            self.status.showMessage("短时能量提取", 2000)
            pass
        elif feature == "ST_ZeroCross":
            name = self.current_file + "stzcr"
            st_zcr = self.file_dict[self.current_file].st_zcr()
            self.middle_data[name] = st_zcr
            self.middle_data_listwidget.addItem(name)
            self.status.showMessage("短时过零率提取", 2000)
            pass
        pass

    def choose_classfun(self):
        # todo 根据选择的分类函数调用相应的方法
        # todo return
        if self.class_feature_data == {}:
            QWidgets.QMessageBox.information(self, "Warring", "没有选择分类特征",
                                             QWidgets.QMessageBox.Yes | QWidgets.QMessageBox.No,
                                             QWidgets.QMessageBox.Yes)
            return 0
        elif len(self.class_feature_data) > 2:
            QWidgets.QMessageBox.information(self, "Warring", "特征数不符合该方法",
                                             QWidgets.QMessageBox.Yes | QWidgets.QMessageBox.No,
                                             QWidgets.QMessageBox.Yes)
            return 0

        if self.main_window.classfication_combobox.currentText() == "Threshold":
            th1, _ = QWidgets.QInputDialog.getDouble(self.main_window, "输入TH1的值", "TH1", value=1.2)
            th2, _ = QWidgets.QInputDialog.getDouble(self.main_window, "输入TH2的值", "TH2", value=1.6)
            speech_mark = thd.threshold(self.class_feature_data, threshold_val1=th1, threshold_val2=th2)
            self.middle_data_listwidget.addItem("speech_mark_threshold")
            self.middle_data["speech_mark_threshold"] = speech_mark
        pass

    def play_voice(self):
        self.status_player = 1
        if self.player.state() == Qmedia.QMediaPlayer.StoppedState:
            if self.player.mediaStatus() == Qmedia.QMediaPlayer.NoMedia:
                try:
                    self.current_playlist.clear()
                    self.current_playlist.addMedia(Qmedia.QMediaContent(QtCore.QUrl.fromLocalFile(
                        self.file_dict[self.current_file].filename)))
                    self.player.setPlaylist(self.current_playlist)
                except:
                    QWidgets.QMessageBox.Warning(self, "No voice File Choose",
                                                 "Please Choose a Voice File\n(double click file item)")
                    return 0

            elif self.player.mediaStatus() == Qmedia.QMediaPlayer.LoadedMedia:
                self.player.play()
                self.statusBar().showMessage("音频文件"+self.current_file+"播放中...", 2000)
            elif self.player.mediaStatus() == Qmedia.QMediaPlayer.BufferedMedia:
                self.player.play()
                self.statusBar().showMessage("音频文件" + self.current_file + "播放中...", 2000)
        elif self.player.state() == Qmedia.QMediaPlayer.PlayingState:
            self.statusBar().showMessage("音频文件" + self.current_file + "播放中...", 2000)
        elif self.player.state() == Qmedia.QMediaPlayer.PausedState:
            self.player.play()
            self.statusBar().showMessage("音频文件" + self.current_file + "播放中...", 2000)

    def stop_play(self):
        self.status_player = 0
        if self.player.state() == Qmedia.QMediaPlayer.PlayingState:
            self.player.stop()
            self.statusBar().showMessage("播放停止", 2000)
        elif self.player.state() == Qmedia.QMediaPlayer.PausedState:
            self.player.stop()
            self.statusBar().showMessage("播放停止", 2000)
        elif self.player.state() == Qmedia.QMediaPlayer.StoppedState:
            self.statusBar().showMessage("播放停止", 2000)
            pass
        # ----------------------------------------------------------------
        if self.status_recoder == 1 or self.status_recoder == 2:
            save_url = QWidgets.QFileDialog.getSaveFileUrl(self, "Save file", ".\\recoder.wav", "Audio(*.wav)")
            if save_url[0] != QtCore.QUrl(''):
                self.recoder.setOutputLocation(save_url[0])
            self.status_recoder = 0
            if self.recoder.state() == Qmedia.QAudioRecorder.RecordingState:
                self.recoder.stop()
                self.statusBar().showMessage("录音停止，录音文件："+save_url[1]+"已保存", 2000)
            elif self.recoder.state() == Qmedia.QAudioRecorder.PausedState:
                self.recoder.stop()
                self.statusBar().showMessage("录音停止，录音文件："+save_url[1]+"已保存", 2000)
            elif self.recoder.state() == Qmedia.QAudioRecorder.StoppedState:
                pass

    def pause_play(self):
        self.status_player = 2
        if self.player.state() == Qmedia.QMediaPlayer.PlayingState:
            self.player.pause()
            self.statusBar().showMessage("播放暂停", 2000)
        # ------------------------------------------------------------------
        if self.recoder.state() == Qmedia.QAudioRecorder.RecordingState:
            self.status_recoder = 2
            self.recoder.pause()
            self.statusBar().showMessage("录音暂停！", 2000)

    def recoder_voice(self):
        self.status_recoder = 1
        if self.recoder.state() == Qmedia.QAudioRecorder.StoppedState:
            self.recoder.record()
            self.statusBar().showMessage("录音中...", 2000)
        elif self.recoder.state() == Qmedia.QAudioRecorder.PausedState:
            self.recoder.record()
            self.statusBar().showMessage("恢复录音", 2000)
        elif self.recoder.state() == Qmedia.QAudioRecorder.RecordingState:
            self.statusBar().showMessage("录音中...", 2000)
            pass


class MyWindow(QWidgets.QWidget):

    def __init__(self):
        super().__init__()
        self.main_window_layout = QWidgets.QVBoxLayout()
        # topLayout 布局
        self.top_layout = QWidgets.QHBoxLayout()

        self.left_top_layout = QWidgets.QVBoxLayout()
        self.plot_button = QWidgets.QPushButton("绘图")
        self.clear_button = QWidgets.QPushButton("清除")
        self.data_lineEdit = QWidgets.QLineEdit()
        self.subplot_lineEdit = QWidgets.QLineEdit()
        self.is_holdOn = QWidgets.QCheckBox()
        self.play_button = QWidgets.QPushButton("播放")
        self.pause_button = QWidgets.QPushButton("暂停")
        self.stop_button = QWidgets.QPushButton("停止")
        self.recoder_button = QWidgets.QPushButton("录制")

        self.right_top_layout = QWidgets.QVBoxLayout()
        self.features_combobox = QWidgets.QComboBox()
        self.classfication_combobox = QWidgets.QComboBox()
        self.threshold_lineedit = QWidgets.QLineEdit()
        self.figure = plt.figure()
        self.canvas = FigureCanvas(self.figure)
        self.list_file = QWidgets.QListWidget()
        self.init_top_layout()

        # bottom_layout 布局
        self.bottom_layout = QWidgets.QHBoxLayout()
        self.init_bottom_layout()

        # 主窗口布局
        self.main_window_layout.addLayout(self.top_layout, stretch=2)
        self.main_window_layout.addLayout(self.bottom_layout, stretch=1)
        self.setLayout(self.main_window_layout)

    def init_top_layout(self):
        # left_top_layout
        plot_buttons = QWidgets.QHBoxLayout()
        plot_buttons.addWidget(self.plot_button)
        plot_buttons.addWidget(self.clear_button)

        plot_choice_layout = QWidgets.QFormLayout()
        self.subplot_lineEdit.setPlaceholderText("整形")
        subplot_validator = QtGui.QIntValidator(self)
        subplot_validator.setRange(111, 999)
        self.subplot_lineEdit.setValidator(subplot_validator)
        plot_choice_layout.addRow(QWidgets.QLabel("数据:"), self.data_lineEdit)
        plot_choice_layout.addRow(QWidgets.QLabel("SubPlot:"), self.subplot_lineEdit)
        plot_choice_layout.addRow(QWidgets.QLabel("Hold"), self.is_holdOn)

        play_layout = QWidgets.QHBoxLayout()
        play_layout.addWidget(self.play_button)
        play_layout.addWidget(self.pause_button)
        play_layout.addWidget(self.stop_button)
        play_layout.addWidget(self.recoder_button)

        self.left_top_layout.addLayout(plot_buttons)
        self.left_top_layout.addLayout(plot_choice_layout)
        self.left_top_layout.addWidget(self.list_file)
        self.left_top_layout.addLayout(play_layout)
        # right_top_layout
        test_button = QWidgets.QPushButton("Test")
        features_layout = QWidgets.QFormLayout()
        self.features_combobox.addItem("ST_energy")
        self.features_combobox.addItem("ST_ZeroCross")
        features_layout.addRow(QWidgets.QLabel("Features:"), self.features_combobox)
        classification_layout = QWidgets.QFormLayout()
        self.classfication_combobox.addItem("Threshold")
        classification_layout.addRow(QWidgets.QLabel("ClassMethod:"), self.classfication_combobox)
        self.right_top_layout.addWidget(QWidgets.QLabel("分类使用的特征⬇"))
        self.right_top_layout.addWidget(self.threshold_lineedit)

        self.right_top_layout.addLayout(features_layout)
        self.right_top_layout.addLayout(classification_layout)
        self.right_top_layout.addWidget(test_button)
        self.right_top_layout.addStretch()

        self.top_layout.addLayout(self.left_top_layout, stretch=1)
        self.top_layout.addStretch()
        self.top_layout.addWidget(self.canvas, stretch=3)
        self.top_layout.addStretch()
        self.top_layout.addLayout(self.right_top_layout, stretch=1)

    def init_bottom_layout(self):
        button = QWidgets.QPushButton("Test")
        self.bottom_layout.addWidget(button)


if __name__ == "__main__":
    app = QApplication(sys.argv)
    form = MyMainWindow()
    form.show()
    sys.exit(app.exec_())

