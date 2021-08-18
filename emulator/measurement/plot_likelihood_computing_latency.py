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


def get_cdf(data):
    counts, bin_edges = np.histogram(data, bins=len(data), density=True)
    dx = bin_edges[1] - bin_edges[0]
    cdf = np.cumsum(counts) * dx
    # label = np.sort(data)
    return bin_edges[1:], cdf


if __name__ == '__main__':
    number_node = [0, 1, 4, 7]
    number_test = 50

    computing_server_latency_cf = np.zeros(number_test)
    computing_server_latency_cf_hbh = np.zeros(number_test)
    computing_server_latency_sf = np.zeros(number_test)
    computing_latency_cf = np.zeros(number_test)
    computing_latency_cf_hbh = np.zeros(number_test)
    computing_latency_sf = np.zeros(number_test)
    for node in number_node:
        path_server_cf = './emulator/measurement/results_v4/' + \
            str(node)+'s/server_cf.csv'
        path_server_cf_hbh = './emulator/measurement/results_v4/' + \
            str(node)+'s/server_cf_hbh.csv'
        path_server_sf = './emulator/measurement/results_v4/' + \
            str(node)+'s/server_sf.csv'

        server_cf = np.loadtxt(
            path_server_cf, delimiter=',', usecols=[5])
        server_cf_hbh = np.loadtxt(
            path_server_cf_hbh, delimiter=',', usecols=[5])
        server_sf = np.loadtxt(
            path_server_sf, delimiter=',', usecols=[5])

        computing_server_latency_cf = np.row_stack(
            (computing_server_latency_cf, server_cf))
        computing_server_latency_cf_hbh = np.row_stack(
            (computing_server_latency_cf_hbh, server_cf_hbh))
        computing_server_latency_sf = np.row_stack(
            (computing_server_latency_sf, server_sf))

        if node > 0:
            computing_vnf_latency_cf = np.zeros(number_test)
            computing_vnf_latency_hbh = np.zeros(number_test)
            for vnf in range(0, node):
                path_vnf_cf = './emulator/measurement/results_v4/' + \
                    str(node)+'s/vnf' + str(vnf) + \
                    '-s' + str(vnf) + '_cf.csv'
                path_vnf_cf_hbh = './emulator/measurement/results_v4/' + \
                    str(node)+'s/vnf' + str(vnf) + \
                    '-s' + str(vnf) + '_cf_hbh.csv'
                computing_vnf_latency_cf = computing_vnf_latency_cf + \
                    np.loadtxt(path_vnf_cf, delimiter=',', usecols=[7])
                computing_vnf_latency_hbh = computing_vnf_latency_hbh + \
                    np.loadtxt(path_vnf_cf_hbh, delimiter=',', usecols=[7])
        else:
            computing_vnf_latency_cf = np.zeros(number_test)
            computing_vnf_latency_hbh = np.zeros(number_test)

        server_cf = server_cf + computing_vnf_latency_cf
        server_cf_hbh = server_cf_hbh + computing_vnf_latency_hbh
        computing_latency_cf = np.row_stack(
            (computing_latency_cf, server_cf))
        computing_latency_cf_hbh = np.row_stack(
            (computing_latency_cf_hbh, server_cf_hbh))
        computing_latency_sf = np.row_stack(
            (computing_latency_sf, server_sf))

    computing_server_latency_cf = computing_server_latency_cf[1:, :]
    computing_server_latency_cf_hbh = computing_server_latency_cf_hbh[1:, :]
    computing_server_latency_sf = computing_server_latency_sf[1:, :]
    computing_latency_cf = computing_latency_cf[1:, :]
    computing_latency_cf_hbh = computing_latency_cf_hbh[1:, :]
    computing_latency_sf = computing_latency_sf[1:, :]

    with plt.style.context(['science', 'ieee']):
        fig_width = 6.5
        barwidth = 0.4
        bardistance = barwidth * 1.7
        colordict = {
            'compute_forward': '#0077BB',
            'store_forward': '#DDAA33',
            'store_forward_ia': '#009988',
            'orange': '#EE7733',
            'red': '#993C00',
            'blue': '#3340AD'
        }
        markerdict = {
            'compute_forward': 'o',
            'store_forward': 'v',
            'store_forward_ia': 's'
        }
        colorlist = ['#DDAA33', '#7ACFE5', '#3F9ABF',
                     '#024B7A',  '#0077BB', '#009988']
        markerlist = ['o', 'v', '^', '>', 'p', 's']

        plt.rcParams.update({'font.size': 11})

        fig = plt.figure(figsize=(fig_width, fig_width / 1.618))
        # ax = fig.add_subplot(1, 1, 1)
        spec = gridspec.GridSpec(ncols=1, nrows=2, height_ratios=[1, 6])
        ax_1 = fig.add_subplot(spec[0])
        ax_1.yaxis.grid(True, linestyle='--', which='major',
                        color='lightgrey', alpha=0.5, linewidth=0.2)
        box = ax_1.boxplot(computing_latency_sf[0, :], positions=np.arange(1), vert=False, widths=barwidth, showfliers=True, showmeans=False, patch_artist=True,
                           boxprops=dict(
                               color='black', facecolor=colorlist[0], lw=1),
                           medianprops=dict(color='black'),
                           capprops=dict(color='black'),
                           whiskerprops=dict(color='black'),
                           flierprops=dict(
                               color=colorlist[0], markeredgecolor=colorlist[0], ms=4),
                           meanprops=dict(markerfacecolor='black', markeredgecolor='black'))
        for box_id in range(1, len(number_node)):
            box1 = ax_1.boxplot(computing_latency_cf[box_id, :], positions=np.arange(1) - bardistance*box_id, vert=False, widths=barwidth, showfliers=True, showmeans=False,
                                patch_artist=True,
                                boxprops=dict(
                                    color='black', facecolor=colorlist[box_id], lw=1),
                                medianprops=dict(color='black'),
                                capprops=dict(color='black'),
                                whiskerprops=dict(color='black'),
                                flierprops=dict(
                                    color=colorlist[box_id], markeredgecolor=colorlist[box_id], ms=4),
                                meanprops=dict(markerfacecolor='black', markeredgecolor='black'))
            # box2 = ax_1.boxplot(computing_latency_cf_hbh[box_id, :], positions=np.arange(1) - bardistance*(box_id+len(number_node)-1), vert=False, widths=barwidth,
            #                     showfliers=False, showmeans=False,
            #                     patch_artist=True, boxprops=dict(facecolor=colorlist[box_id], lw=1, hatch='\\'),
            #                     medianprops=dict(color='black'),
            #                     meanprops=dict(markerfacecolor='black', markeredgecolor='black', markersize=3, marker=markerlist[box_id]))
        ax_1.set_xticks(np.arange(1, 8, 1))
        ax_1.set_xlim([0.75, 7.25])
        ax_1.axes.xaxis.set_visible(True)
        ax_1.axes.yaxis.set_visible(False)

        ax_2 = fig.add_subplot(spec[1])
        ax_2.yaxis.grid(True, linestyle='--', which='major',
                        color='lightgrey', alpha=0.5, linewidth=0.2)
        bin_store, cdf_store = get_cdf(computing_latency_sf[0, :])
        line = ax_2.plot(
            bin_store, cdf_store, color=colorlist[0], lw=1.2, ls='-.', marker=markerlist[0], ms=4, markerfacecolor='none', label=r'FastICA $k=0$')
        for line_id in range(1, len(number_node)):
            bin_compute, cdf_compute = get_cdf(
                computing_latency_cf[line_id, :])
            bin_compute_hbh, cdf_compute_us = get_cdf(
                computing_latency_cf_hbh[line_id, :])
            line1 = ax_2.plot(bin_compute, cdf_compute, color=colorlist[line_id], lw=1.2, ls='-',
                              marker=markerlist[line_id], ms=4, markerfacecolor='none', label=r'pICA $k=$ '+str(number_node[line_id]))
            # line1 = ax_2.plot(bin_compute_hbh, cdf_compute_us, color=colorlist[line_id], lw=1.2, ls=':',
            #                   marker=markerlist[line_id], ms=4, markerfacecolor='none', label=r'pICA HbH $k=$ '+str(number_node[line_id]))
        ax_2.set_xlabel(r'Computing loads $t_c$ of the network ($s$)')
        ax_2.set_ylabel(r'Likelihood of occurrence')
        ax_2.set_xticks(np.arange(1, 8, 1))
        ax_2.set_xlim([0.75, 7.25])
        ax_2.set_yticks(np.arange(0, 1.1, 0.2))

        plt.legend(loc='lower right', ncol=1)
        fig.subplots_adjust(hspace=0.02)
        plt.savefig('./emulator/measurement/plot/computing_likelihood.pdf',
                    dpi=600, bbox_inches='tight')

        fig = plt.figure(figsize=(fig_width, fig_width / 1.618))
        # ax = fig.add_subplot(1, 1, 1)
        spec = gridspec.GridSpec(ncols=1, nrows=2, height_ratios=[1, 6])
        ax_1 = fig.add_subplot(spec[0])
        ax_1.yaxis.grid(True, linestyle='--', which='major',
                        color='lightgrey', alpha=0.5, linewidth=0.2)
        box = ax_1.boxplot(computing_server_latency_sf[0, :], positions=np.arange(1), vert=False, widths=barwidth, showfliers=True, showmeans=False, patch_artist=True,
                           boxprops=dict(
                               color='black', facecolor=colorlist[0], lw=1),
                           medianprops=dict(color='black'),
                           capprops=dict(color='black'),
                           whiskerprops=dict(color='black'),
                           flierprops=dict(
                               color=colorlist[0], markeredgecolor=colorlist[0], ms=4),
                           meanprops=dict(markerfacecolor='black', markeredgecolor='black'))
        for box_id in range(1, len(number_node)):
            box1 = ax_1.boxplot(computing_server_latency_cf[box_id, :], positions=np.arange(1) - bardistance*box_id, vert=False, widths=barwidth, showfliers=True, showmeans=False, patch_artist=True,
                                boxprops=dict(
                                    color='black', facecolor=colorlist[box_id], lw=1),
                                medianprops=dict(color='black'),
                                capprops=dict(color='black'),
                                whiskerprops=dict(color='black'),
                                flierprops=dict(
                                    color=colorlist[box_id], markeredgecolor=colorlist[box_id], ms=4),
                                meanprops=dict(markerfacecolor='black', markeredgecolor='black'))
            # box2 = ax_1.boxplot(computing_server_latency_cf_hbh[box_id, :], positions=np.arange(1) - bardistance*(box_id+len(number_node)-1), vert=False, widths=barwidth,
            #                     showfliers=False, showmeans=False,
            #                     patch_artist=True, boxprops=dict(facecolor=colorlist[box_id], lw=1, hatch='\\'),
            #                     medianprops=dict(color='black'),
            #                     meanprops=dict(markerfacecolor='black', markeredgecolor='black', markersize=3, marker=markerlist[box_id]))
        ax_1.set_xticks(np.arange(0, 8, 1))
        ax_1.set_xlim([-0.25, 7.25])
        ax_1.axes.xaxis.set_visible(True)
        ax_1.axes.yaxis.set_visible(False)

        ax_2 = fig.add_subplot(spec[1])
        ax_2.yaxis.grid(True, linestyle='--', which='major',
                        color='lightgrey', alpha=0.5, linewidth=0.2)
        bin_store, cdf_store = get_cdf(computing_server_latency_sf[0, :])
        line = ax_2.plot(
            bin_store, cdf_store, color=colorlist[0], lw=1.2, ls='-.', marker=markerlist[0], ms=4, markerfacecolor='none', label=r'FastICA $k=0$')
        for line_id in range(1, len(number_node)):
            bin_compute, cdf_compute = get_cdf(
                computing_server_latency_cf[line_id, :])
            bin_compute_hbh, cdf_compute_us = get_cdf(
                computing_server_latency_cf_hbh[line_id, :])
            line1 = ax_2.plot(bin_compute, cdf_compute, color=colorlist[line_id], lw=1.2, ls='-',
                              marker=markerlist[line_id], ms=4, markerfacecolor='none', label=r'pICA $k=$ '+str(number_node[line_id]))
            # line1 = ax_2.plot(bin_compute_hbh, cdf_compute_us, color=colorlist[line_id], lw=1.2, ls=':',
            #                   marker=markerlist[line_id], ms=3, label=r'pICA HbH $k=$ '+str(number_node[line_id]))
        ax_2.set_xlabel(r'Residual computing loads $t_c$ on RA ($s$)')
        ax_2.set_ylabel(r'Likelihood of occurrence')
        ax_2.set_xticks(np.arange(0, 8, 1))
        ax_2.set_xlim([-0.25, 7.25])
        ax_2.set_yticks(np.arange(0, 1.1, 0.2))

        plt.legend(loc='lower right', ncol=1)
        fig.subplots_adjust(hspace=0.02)
        plt.savefig('./emulator/measurement/plot/computing_server_likelihood.pdf',
                    dpi=600, bbox_inches='tight')
