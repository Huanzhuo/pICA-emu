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
    node_number = [0, 2, 4] # k
    dataset_id = 0
    test_mode = '_cf_us'  # _sf _cf _cf_us

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

        plt.rcParams.update({'font.size': 11})

        fig = plt.figure(figsize=(fig_width, fig_width / 1.618))
        ax = fig.add_subplot(1, 1, 1)
        ax.yaxis.grid(True, linestyle='--', which='major',
                    color='lightgrey', alpha=0.5, linewidth=0.2)

        for node_id in node_number:
            path_w_improve_csv = './emulator/measurement/' + str(node_id)+'s/pICA_'+str(dataset_id)+test_mode+'.csv'
            time_accuracy = np.loadtxt(path_w_improve_csv, delimiter=',', usecols=[0, 1])
            if node_id == 0:
                line1 = ax.plot(time_accuracy[:, 0]*1000, time_accuracy[:, 1]/np.max(time_accuracy[:, 1])*100, color=colorlist[node_id], lw=1, ls='-', marker=markerlist[node_id], ms=2, label=r'$k=$ '+str(node_id))
            else:
                line1 = ax.plot(time_accuracy[:, 0]*1000, time_accuracy[:, 1]/np.max(time_accuracy[:, 1])*100, color=colorlist[node_id], lw=1, ls='-', marker=markerlist[node_id], ms=2, label=r'$k=$ '+str(node_id))

            # bar1 = ax.bar(x_index-barwidth, len_subset/np.max(len_subset)*100, barwidth, fill=True,
            #             color=colordict['darkblue'], edgecolor='#FFFFFF', ecolor='#555555', hatch='\\')
            # bar2 = ax.bar(x_index, process_latency/sum(process_latency)*100, barwidth, fill=True,
            #             color=colordict['lightblue'], edgecolor='#FFFFFF', ecolor='#555555', hatch='/')
            # bar3 = ax.bar(x_index+barwidth, separation_accuracy/separation_accuracy[-1]*100, barwidth, fill=True,
            #             color=colordict['midblue'], edgecolor='#FFFFFF', ecolor='#555555', hatch='//')
            
        ax.set_xlabel(r'Time ($ms$)')
        # ax.set_xlim([1, 10000])
        ax.set_xticks(np.arange(0, 10001, 2000))
        ax.set_xscale('log')
        ax.set_ylabel(r'Accruracy improvement ($\%$)')
        ax.set_yticks(np.arange(0, 101, 20))
        # ax.set_xlim([2, 60000])
        # ax.set_ylim([0, 201])
        # ax.legend([bar1, bar2, bar3], [
        #     'Subset data size', 'Processing time', 'Processing precision'], loc='upper left', ncol=1)
        # plt.xticks(x_index, ['Node 1', 'Node 2', 'Node 3',
        #                     'Node 4', 'Node 5', 'Node 6', 'Remote \n Agent'], rotation=30)
        plt.legend()
        plt.savefig('./emulator/measurement/w_improvement_'+str(dataset_id)+test_mode+'.pdf',
                    dpi=600, bbox_inches='tight')