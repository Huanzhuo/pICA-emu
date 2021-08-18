import json
import numpy as np
import scipy.stats as st

import matplotlib
import matplotlib.pyplot as plt
from matplotlib import gridspec

matplotlib.use('TkAgg')

print(matplotlib.get_configdir())


def get_conf_interval(index, data, conf_rate):
    data_stat = []
    # index = data[:, 0].astype(int)
    for i in range(len(index)):
        conf_interval_low, conf_interval_high = st.t.interval(conf_rate, len(
            data[i, :])-1, loc=np.mean(data[i, :]), scale=st.sem(data[i, :]))
        conf_mean = np.mean(data[i, :])
        data_stat.append([index[i], conf_interval_low,
                         conf_mean, conf_interval_high])
    return np.array(data_stat)


if __name__ == '__main__':
    number_node = [0, 1, 2, 3, 4, 5, 6, 7]
    conf_rate = 0.95
    number_test = 50

    stoppage = np.array([[0, 0, 50, 50],
                        [1, 50, 50, 100],
                        [2, 99, 51, 150],
                        [3, 147, 53, 200],
                        [4, 191, 59, 250],
                        [5, 230, 68, 298],
                        [6, 256, 89, 345],
                        [7, 273, 96, 369]])
    with plt.style.context(['science', 'ieee']):
        fig_width = 6.5
        barwidth = 0.2
        bardistance = barwidth * 0.6
        colordict = {
            'compute_forward': '#0077BB',
            'store_forward': '#DDAA33',
            'store_forward_ia': '#009988',
            'orange': '#EE7733',
            'red': '#993C00',
            'blue': '#3340AD'
        }
        markerdict = {
            'compute_forward': 'p',
            'store_forward': 'o',
            'store_forward_ia': 's'
        }

        plt.rcParams.update({'font.size': 10})

        fig = plt.figure(figsize=(fig_width, fig_width / 1.618))
        ax = fig.add_subplot(1, 1, 1)
        ax.yaxis.grid(True, linestyle='--', which='major',
                      color='lightgrey', alpha=0.5, linewidth=0.2)
        ax_twin = ax.twinx()
        x_index = np.arange(len(number_node))
        bar1 = ax.bar(x_index-bardistance, stoppage[:, 1], barwidth, fill=True,
                      color=colordict['blue'], edgecolor='#FFFFFF', ecolor='#555555', hatch='\\', label='Greedy Stoppage')
        bar2 = ax.bar(x_index+bardistance, stoppage[:, 2], barwidth, fill=True,
                      color=colordict['orange'], edgecolor='#FFFFFF', ecolor='#555555', hatch='//', label='Normal Stoppage')
        line, = ax_twin.plot(x_index, stoppage[:, 1]/stoppage[:, 3]*100, color=colordict['compute_forward'],
                             lw=1.2, ls='-', marker=markerdict['compute_forward'], ms=4, markerfacecolor='none', label='Greedy Stoppage')
        ax.set_xlabel(r'Number of nodes $k$')
        ax.set_ylabel(r'Number of triggered stoppage')
        ax.set_xlim([-0.5, 7.5])
        ax.set_xticks(range(len(number_node)))
        ax.set_yticks(np.arange(0, 501, 100))
        ax_twin.set_ylabel(r'Greedy strategy in percentage ($\%$)')
        ax_twin.set_xlim([-0.5, 7.5])
        ax_twin.set_ylim([0, 100])
        ax_twin.set_xticks(range(len(number_node)))
        ax_twin.set_yticks(np.arange(0, 101, 20))
        # ax.legend([line1, line2, line3], ['pICA',
        #                                   'FastICA', 'pICA hbh'], loc='upper right')
        # plt.xticks(range(len(number_node)), number_node)
        ax.legend(handles=[bar1, bar2, line], loc='upper left')
        plt.savefig('./emulator/measurement/plot/greedy_stoppage.pdf',
                    dpi=600, bbox_inches='tight')
