import json
import numpy as np
import scipy.stats as st
from pybss_testbed import *
import pickle

import matplotlib
import matplotlib.pyplot as plt
from matplotlib import gridspec
from utils import *

matplotlib.use('TkAgg')

print(matplotlib.get_configdir())

if __name__ == '__main__':
    nodes = 6
    number_test = 1

    fr = open('./emulator/MIMII/saxsNew.pkl', 'rb')
    saxs = pickle.load(fr)
    ss, aa, xx = saxs
    s = ss[number_test]
    x = xx[number_test]

    path_server_csv = './emulator/measurement/'+str(nodes)+'s/server_cf.csv'
    process_latency = np.loadtxt(path_server_csv, delimiter=',', usecols=[1])[
        number_test] * 1000
    w = np.array(json.loads(measure_read_csv_to_2dlist(
        path_server_csv)[number_test][3].replace('|', ',')))
    hat_s = np.dot(w, x)
    separation_accuracy = pybss_tb.bss_evaluation(s, hat_s, type='sdr')

    for node in range(nodes-1, -1, -1):
        path_vnf_csv = './emulator/measurement/' + \
            str(nodes)+'s/vnf' + str(node)+'-s' + str(node)+'.csv'
        vnf_latency = np.loadtxt(path_vnf_csv, delimiter=',', usecols=[3])[
            number_test] * 1000
        process_latency = np.row_stack((vnf_latency, process_latency))
        w = np.array(json.loads(measure_read_csv_to_2dlist(
            path_vnf_csv)[number_test][5].replace('|', ',')))
        hat_s = np.dot(w, x)
        vnf_accuracy = pybss_tb.bss_evaluation(s, hat_s, type='sdr')
        separation_accuracy = np.row_stack((vnf_accuracy, separation_accuracy))

    path_details_csv = './emulator/measurement/pICA_' + str(nodes)+'details.csv'
    len_subset = np.loadtxt(path_details_csv, delimiter=',', usecols=np.arange(
        1, len(separation_accuracy)+1, 1))

    len_subset = len_subset[0, :]
    process_latency = process_latency[:, 0]
    separation_accuracy = separation_accuracy[:, 0]

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
            'compute_forward': 'p',
            'store_forward': 'o',
            'store_forward_ia': 's'
        }

        plt.rcParams.update({'font.size': 11})

        fig = plt.figure(figsize=(fig_width, fig_width / 1.618))
        ax = fig.add_subplot(1, 1, 1)
        ax.yaxis.grid(True, linestyle='--', which='major',
                      color='lightgrey', alpha=0.5, linewidth=0.2)
        x_index = np.arange(nodes + 1)
        bar1 = ax.bar(x_index-barwidth, len_subset/np.max(len_subset)*100, barwidth, fill=True,
                      color=colordict['darkblue'], edgecolor='#FFFFFF', ecolor='#555555', hatch='\\')
        bar2 = ax.bar(x_index, process_latency/sum(process_latency)*100, barwidth, fill=True,
                      color=colordict['lightblue'], edgecolor='#FFFFFF', ecolor='#555555', hatch='/')
        bar3 = ax.bar(x_index+barwidth, separation_accuracy/separation_accuracy[-1]*100, barwidth, fill=True,
                      color=colordict['midblue'], edgecolor='#FFFFFF', ecolor='#555555', hatch='//')
        
        # ax.set_xlabel(r'Number of nodes $k$')
        ax.set_ylabel(r'Percent in total cost ($\%$)')
        ax.set_yticks(np.arange(0, 101, 20))
        # ax.set_xlim([2, 60000])
        # ax.set_ylim([0, 201])
        ax.legend([bar1, bar2, bar3], [
            'Subset data size', 'Processing time', 'Processing precision'], loc='upper left', ncol=1)
        plt.xticks(x_index, ['Node 1', 'Node 2', 'Node 3',
                             'Node 4', 'Node 5', 'Node 6', 'Remote \n Agent'], rotation=30)
        plt.savefig('./emulator/measurement/nodes_performance_emu.pdf',
                    dpi=600, bbox_inches='tight')
