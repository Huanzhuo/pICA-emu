import json
import numpy as np
import scipy.stats as st
from scipy.stats.stats import mode
from pybss_testbed import *
import pickle

import matplotlib
import matplotlib.pyplot as plt
from matplotlib import gridspec
from utils import *

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
    node_number = [1, 4, 7]  # k
    test_mode = ['_cf', '_sf', '_cf_hbh']  # _sf _cf _cf_us
    conf_rate = 0.95
    dataset_number = 30

    with plt.style.context(['science', 'ieee']):
        fig_width = 6.5*2
        barwidth = 0.15
        colordict = {
            '_cf': '#0077BB',
            '_sf': '#DDAA33',
            '_cf_hbh': '#009988',
            'darkblue': '#024B7A',
            'lightblue': '#3F9ABF',
            'midblue': '#7ACFE5'
        }
        markerdict = {
            '_cf': 'd',
            '_sf': 'o',
            '_cf_hbh': 's'
        }
        legenddict = {
            '_sf': 'FastICA',
            '_cf': 'pICA',
            '_cf_hbh': 'pICA hbh'
        }

        plt.rcParams.update({'font.size': 11})

        fig = plt.figure(figsize=(fig_width, fig_width / 2.5))
        spec = gridspec.GridSpec(
            ncols=len(node_number), nrows=2, height_ratios=[1, 1])
        i = 0
        for node_id in node_number:
            for mode_id in ['_sf', '_cf_hbh']:
                ax_1 = fig.add_subplot(spec[i])
                ax_1.yaxis.grid(True, linestyle='--', which='major',
                                color='lightgrey', alpha=0.5, linewidth=0.2)

                path_compute_accuracy = './emulator/measurement/results_v4/' + \
                    str(node_id)+'s/pICA_accuracy'+mode_id+'.csv'
                path_compute_timestamp = './emulator/measurement/results_v4/' + \
                    str(node_id)+'s/pICA_time'+mode_id+'.csv'

                compute_accuracy = np.loadtxt(
                    path_compute_accuracy, delimiter=',', usecols=np.arange(0, dataset_number))
                compute_timestamp = np.loadtxt(
                    path_compute_timestamp, delimiter=',', usecols=np.arange(0, dataset_number))

                compute_timestamp_conf = get_conf_interval(
                    compute_timestamp[:, 0], compute_timestamp[:, 1:], conf_rate)
                compute_accuracy_conf = get_conf_interval(
                    compute_accuracy[:, 0], compute_accuracy[:, 1:], conf_rate)

                line_1 = ax_1.errorbar(compute_timestamp_conf[:, 2], compute_accuracy_conf[:, 2], color=colordict[mode_id], lw=1.2, ls='-', marker=markerdict[mode_id], ms=4, markerfacecolor='none', label=legenddict[mode_id])
                line_1_fill = ax_1.fill_between(compute_timestamp_conf[:, 2], compute_accuracy_conf[:, 1], compute_accuracy_conf[:, 3], color=colordict[mode_id], alpha=0.2)

                # ax_1.set_xlabel(r'Time ($ms$)')
                ax_1.set_xticks(np.arange(0, 19, 3))
                ax_1.set_ylabel(r'SDR ($dB$)')
                # if i == 0:
                #     ax_1.set_ylabel(r'SDR ($dB$)')
                ax_1.set_yticks(np.arange(0, 31, 5))
                ax_1.legend(loc='lower right')
            j = i + len(node_number)
            for mode_id in ['_sf', '_cf']:
                ax_2 = fig.add_subplot(spec[j])
                ax_2.yaxis.grid(True, linestyle='--', which='major',
                                color='lightgrey', alpha=0.5, linewidth=0.2)

                path_compute_accuracy = './emulator/measurement/results_v4/' + \
                    str(node_id)+'s/pICA_accuracy'+mode_id+'.csv'
                path_compute_timestamp = './emulator/measurement/results_v4/' + \
                    str(node_id)+'s/pICA_time'+mode_id+'.csv'

                compute_accuracy = np.loadtxt(
                    path_compute_accuracy, delimiter=',', usecols=np.arange(0, dataset_number))
                compute_timestamp = np.loadtxt(
                    path_compute_timestamp, delimiter=',', usecols=np.arange(0, dataset_number))

                compute_timestamp_conf = get_conf_interval(
                    compute_timestamp[:, 0], compute_timestamp[:, 1:], conf_rate)
                compute_accuracy_conf = get_conf_interval(
                    compute_accuracy[:, 0], compute_accuracy[:, 1:], conf_rate)

                line_2 = ax_2.errorbar(compute_timestamp_conf[:, 2], compute_accuracy_conf[:, 2], color=colordict[mode_id], lw=1.2, ls='-', marker=markerdict[mode_id], ms=4, markerfacecolor='none', label=legenddict[mode_id])
                line_2_fill = ax_2.fill_between(compute_timestamp_conf[:, 2], compute_accuracy_conf[:, 1], compute_accuracy_conf[:, 3], color=colordict[mode_id], alpha=0.2)

                ax_2.set_xlabel(r'Service latency $t_s$ ($s$), $k = ' +
                                str(str(node_id)) + r'$')
                ax_2.set_xticks(np.arange(0, 19, 3))
                ax_2.set_ylabel(r'SDR ($dB$)')
                # if i == 0:
                #     ax_2.set_ylabel(r'Accruracy improvement ($\%$)')
                ax_2.set_yticks(np.arange(0, 31, 5))
                ax_2.legend(loc='lower right')
            i = i + 1
        # plt.legend(loc='lower right')
        fig.subplots_adjust(hspace=0.10, wspace=0.20)
        plt.savefig('./emulator/measurement/plot/w_improvement.pdf',
                    dpi=600, bbox_inches='tight')
