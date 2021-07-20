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
    number_node = [4, 5, 6, 7]
    conf_rate = 0.95
    number_test = 50

    fr = open('./emulator/MIMII/saxsNew.pkl', 'rb')
    saxs = pickle.load(fr)
    ss, aa, xx = saxs

    accuracy_cf = np.zeros(number_test)
    accuracy_sf = np.zeros(number_test)
    for node in number_node:
        path_server_compute_client = './emulator/measurement/' + \
            str(node)+'s/server_cf.csv'
        path_server_store_client = './emulator/measurement/' + \
            str(node)+'s/server_sf.csv'
        node_accuracy_cf = []
        node_accuracy_sf = []

        for test_id in range(number_test):
            s = ss[test_id]
            x = xx[test_id]

            w = np.array(json.loads(measure_read_csv_to_2dlist(path_server_compute_client)[test_id][3].replace('|', ',')))
            hat_s = np.dot(w, x)
            node_accuracy_cf = np.append(node_accuracy_cf, pybss_tb.bss_evaluation(s, hat_s, type='sdr'))

            w = np.array(json.loads(measure_read_csv_to_2dlist(path_server_store_client)[test_id][3].replace('|', ',')))
            hat_s = np.dot(w, x)
            node_accuracy_sf = np.append(node_accuracy_sf, pybss_tb.bss_evaluation(s, hat_s, type='sdr'))

        measure_write('pICA_accuracy_cf', node_accuracy_cf)
        measure_write('pICA_accuracy_sf', node_accuracy_sf)

        accuracy_cf = np.row_stack(
            (accuracy_cf, node_accuracy_cf))
        accuracy_sf = np.row_stack(
            (accuracy_sf, node_accuracy_sf))
        
    accuracy_cf = accuracy_cf[1:, :]
    accuracy_sf = accuracy_sf[1:, :]

    ts_cf_conf = get_conf_interval(number_node, accuracy_cf, conf_rate)
    ts_sf_conf = get_conf_interval(number_node, accuracy_sf, conf_rate)

    # with plt.style.context(['science', 'ieee']):
    #     fig_width = 6.5
    #     barwidth = 0.15
    #     # bardistance = barwidth * 1.2
    #     colordict = {
    #         'compute_forward': '#0077BB',
    #         'store_forward': '#DDAA33',
    #         'darkblue': '#024B7A',
    #         'lightblue': '#3F9ABF',
    #         'midblue': '#7ACFE5'
    #     }
    #     markerdict = {
    #         'compute_forward': 'o',
    #         'store_forward': 'v',
    #         'store_forward_ia': 's'
    #     }

    #     plt.rcParams.update({'font.size': 11})

    #     fig = plt.figure(figsize=(fig_width, fig_width / 1.618))
    #     ax = fig.add_subplot(1, 1, 1)
    #     ax.yaxis.grid(True, linestyle='--', which='major',
    #                   color='lightgrey', alpha=0.5, linewidth=0.2)
    #     x_index = np.arange(nodes + 1)
    #     bar1 = ax.bar(x_index-barwidth, len_subset/np.max(len_subset)*100, barwidth, fill=True,
    #                   color=colordict['darkblue'], edgecolor='#FFFFFF', ecolor='#555555', hatch='\\')
    #     bar2 = ax.bar(x_index, process_latency/sum(process_latency)*100, barwidth, fill=True,
    #                   color=colordict['lightblue'], edgecolor='#FFFFFF', ecolor='#555555', hatch='/')
    #     bar3 = ax.bar(x_index+barwidth, separation_accuracy/separation_accuracy[-1]*100, barwidth, fill=True,
    #                   color=colordict['midblue'], edgecolor='#FFFFFF', ecolor='#555555', hatch='//')
        
    #     # ax.set_xlabel(r'Number of nodes $k$')
    #     ax.set_ylabel(r'Percent in total cost ($\%$)')
    #     ax.set_yticks(np.arange(0, 101, 20))
    #     # ax.set_xlim([2, 60000])
    #     # ax.set_ylim([0, 201])
    #     ax.legend([bar1, bar2, bar3], [
    #         'Subset data size', 'Processing time', 'Processing precision'], loc='upper left', ncol=1)
    #     plt.xticks(x_index, ['Node 1', 'Node 2', 'Node 3',
    #                          'Node 4', 'Node 5', 'Node 6', 'Node 7', 'Remote \n Agent'], rotation=30)
    #     plt.savefig('./emulator/measurement/nodes_performance_details_emu.pdf',
    #                 dpi=600, bbox_inches='tight')
