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

    service_latency_cf = np.zeros(number_test)
    service_latency_cf_hbh = np.zeros(number_test)
    service_latency_sf = np.zeros(number_test)

    for node in number_node:
        path_client_cf = './emulator/measurement/results_v4/' + \
            str(node)+'s/client_cf.csv'
        path_client_cf_hbh = './emulator/measurement/results_v4/' + \
            str(node)+'s/client_cf_hbh.csv'
        path_client_sf = './emulator/measurement/results_v4/' + \
            str(node)+'s/client_sf.csv'

        client_cf = np.loadtxt(
            path_client_cf, delimiter=',', usecols=[5, 7])
        client_cf_hbh = np.loadtxt(
            path_client_cf_hbh, delimiter=',', usecols=[5, 7])
        client_sf = np.loadtxt(
            path_client_sf, delimiter=',', usecols=[5, 7])

        service_latency_cf = np.row_stack(
            (service_latency_cf, client_cf[:, 1]))
        service_latency_cf_hbh = np.row_stack(
            (service_latency_cf_hbh, client_cf_hbh[:, 1]))
        service_latency_sf = np.row_stack(
            (service_latency_sf, client_sf[:, 1]))

    service_latency_cf = service_latency_cf[1:, :]
    service_latency_cf_hbh = service_latency_cf_hbh[1:, :]
    service_latency_sf = service_latency_sf[1:, :]

    ts_cf_conf = get_conf_interval(number_node, service_latency_cf, conf_rate)
    ts_cf_hbh_conf = get_conf_interval(
        number_node, service_latency_cf_hbh, conf_rate)
    ts_sf_conf = get_conf_interval(number_node, service_latency_sf, conf_rate)

    # codes for plot figures
    with plt.style.context(['science', 'ieee']):
        fig_width = 6.5
        barwidth = 0.3
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

        plt.rcParams.update({'font.size': 10})

        fig = plt.figure(figsize=(fig_width, fig_width / 1.618))
        ax = fig.add_subplot(1, 1, 1)
        ax.yaxis.grid(True, linestyle='--', which='major',
                      color='lightgrey', alpha=0.5, linewidth=0.2)
        x_index = np.arange(len(number_node))
        line1 = ax.errorbar(
            x_index, ts_cf_conf[:, 2], color=colordict['compute_forward'], lw=1, ls='-', marker=markerdict['compute_forward'], ms=5)
        line1_fill = ax.fill_between(x_index, ts_cf_conf[:, 1],
                                     ts_cf_conf[:, 3], color=colordict['compute_forward'], alpha=0.2)
        line2 = ax.errorbar(
            x_index, ts_sf_conf[:, 2], color=colordict['store_forward'], lw=1, ls='-', marker=markerdict['store_forward'], ms=5)
        line2_fill = ax.fill_between(x_index, ts_sf_conf[:, 1],
                                     ts_sf_conf[:, 3], color=colordict['store_forward'], alpha=0.2)
        line3 = ax.errorbar(
            x_index, ts_cf_hbh_conf[:, 2], color=colordict['store_forward_ia'], lw=1, ls='-', marker=markerdict['store_forward_ia'], ms=5)
        line3_fill = ax.fill_between(x_index, ts_cf_hbh_conf[:, 1],
                                     ts_cf_hbh_conf[:, 3], color=colordict['store_forward_ia'], alpha=0.2)
        ax.set_xlabel(r'Number of nodes $k$')
        ax.set_ylabel(r'Service latency ($s$)')
        # ax.set_xlim([-0.2, 4.2])
        ax.set_yticks(np.arange(0, 18.1, 3))
        ax.legend([line1, line2, line3], ['pICA',
                                          'FastICA', 'pICA hbh'], loc='upper left')
        plt.xticks(range(len(number_node)), number_node)
        plt.savefig('./emulator/measurement/plot/service_latency_emu.pdf',
                    dpi=600, bbox_inches='tight')