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
    number_node = [0, 3, 7]

    number_test = 50

    service_latency_cf = np.zeros(number_test)
    service_latency_cf_us = np.zeros(number_test)
    service_latency_sf = np.zeros(number_test)
    for node in number_node:
        path_client_compute_client = './emulator/measurement/results_v2/' + \
            str(node)+'s/client_cf.csv'
        path_client_compute_client_us = './emulator/measurement/results_v2/' + \
            str(node)+'s/client_cf_us.csv'
        path_client_store_client = './emulator/measurement/results_v2/' + \
            str(node)+'s/client_sf.csv'

        client_compute_forward = np.loadtxt(
            path_client_compute_client, delimiter=',', usecols=[5, 7])
        client_compute_forward_us = np.loadtxt(
            path_client_compute_client_us, delimiter=',', usecols=[5, 7])
        client_store_forward = np.loadtxt(
            path_client_store_client, delimiter=',', usecols=[5, 7])

        service_latency_cf = np.row_stack(
            (service_latency_cf, client_compute_forward[:, 1]))
        service_latency_cf_us = np.row_stack(
            (service_latency_cf_us, client_compute_forward_us[:, 1]))
        service_latency_sf = np.row_stack(
            (service_latency_sf, client_store_forward[:, 1]))

    service_latency_cf = service_latency_cf[1:, :]
    service_latency_cf_us = service_latency_cf_us[1:, :]
    service_latency_sf = service_latency_sf[1:, :]

    with plt.style.context(['science', 'ieee']):
        fig_width = 6.5
        barwidth = 0.2
        bardistance = 0.3
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
            'compute_forward': 'o',
            'store_forward': 'v',
            'store_forward_ia': 's'
        }
        colorlist = ['#DDAA33', '#33BBEE', '#009988', '#6699CC', '#0077BB']
        markerlist = ['s', 'o', 'v', 'p']

        plt.rcParams.update({'font.size': 11})

        fig = plt.figure(figsize=(fig_width, fig_width / 1.5))
        # ax = fig.add_subplot(1, 1, 1)
        spec = gridspec.GridSpec(ncols=1, nrows=2, height_ratios=[1, 5])
        ax_1 = fig.add_subplot(spec[0])
        ax_1.yaxis.grid(True, linestyle='--', which='major',
                        color='lightgrey', alpha=0.5, linewidth=0.2)
        box = ax_1.boxplot(service_latency_sf[0, :], positions=np.arange(1), vert=False, widths=barwidth,
                           showfliers=False, showmeans=False,
                           patch_artist=True, boxprops=dict(facecolor=colorlist[0], lw=1),
                           medianprops=dict(color='black'),
                           meanprops=dict(markerfacecolor='black', markeredgecolor='black', markersize=3, marker=markerlist[0]))
        for box_id in range(1, len(number_node)):
            box1 = ax_1.boxplot(service_latency_cf[box_id, :], positions=np.arange(1) - bardistance*box_id, vert=False, widths=barwidth,
                                showfliers=False, showmeans=False,
                                patch_artist=True, boxprops=dict(facecolor=colorlist[box_id], lw=1),
                                medianprops=dict(color='black'),
                                meanprops=dict(markerfacecolor='black', markeredgecolor='black', markersize=3, marker=markerlist[box_id]))
            box2 = ax_1.boxplot(service_latency_cf_us[box_id, :], positions=np.arange(1) - bardistance*(box_id+len(number_node)-1), vert=False, widths=barwidth,
                                showfliers=False, showmeans=False,
                                patch_artist=True, boxprops=dict(facecolor=colorlist[box_id], lw=1, hatch='\\'),
                                medianprops=dict(color='black'),
                                meanprops=dict(markerfacecolor='black', markeredgecolor='black', markersize=3, marker=markerlist[box_id]))
        # ax_1.set_xticks(np.arange(6.5, 14.1, 1))
        ax_1.axes.xaxis.set_visible(False)
        ax_1.axes.yaxis.set_visible(False)

        ax_2 = fig.add_subplot(spec[1])
        ax_2.yaxis.grid(True, linestyle='--', which='major',
                        color='lightgrey', alpha=0.5, linewidth=0.2)
        bin_store, cdf_store = get_cdf(service_latency_sf[0, :])
        line = ax_2.plot(
            bin_store, cdf_store, color=colorlist[0], lw=1.2, ls='-.', marker=markerlist[0], ms=3, label='FastICA '+r'$k=0$')
        for line_id in range(1, len(number_node)):
            bin_compute, cdf_compute = get_cdf(service_latency_cf[line_id, :])
            bin_compute_us, cdf_compute_us = get_cdf(
                service_latency_cf_us[line_id, :])
            line1 = ax_2.plot(bin_compute, cdf_compute, color=colorlist[line_id], lw=1.2, ls='-',
                              marker=markerlist[line_id], ms=3, label=r'pICA with ks $k=$ '+str(number_node[line_id]))
            line1 = ax_2.plot(bin_compute_us, cdf_compute_us, color=colorlist[line_id], lw=1.2, ls='--',
                              marker=markerlist[line_id], ms=3, label=r'pICA with us $k=$ '+str(number_node[line_id]))
        ax_2.set_xlabel(r'Service Latency ($s$)')
        ax_2.set_ylabel(r'Likelihood of occurrence')
        # ax_2.set_xticks(np.arange(6.5, 14.1, 1))
        ax_2.set_yticks(np.arange(0, 1.1, 0.2))

        plt.legend()
        fig.subplots_adjust(hspace=0.02)
        plt.savefig('./emulator/measurement/service_likelyhood.pdf',
                    dpi=600, bbox_inches='tight')
