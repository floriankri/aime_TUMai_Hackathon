import matplotlib
import matplotlib.pyplot as plt
import utils

matplotlib.rcParams['font.family'] = 'sans-serif'
matplotlib.rcParams['figure.figsize'] = [22, 5]

matplotlib.rcParams['image.cmap'] = 'Blues'


def plot_loss_accuracy(
    train_loss: list[float], val_loss: list[float],
    train_acc: list[float], val_acc: list[float],
):
    if len(train_acc) > 0:
        _, (ax1, ax2) = plt.subplots(1, 2)
    else:
        ax1 = plt.subplot()

    def add_subgraph(ax, training, validation):
        ax.plot(training, label='Training', color=utils.LIGHT_BLUE)
        ax.plot(validation, label='Validation', color=utils.BASIC_BLUE)
        ax.set_xlabel('Epoch')
        ax.legend()

    ax1.set_title('Loss')
    add_subgraph(ax1, train_loss, val_loss)

    if len(train_acc) > 0:
        ax2.set_title('Accuracy')
        ax2.set_ylim((0, 1))
        add_subgraph(ax2, train_acc, val_acc)

    plt.show()


def plot_test_output(output, target):
    data = [output, target]
    ax = plt.subplot()
    ax.matshow(data, aspect='auto', norm=None)
    ax.get_xaxis().set_visible(False)
    ax.get_yaxis().set_visible(False)
    plt.show()
