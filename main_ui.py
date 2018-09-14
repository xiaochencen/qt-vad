import sys
from PyQt5 import QtCore, QtGui
import PyQt5.QtWidgets as QWidgets
from PyQt5.QtWidgets import QApplication
import matplotlib
import matplotlib.pyplot as plt
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure
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
        self.file_dict = {}
        self.middle_data = {}
        self.feature_data = {}
        self.current_file = None
        self.current_data = {"x": None, "y": None}
        # menu初始化
        self.menu_bar = self.menuBar()
        self.menu1_file = QWidgets.QMenu("文件")
        self.menu2_data = QWidgets.QMenu("数据")
        self.data_action = QWidgets.QAction("特征数据", self.menu2_data)
        self.open_file = QWidgets.QAction("打开文件", self.menu1_file)
        self.data_action.setShortcut("Ctrl+D")
        self.open_file.setShortcut("Ctrl+O")
        self.data_action.triggered.connect(self.show_feature_list)
        self.open_file.triggered.connect(self.get_file)
        self.menu2_data.addAction(self.data_action)
        self.menu1_file.addAction(self.open_file)

        self.menu_bar.addMenu(self.menu1_file)
        self.menu_bar.addMenu(self.menu2_data)
        self.middle_data_dock = QWidgets.QDockWidget("MiddleData", self)
        self.middle_data_listwidget = QWidgets.QListWidget()
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
        self.main_window.clear_button.clicked.connect(self.clear_plot)

    def get_file(self):
        file_dialog = QWidgets.QFileDialog()
        f, _ = file_dialog.getOpenFileNames(self, "OpenFiles", "\\", "*.wav")
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
        current_item = self.main_window.list_file.currentItem()
        self.current_file = self.file_dict[current_item.text()]
        self.status.showMessage("当前文件:"+self.current_file.text(), 5000)

    def get_voice_data(self):
        if self.current_file is None:
            current_item = self.main_window.list_file.currentItem()
            self.current_file = self.file_dict[current_item.text()]
            self.status.showMessage("当前文件:" + self.current_file.text(), 5000)
        self.current_data = self.current_file.data

    def get_current_data(self):
        data_name = self.middle_data_listwidget.currentItem().text()
        self.current_data = self.middle_data[data_name]

    def __plot(self):
        subplot = self.main_window.subplot_lineEdit.text()
        hold_on = self.main_window.is_holdOn.isChecked()
        y = self.current_data['y']
        plt.cla()
        if y is None:
            QWidgets.QMessageBox.critical(self, "坐标错误", "纵坐标错误")
            return 0
        elif len(subplot) != 3:
            QWidgets.QMessageBox.warning(self, '参数错误', 'subplot参数错误')
            return 0
        ax = self.main_window.figure.add_subplot(subplot)
        # ax.bar
        if hold_on is False:
            plt.cla()
        ax.plot(y)
        self.main_window.canvas.draw()

    def clear_plot(self):
        self.main_window.figure.clear()
        self.main_window.canvas.draw()

    def init_dock(self):
        self.middle_data_dock.setAllowedAreas(QtCore.Qt.RightDockWidgetArea)
        self.middle_data_dock.setFeatures(QWidgets.QDockWidget.AllDockWidgetFeatures)

    def show_feature_list(self):
        state = self.middle_data_dock.isVisible()
        if state:
            self.middle_data_dock.close()
        else:
            self.middle_data_dock.show()


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
        self.push_button = QWidgets.QPushButton("暂停")
        self.stop_button = QWidgets.QPushButton("停止")

        self.right_top_layout = QWidgets.QVBoxLayout()
        self.features_combobox = QWidgets.QComboBox()
        self.classfication_combobox = QWidgets.QComboBox()
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
        play_layout.addWidget(self.push_button)
        play_layout.addWidget(self.stop_button)

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

