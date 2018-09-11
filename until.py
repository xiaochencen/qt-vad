import numpy as np
import matplotlib.pyplot as plt


def my_plot(title, *args, y, x, figures: tuple, **kwargs):
    color = ['b', 'g', 'r', 'c', 'm', 'y']
    plt.suptitle(title)
    if type(y) == list:
        plt.plot(y, x)
    elif len(figures) != 2 and type(y) == tuple:
        figures = (len(y), 1)
        for item in range(len(y)):
            plt.subplot(figures[0], figures[1], item+1)
            plt.plot(y[item], x[item], alpha=0.8, color=color[item])
    plt.show()
    pass


if __name__ == "__main__":
    a = list(range(10))
    b = list(range(1, 11))
    c = {"a": a, "b": b}
    my_plot("chenwang", x=(a, b), y=(a, b))
    input("")