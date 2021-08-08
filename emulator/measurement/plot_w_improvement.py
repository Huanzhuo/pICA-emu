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
    node_number = 5 # k
    # dataset_id = 0
    test_mode = ['_cf', '_sf', '_cf_us']  # _sf _cf _cf_us
    conf_rate = 0.95

    with plt.style.context(['science', 'ieee']):
        fig_width = 6.5
        barwidth = 0.15
        # bardistance = barwidth * 1.2
        colordict = {
            'compute_forward': '#0077BB',
            'store_forward': '#DDAA33',
            'darkblue': '#024B7A',
            'lightblue': '#3F9ABF',
            'midblue': '#7ACFE5'
        }
        markerdict = {
            'compute_forward': 'o',
            'store_forward': 'v',
            'store_forward_ia': 's'
        }
        colorlist = ['#DDAA33', '#0077BB', '#0077BB', '#024B7A', '#024B7A', '#3F9ABF', '#3F9ABF', '#7ACFE5', '#7ACFE5']
        markerlist = ['o', 'v', 'v', 's', 's', 'v', 'v', 's', 's']

        plt.rcParams.update({'font.size': 10})

        fig = plt.figure(figsize=(fig_width, fig_width / 1.618))
        ax = fig.add_subplot(1, 1, 1)
        ax.yaxis.grid(True, linestyle='--', which='major',
                    color='lightgrey', alpha=0.5, linewidth=0.2)

        for mode_id in test_mode:
            i = 0
            path_compute_accuracy = './emulator/measurement/results_v4/' + str(node_number)+'s/pICA_accuracy'+mode_id+'.csv'
            path_compute_timestamp = './emulator/measurement/results_v4/' + str(node_number)+'s/pICA_time'+mode_id+'.csv'
            if mode_id != '_sf':
                compute_accuracy = np.loadtxt(path_compute_accuracy, delimiter=',', usecols=np.arange(0, (node_number+1)*2))
                compute_timestamp = np.loadtxt(path_compute_timestamp, delimiter=',', usecols=np.arange(0, (node_number+1)*2))
            else:
                compute_accuracy = np.loadtxt(path_compute_accuracy, delimiter=',', usecols=np.arange(0, 3))
                compute_timestamp = np.loadtxt(path_compute_timestamp, delimiter=',', usecols=np.arange(0, 3))
            
            compute_timestamp_conf = get_conf_interval(compute_timestamp[:, 0], compute_timestamp[:, 1:], conf_rate)
            compute_accuracy_conf = get_conf_interval(compute_accuracy[:, 0], compute_accuracy[:, 1:], conf_rate)

            line = ax.errorbar(compute_timestamp_conf[:, 2], compute_accuracy_conf[:, 2], color=colorlist[i], lw=1, ls='-', marker=markerlist[i], ms=5)
            line_fill = ax.fill_between(compute_timestamp_conf[:, 2], compute_accuracy_conf[:, 1], compute_accuracy_conf[:, 3], color=colorlist[i], alpha=0.2)

            i = i + 1


            # bar1 = ax.bar(x_index-barwidth, len_subset/np.max(len_subset)*100, barwidth, fill=True,
            #             color=colordict['darkblue'], edgecolor='#FFFFFF', ecolor='#555555', hatch='\\')
            # bar2 = ax.bar(x_index, process_latency/sum(process_latency)*100, barwidth, fill=True,
            #             color=colordict['lightblue'], edgecolor='#FFFFFF', ecolor='#555555', hatch='/')
            # bar3 = ax.bar(x_index+barwidth, separation_accuracy/separation_accuracy[-1]*100, barwidth, fill=True,
            #             color=colordict['midblue'], edgecolor='#FFFFFF', ecolor='#555555', hatch='//')
            
        ax.set_xlabel(r'Time ($ms$)')
        # ax.set_xlim([1, 10000])
        # ax.set_xticks(np.arange(0, 10001, 2000))
        # ax.set_xscale('log')
        ax.set_ylabel(r'Accruracy improvement ($\%$)')
        # ax.set_yticks(np.arange(0, 101, 20))
        # ax.set_xlim([2, 60000])
        # ax.set_ylim([0, 201])
        # ax.legend([bar1, bar2, bar3], [
        #     'Subset data size', 'Processing time', 'Processing precision'], loc='upper left', ncol=1)
        # plt.xticks(x_index, ['Node 1', 'Node 2', 'Node 3',
        #                     'Node 4', 'Node 5', 'Node 6', 'Remote \n Agent'], rotation=30)
        plt.legend()
        plt.savefig('./emulator/measurement/plot/w_improvement_'+str(node_number)+test_mode+'.pdf',
                    dpi=600, bbox_inches='tight')