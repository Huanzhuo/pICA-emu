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
    stoppage_k = np.array([[50, 50, 50, 43, 37, 26, 14,  0],
                           [0,  0,  0,  7,  13, 24, 32, 24]])
    with plt.style.context(['science', 'ieee']):
        fig_width = 6.5
        barwidth = 0.25
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

        plt.rcParams.update({'font.size': 11})

        fig = plt.figure(figsize=(fig_width, fig_width / 1.618))
        ax = fig.add_subplot(1, 1, 1)
        ax.xaxis.grid(True, linestyle='--', which='major',
                      color='lightgrey', alpha=1, linewidth=0.2)
        ax.yaxis.grid(True, linestyle='--', which='both',
                      color='lightgrey', alpha=1, linewidth=0.2)
        # ax_twin = ax.twinx()
        x_index = stoppage[:, 0]
        bar1 = ax.bar(x_index-bardistance, stoppage[:, 1], barwidth, fill=True,
                      color=colordict['compute_forward'], edgecolor='#FFFFFF', ecolor='#555555', hatch='\\', label='Greedy Stoppage')
        bar2 = ax.bar(x_index+bardistance, stoppage[:, 2], barwidth, fill=True,
                      color=colordict['store_forward'], edgecolor='#FFFFFF', ecolor='#555555', hatch='//', label='Normal Stoppage')
        # line, = ax_twin.plot(x_index, stoppage[:, 1]/stoppage[:, 3]*100, color=colordict['compute_forward'],
        #                      lw=1.2, ls='-', marker=markerdict['compute_forward'], ms=4, markerfacecolor='none', label='Greedy Stoppage')
        for i in x_index:
            ax.text(i-bardistance*3, max(stoppage[i, 1], stoppage[i, 2])+5, r'$'+str(
                round(stoppage[i, 1]/stoppage[i, 3], 4)*100)+r'\%$', rotation=25)
            # ax.text(i+bardistance*0, stoppage[i, 2]+5, r'$'+str(round(stoppage[i, 2]/stoppage[i, 3], 3)*100)+r'\%$', rotation=45)
        ax.set_xlabel(r'Number of nodes $k$')
        ax.set_ylabel(r'Number of triggered stoppage')
        ax.set_xlim([-0.5, 7.5])
        ax.set_xticks(range(len(number_node)))
        ax.set_yticks(np.arange(0, 351, 50))
        # ax_twin.set_ylabel(r'Greedy strategy in percentage ($\%$)')
        # ax_twin.set_xlim([-0.5, 7.5])
        # ax_twin.set_ylim([0, 100])
        # ax_twin.set_xticks(range(len(number_node)))
        # ax_twin.set_yticks(np.arange(0, 101, 20))
        # ax.legend([line1, line2, line3], ['pICA',
        #                                   'FastICA', 'pICA hbh'], loc='upper right')
        # plt.xticks(range(len(number_node)), number_node)
        ax.legend(handles=[bar1, bar2], loc='upper left')
        plt.savefig('./emulator/measurement/plot/greedy_stoppage.pdf',
                    dpi=600, bbox_inches='tight')

        fig = plt.figure(figsize=(fig_width, fig_width / 1.618))
        ax = fig.add_subplot(1, 1, 1)
        ax.xaxis.grid(True, linestyle='--', which='major',
                      color='lightgrey', alpha=1, linewidth=0.2)
        ax.yaxis.grid(True, linestyle='--', which='major',
                      color='lightgrey', alpha=1, linewidth=0.2)
        x_index = np.arange(0, len(stoppage_k[0, :]))
        bar1 = ax.bar(x_index, stoppage_k[0, :], barwidth, fill=True,
                      color=colordict['compute_forward'], edgecolor='#000000', ecolor='#555555', lw=0.8, hatch='\\', label='Greedy Stoppage')
        bar2 = ax.bar(x_index, stoppage_k[1, :], barwidth, bottom=stoppage_k[0, :], fill=True,
                      color=colordict['store_forward'], edgecolor='#000000', ecolor='#555555', lw=0.8, hatch='//', label='Normal Stoppage')
        for i in x_index:
            if stoppage_k[0, i] != 0:
                ax.text(i-bardistance*2.5, stoppage_k[0, i]/2-3, r'$'+str(
                    "{:.0f}".format(stoppage_k[0, i]/50*100))+r'\%$', rotation=90)
            if stoppage_k[1, i] != 0:
                ax.text(i-bardistance*2.5, stoppage_k[1, i]/2+stoppage_k[0, i]-2, r'$'+str(
                    "{:.0f}".format(stoppage_k[1, i]/50*100))+r'\%$', rotation=90)
        ax.set_xlabel(r'Index of network nodes')
        ax.set_ylabel(r'Number of triggered stoppage')
        ax.set_xlim([-0.7, 7.5])
        ax.set_ylim([0, 65])
        ax.set_xticks(range(len(number_node)))
        ax.set_yticks(np.arange(0, 61, 10))
        plt.xticks(x_index, ['1', '2', '3', '4', '5', '6', '7', 'RA'])
        ax.legend(handles=[bar1, bar2], loc='upper right')
        plt.savefig('./emulator/measurement/plot/greedy_stoppage_7.pdf',
                    dpi=600, bbox_inches='tight')
