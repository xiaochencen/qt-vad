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
        self.current_file = None
        # menu初始化
        self.menu_bar = self.menuBar()
        self.menu1_file = QWidgets.QMenu("文件")
        self.open_file = QWidgets.QAction("打开文件", self.menu1_file)
        self.open_file.setShortcut("Ctrl+O")
        self.open_file.triggered.connect(self.get_file)
        self.menu1_file.addAction(self.open_file)

        self.menu2_draw = QWidgets.QMenu("绘图")
        self.menu2_plot = QWidgets.QAction("绘制", self.menu2_draw)
        # self.menu2_plot.setIcon()
        self.menu2_draw.addAction(self.menu2_plot)
        self.menu_bar.addMenu(self.menu1_file)
        self.menu_bar.addMenu(self.menu2_draw)
        #self.menu2_plot.triggered.connect(self.plot_)
        # 主窗口载入
        self.main_window = MyWindow()
        self.main_window.list_file.doubleClicked.connect(self.get_item)
        self.setCentralWidget(self.main_window)

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
        self.current_file = self.main_window.list_file.currentItem()
        self.status.showMessage("当前文件:"+self.current_file.text(), 5000)


class MyWindow(QWidgets.QWidget):

    def __init__(self):
        super().__init__()
        self.main_window_layout = QWidgets.QVBoxLayout()
        # topLayout 布局
        self.top_layout = QWidgets.QHBoxLayout()
        self.left_top_layout = QWidgets.QVBoxLayout()
        self.right_top_layout = QWidgets.QVBoxLayout()
        figure = plt.figure()
        self.canvas = FigureCanvas(figure)
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
        plot_buttons = QWidgets.QHBoxLayout()
        plot_button = QWidgets.QPushButton("绘图")
        # todo plot
        clear_button = QWidgets.QPushButton("清除")
        # todo clear
        plot_buttons.addWidget(plot_button)
        plot_buttons.addStretch()
        plot_buttons.addWidget(clear_button)
        self.left_top_layout.addLayout(plot_buttons)
        self.left_top_layout.addWidget(self.list_file)
        test_button = QWidgets.QPushButton("Test")
        self.right_top_layout.addWidget(test_button)
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

