import json
import numpy as np
from numpy.core.fromnumeric import size
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
    nodes = 7
    number_node = 7
    number_test = 50
    conf_rate = 0.99
    # emulator/measurement/results_v4/pICA_7details.csv
    path_csv = './emulator/measurement/results_v4/pICA_' + \
        str(nodes)+'details.csv'
    node_details = np.loadtxt(path_csv, delimiter=',', usecols=np.arange(
        1, nodes+2, 1))
    len_subset = node_details[0, :]
    process_latency = node_details[1, :]
    separation_accuracy = node_details[2, :]

    path_lens_csv = './emulator/measurement/results_v4/pICA_' + \
        str(nodes)+'_lens.csv'
    node_lens = np.loadtxt(path_lens_csv, delimiter=',', usecols=np.arange(
        0, number_test+1, 1))[1:, :]
    for i in range(1, node_lens.shape[1]-1, 1):
        node_lens[:, i] = node_lens[:, i]/max(node_lens[:, i])*100
    # node_lens_conf = get_conf_interval(node_lens[:, 0], node_lens[:, 1:], conf_rate)
    path_accuracy_csv = './emulator/measurement/results_v4/pICA_' + \
        str(nodes)+'_accuracy.csv'
    node_accuracy = np.loadtxt(path_accuracy_csv, delimiter=',', usecols=np.arange(
        0, number_test+1, 1))[1:, :]
    for i in range(1, node_accuracy.shape[1]-1, 1):
        node_accuracy[:, i] = node_accuracy[:, i]/max(node_accuracy[:, i])*100
    node_accuracy_conf = get_conf_interval(
        node_accuracy[:, 0], node_accuracy[:, 1:], conf_rate)
    path_time_csv = './emulator/measurement/results_v4/pICA_' + \
        str(nodes)+'_time.csv'
    node_time = np.loadtxt(path_time_csv, delimiter=',', usecols=np.arange(
        0, number_test+1, 1))[1:, :]
    for i in range(1, node_time.shape[1]-1, 1):
        node_time[:, i] = node_time[:, i]/sum(node_time[:, i])*100

    with plt.style.context(['science', 'ieee']):
        fig_width = 6.5
        barwidth = 0.15
        bardistance = barwidth * 1.2
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

        plt.rcParams.update({'font.size': 11})

        # fig = plt.figure(figsize=(fig_width, fig_width / 1.618))
        # ax = fig.add_subplot(1, 1, 1)
        # ax.yaxis.grid(True, linestyle='--', which='major',
        #               color='lightgrey', alpha=0.5, linewidth=0.2)
        # x_index = np.arange(nodes + 1)
        # bar1 = ax.bar(x_index-barwidth, len_subset/np.max(len_subset)*100, barwidth, fill=True,
        #               color=colordict['darkblue'], edgecolor='#FFFFFF', ecolor='#555555', hatch='\\')
        # bar2 = ax.bar(x_index, process_latency/sum(process_latency)*100, barwidth, fill=True,
        #               color=colordict['lightblue'], edgecolor='#FFFFFF', ecolor='#555555', hatch='/')
        # bar3 = ax.bar(x_index+barwidth, separation_accuracy/separation_accuracy[-1]*100, barwidth, fill=True,
        #               color=colordict['midblue'], edgecolor='#FFFFFF', ecolor='#555555', hatch='//')

        # # ax.set_xlabel(r'Number of nodes $k$')
        # ax.set_ylabel(r'Percent in total cost ($\%$)')
        # ax.set_yticks(np.arange(0, 101, 20))
        # # ax.set_xlim([2, 60000])
        # # ax.set_ylim([0, 201])
        # ax.legend([bar1, bar2, bar3], [
        #     r'Subset data size $lX$', r'Computing time $t_c$', r'Separation precision SDR'], loc='upper left', ncol=1)
        # plt.xticks(x_index, ['Node 1', 'Node 2', 'Node 3', 'Node 4',
        #            'Node 5', 'Node 6', 'Node 7', 'Remote \n Agent'], rotation=30)
        # plt.savefig('./emulator/measurement/plot/nodes_performance_simu.pdf',
        #             dpi=600, bbox_inches='tight')

        fig = plt.figure(figsize=(fig_width, fig_width / 1.618))
        ax = fig.add_subplot(1, 1, 1)
        ax.xaxis.grid(True, linestyle='--', which='major',
                      color='lightgrey', alpha=0.5, linewidth=0.2)
        ax.yaxis.grid(True, linestyle='--', which='major',
                      color='lightgrey', alpha=0.5, linewidth=0.2)
        x_index = np.arange(1, nodes + 2)
        for i in range(1, node_lens.shape[1]-1):
            sct1 = ax.scatter(x_index-barwidth, node_lens[:, i], color=colordict['lightblue'], marker='X', s=40, facecolors='none')
            sct2 = ax.scatter(x_index+barwidth, node_time[:, i], color=colordict['midblue'], marker='o', s=35, facecolors='none')
            for j in np.arange(node_lens.shape[0]):
                ax.annotate('', xytext=(x_index[j]-barwidth, node_lens[j, i]), xy=(x_index[j]+barwidth, node_time[j, i]), arrowprops=dict(arrowstyle="->"))
        line1 = ax.errorbar(
            x_index, node_accuracy_conf[:, 2], color=colordict['darkblue'], marker='s', ms=6, markerfacecolor='none')
        ax.fill_between(
            x_index, node_accuracy_conf[:, 1], node_accuracy_conf[:, 3], color=colordict['darkblue'], alpha=0.2)
        # box1 = ax.boxplot(np.transpose(node_lens[:, 1:]), positions=np.transpose(node_lens[:, 0]) - barwidth, vert=True, widths=barwidth, showfliers=False, showmeans=False, patch_artist=True,
        #                   boxprops=dict(
        #     color='black', facecolor=colordict['lightblue'], lw=1),
        #     medianprops=dict(color='black'),
        #     capprops=dict(color='black'),
        #     whiskerprops=dict(color='black'),
        #     flierprops=dict(
        #     color=colordict['lightblue'], markeredgecolor=colordict['lightblue'], ms=4),
        #     meanprops=dict(markerfacecolor='black', markeredgecolor='black'))
        # box2 = ax.boxplot(np.transpose(node_time[:, 1:]), positions=np.transpose(node_time[:, 0]) + barwidth, notch=True, vert=True, widths=barwidth, showfliers=False, showmeans=False, patch_artist=True,
        #                   boxprops=dict(
        #     color='black', facecolor=colordict['midblue'], lw=1, hatch='\\'),
        #     medianprops=dict(color='black'),
        #     capprops=dict(color='black'),
        #     whiskerprops=dict(color='black'),
        #     flierprops=dict(
        #     color=colordict['midblue'], markeredgecolor=colordict['midblue'], ms=4),
        #     meanprops=dict(markerfacecolor='black', markeredgecolor='black'))
        ax.set_xlabel(r'Index of network nodes')
        ax.set_ylabel(r'Percent in total cost ($\%$)')
        # ax.set_yticks(np.arange(0, 101, 20))
        # ax.legend([box1["boxes"][0], sct2, line1], [
        #     r'Subset data size $l_k$', r'Computing time $t_c$', r'Separation precision SDR'], loc='upper left', ncol=1)
        ax.legend([sct1, sct2, line1], [
            r'Subset data size $l_k$', r'Computing time $t_c$', r'Separation precision SDR'], loc='upper left', ncol=1)
        plt.xticks(x_index, ['1', '2', '3', '4', '5', '6', '7', 'RA'])
        plt.savefig('./emulator/measurement/plot/nodes_performance_details.pdf',
                    dpi=600, bbox_inches='tight')

        fig = plt.figure(figsize=(fig_width, fig_width / 1.618 * 2))
        ax = fig.add_subplot(2, 1, 1)
        ax.xaxis.grid(True, linestyle='--', which='major',
                      color='lightgrey', alpha=0.5, linewidth=0.2)
        ax.yaxis.grid(True, linestyle='--', which='major',
                      color='lightgrey', alpha=0.5, linewidth=0.2)
        x_index = np.arange(nodes + 1)
        for i in range(1, node_lens.shape[1]-1):
            sct1 = ax.scatter(
                x_index-barwidth, node_lens[:, i], color=colordict['lightblue'], marker='X', s=25, facecolors='none')
            sct2 = ax.scatter(
                x_index+barwidth, node_time[:, i], color=colordict['midblue'], marker='p', s=20, facecolors='none')
        line1 = ax.errorbar(
            x_index, node_accuracy_conf[:, 2], color=colordict['darkblue'], marker='s', ms=4, markerfacecolor='none')
        ax.fill_between(
            x_index, node_accuracy_conf[:, 1], node_accuracy_conf[:, 3], color=colordict['darkblue'], alpha=0.2)
        # line1 =ax.errorbar(x_index, node_lens_conf[:, 2], color=colordict['darkblue'])
        # line_1_fill = ax.fill_between(x_index, node_lens_conf[:, 1], node_lens_conf[:, 3], color=colordict['darkblue'], alpha=0.2)
        # box = ax.boxplot(np.transpose(node_lens[:, 1:]), vert=True, widths=barwidth, showfliers=True, showmeans=False, patch_artist=True,
        #                    boxprops=dict(
        #                        color='black', facecolor=colordict['darkblue'], lw=1),
        #                    medianprops=dict(color='black'),
        #                    capprops=dict(color='black'),
        #                    whiskerprops=dict(color='black'),
        #                    flierprops=dict(
        #                        color=colordict['darkblue'], markeredgecolor=colordict['darkblue'], ms=4),
        #                    meanprops=dict(markerfacecolor='black', markeredgecolor='black'))
        # line1, = ax.plot(x_index, len_subset/np.max(len_subset)*100, color=colordict['darkblue'], lw=1.2, ls='-',
        #                  marker='o', ms=4, markerfacecolor='none')
        # line2, = ax.plot(x_index, process_latency/sum(process_latency)*100,
        #                  color=colordict['lightblue'], lw=1.2, ls='--', marker='s', ms=4, markerfacecolor='none')
        # line3, = ax.plot(x_index, separation_accuracy /
        #                  separation_accuracy[-1]*100, color=colordict['midblue'], lw=1.2, ls='-.', marker='p', ms=4, markerfacecolor='none')

        ax.set_xlabel(r'Index of network nodes')
        ax.set_ylabel(r'Percent in total cost ($\%$)')
        # ax.set_yticks(np.arange(0, 101, 20))
        ax.legend([sct1, sct2, line1], [
            r'Subset data size $lX$', r'Computing time $t_c$', r'Separation precision SDR'], loc='upper left', ncol=1)
        plt.xticks(x_index, ['1', '2', '3', '4', '5', '6', '7', 'RA'])
        # plt.savefig('./emulator/measurement/plot/nodes_performance_details.pdf',
        #             dpi=600, bbox_inches='tight')

        stoppage_k = np.array([[50, 50, 50, 43, 37, 26, 14,  0],
                               [0,  0,  0,  7,  13, 24, 32, 24]])
        # fig = plt.figure(figsize=(fig_width, fig_width / 1.618))
        ax_2 = fig.add_subplot(2, 1, 2)
        ax_2.xaxis.grid(True, linestyle='--', which='major',
                        color='lightgrey', alpha=0.5, linewidth=0.2)
        ax_2.yaxis.grid(True, linestyle='--', which='major',
                        color='lightgrey', alpha=0.5, linewidth=0.2)
        x_index = np.arange(0, len(stoppage_k[0, :]))
        bar1 = ax_2.bar(x_index, stoppage_k[0, :], barwidth, fill=True,
                        color=colordict['compute_forward'], edgecolor='#FFFFFF', ecolor='#555555', hatch='\\', label='Greedy Stoppage')
        bar2 = ax_2.bar(x_index, stoppage_k[1, :], barwidth, bottom=stoppage_k[0, :], fill=True,
                        color=colordict['store_forward'], edgecolor='#FFFFFF', ecolor='#555555', hatch='//', label='Normal Stoppage')
        # for i in x_index:
        #     ax_2.text(i-bardistance*3, max(stoppage[i, 1], stoppage[i, 2])+5, r'$'+str(round(stoppage[i, 1]/stoppage[i, 3], 4)*100)+r'\%$', rotation=25)
        ax_2.set_xlabel(r'Index of network nodes')
        ax_2.set_ylabel(r'Number of triggered stoppage')
        ax_2.set_xlim([-0.5, 7.5])
        ax_2.set_ylim([0, 65])
        # ax_2.set_xticks(range(len(number_node)))
        ax_2.set_yticks(np.arange(0, 61, 10))
        plt.xticks(x_index, ['1', '2', '3', '4', '5', '6', '7', 'RA'])
        ax_2.legend(handles=[bar1, bar2], loc='upper right')
        plt.savefig('./emulator/measurement/plot/node_details_greedy_stoppage.pdf',
                    dpi=600, bbox_inches='tight')

    # fr = open('./emulator/MIMII/saxsNew.pkl', 'rb')
    # saxs = pickle.load(fr)
    # ss, aa, xx = saxs
    # s = ss[number_test]
    # x = xx[number_test]

    # path_server_csv = './emulator/measurement/'+str(nodes)+'s/server_cf.csv'
    # process_latency = np.loadtxt(path_server_csv, delimiter=',', usecols=[1])[
    #     number_test] * 1000
    # w = np.array(json.loads(measure_read_csv_to_2dlist(
    #     path_server_csv)[number_test][3].replace('|', ',')))
    # hat_s = np.dot(w, x)
    # separation_accuracy = pybss_tb.bss_evaluation(s, hat_s, type='sdr')

    # for node in range(nodes-1, -1, -1):
    #     path_vnf_csv = './emulator/measurement/' + \
    #         str(nodes)+'s/vnf' + str(node)+'-s' + str(node)+'.csv'
    #     vnf_latency = np.loadtxt(path_vnf_csv, delimiter=',', usecols=[3])[
    #         number_test] * 1000
    #     process_latency = np.row_stack((vnf_latency, process_latency))
    #     w = np.array(json.loads(measure_read_csv_to_2dlist(
    #         path_vnf_csv)[number_test][5].replace('|', ',')))
    #     hat_s = np.dot(w, x)
    #     vnf_accuracy = pybss_tb.bss_evaluation(s, hat_s, type='sdr')
    #     separation_accuracy = np.row_stack((vnf_accuracy, separation_accuracy))

    # path_details_csv = './emulator/measurement/results/pICA_' + str(nodes)+'details.csv'
    # len_subset = np.loadtxt(path_details_csv, delimiter=',', usecols=np.arange(
    #     1, len(separation_accuracy)+1, 1))

    # len_subset = len_subset[0, :]
    # process_latency = process_latency[:, 0]
    # separation_accuracy = separation_accuracy[:, 0]

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
    #         'compute_forward': 'p',
    #         'store_forward': 'o',
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
    #     plt.savefig('./emulator/measurement/plot/nodes_performance_emu.pdf',
    #                 dpi=600, bbox_inches='tight')
