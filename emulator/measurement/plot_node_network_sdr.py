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
    number_node = [0, 1, 2, 3, 4, 5, 6, 7, 8]
    conf_rate = 0.95
    number_test = 50

    # accuracy_cf = np.zeros(number_test)
    # accuracy_sf = np.zeros(number_test)
    path_compute = './emulator/measurement/pICA_accuracy_cf.csv'
    path_store = './emulator/measurement/pICA_accuracy_cf.csv'

    accuracy_cf = np.loadtxt(path_compute, delimiter=',', usecols=np.arange(0, len(number_node), 1))
    accuracy_sf = np.loadtxt(path_store, delimiter=',', usecols=np.arange(0, len(number_node), 1))

    accuracy_cf_conf = get_conf_interval(number_node, accuracy_cf, conf_rate)
    accuracy_sf_conf = get_conf_interval(number_node, accuracy_sf, conf_rate)

    # codes for plot figures
    with plt.style.context(['science', 'ieee']):
        fig_width = 6.5
        # barwidth = 0.15
        # bardistance = barwidth * 1.2
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
        barwidth = 0.3

        plt.rcParams.update({'font.size': 11})
        fig = plt.figure(figsize=(fig_width, fig_width / 1.618))
        ax = fig.add_subplot(1, 1, 1)
        ax.yaxis.grid(True, linestyle='--', which='major',
                      color='lightgrey', alpha=0.5, linewidth=0.2)
        x_index = np.arange(len(number_node))
        bar1 = ax.bar(x_index-barwidth/2, accuracy_cf_conf[:, 2], barwidth, yerr=accuracy_cf_conf[:, 3] - accuracy_cf_conf[:, 2],
                      error_kw=dict(lw=1, capsize=2, capthick=1), fill=True, color=colordict['compute_forward'], edgecolor='#FFFFFF', ecolor='#555555', hatch='\\')
        bar2 = ax.bar(x_index+barwidth/2, accuracy_sf_conf[:, 2], barwidth, yerr=accuracy_sf_conf[:, 3] - accuracy_sf_conf[:, 2],
                      error_kw=dict(lw=1, capsize=2, capthick=1), fill=True, color=colordict['store_forward'], edgecolor='#FFFFFF', ecolor='#555555', hatch='/')

        ax.set_xlabel(r'Number of nodes $k$')
        ax.set_ylabel(r'Processing precision SDR ($dB$)')
        ax.set_yticks(np.arange(0, 41, 5))
        # ax.set_xlim([2, 60000])
        # ax.set_ylim([0, 201])
        ax.legend([bar1, bar2], [
            'pICA', 'FastICA'], loc='upper right', ncol=1)
        plt.xticks(range(len(number_node)), number_node)
        plt.savefig('emulator/measurement/process_accuracy_emu.pdf',
                    dpi=600, bbox_inches='tight')