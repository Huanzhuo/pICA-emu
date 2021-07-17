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
    service_latency_sf = np.zeros(number_test)
    transmission_latency_cf = np.zeros(number_test)
    transmission_latency_sf = np.zeros(number_test)
    process_server_latency_cf = np.zeros(number_test)
    process_server_latency_sf = np.zeros(number_test)
    for node in number_node:
        path_client_compute_client = './emulator/measurement/' + \
            str(node)+'/client_cf.csv'
        path_client_store_client = './emulator/measurement/' + \
            str(node)+'/client_sf.csv'
        path_server_compute_client = './emulator/measurement/' + \
            str(node)+'/client_cf.csv'
        path_server_store_client = './emulator/measurement/' + \
            str(node)+'/client_sf.csv'

        client_compute_forward = np.loadtxt(
            path_client_compute_client, delimiter=',', usecols=[3, 5])
        client_store_forward = np.loadtxt(
            path_client_store_client, delimiter=',', usecols=[3, 5])
        server_compute_forward = np.loadtxt(
            path_server_compute_client, delimiter=',', usecols=[1])
        server_store_forward = np.loadtxt(
            path_server_store_client, delimiter=',', usecols=[1])

        service_latency_cf = np.row_stack(
            (service_latency_cf, client_compute_forward[:, 1]))
        service_latency_sf = np.row_stack(
            (service_latency_sf, client_store_forward[:, 1]))
        transmission_latency_cf = np.row_stack(
            (transmission_latency_cf, client_compute_forward[:, 0]))
        transmission_latency_sf = np.row_stack(
            (transmission_latency_sf, client_store_forward[:, 0]))
        process_server_latency_cf = np.row_stack(
            (process_server_latency_cf, server_compute_forward))
        process_server_latency_sf = np.row_stack(
            (process_server_latency_sf, server_store_forward))

    service_latency_cf = service_latency_cf[1:, :] * 1000
    service_latency_sf = service_latency_sf[1:, :] * 1000
    transmission_latency_cf = transmission_latency_cf[1:, :] * 1000
    transmission_latency_sf = transmission_latency_sf[1:, :] * 1000
    process_server_latency_cf = process_server_latency_cf[1:, :] * 1000
    process_server_latency_sf = process_server_latency_sf[1:, :] * 1000

    ts_cf_conf = get_conf_interval(number_node, service_latency_cf, conf_rate)
    ts_sf_conf = get_conf_interval(number_node, service_latency_sf, conf_rate)
    tt_cf_conf = get_conf_interval(
        number_node, transmission_latency_cf, conf_rate)
    tt_sf_conf = get_conf_interval(
        number_node, transmission_latency_sf, conf_rate)
    tp_server_cf_conf = get_conf_interval(
        number_node, process_server_latency_cf, conf_rate)
    tp_server_sf_conf = get_conf_interval(
        number_node, process_server_latency_sf, conf_rate)

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
            'compute_forward': 'o',
            'store_forward': 'v',
            'store_forward_ia': 's'
        }

        plt.rcParams.update({'font.size': 11})

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
        ax.set_xlabel(r'Number of nodes $k$')
        ax.set_ylabel(r'Service latency ($ms$)')
        # ax.set_xlim([-0.2, 4.2])
        # ax.set_yticks(np.arange(0, 151, 30))
        ax.legend([line1, line2], ['pICA',
                                   'FastICA'], loc='upper right')
        plt.xticks(range(len(number_node)), number_node)
        plt.savefig('./emulator/measurement/service_latency_all.pdf',
                    dpi=600, bbox_inches='tight')

        fig = plt.figure(figsize=(fig_width, fig_width / 1.618))
        ax = fig.add_subplot(1, 1, 1)
        ax.yaxis.grid(True, linestyle='--', which='major',
                      color='lightgrey', alpha=0.5, linewidth=0.2)
        x_index = np.arange(len(number_node))
        line1 = ax.errorbar(
            x_index, tt_cf_conf[:, 2], color=colordict['compute_forward'], lw=1, ls='-', marker=markerdict['compute_forward'], ms=5)
        line1_fill = ax.fill_between(x_index, tt_cf_conf[:, 1],
                                     tt_cf_conf[:, 3], color=colordict['compute_forward'], alpha=0.2)
        line2 = ax.errorbar(
            x_index, tt_sf_conf[:, 2], color=colordict['store_forward'], lw=1, ls='-', marker=markerdict['store_forward'], ms=5)
        line2_fill = ax.fill_between(x_index, tt_sf_conf[:, 1],
                                     tt_sf_conf[:, 3], color=colordict['store_forward'], alpha=0.2)
        ax.set_xlabel(r'Number of nodes $k$')
        ax.set_ylabel(r'Transmission latency ($ms$)')
        # ax.set_xlim([-0.2, 4.2])
        # ax.set_yticks(np.arange(0, 151, 30))
        ax.legend([line1, line2], ['pICA',
                                   'FastICA'], loc='upper right')
        plt.xticks(range(len(number_node)), number_node)
        plt.savefig('./emulator/measurement/transmission_latency_all.pdf',
                    dpi=600, bbox_inches='tight')

        fig = plt.figure(figsize=(fig_width, fig_width / 1.618))
        ax = fig.add_subplot(1, 1, 1)
        ax.yaxis.grid(True, linestyle='--', which='major',
                      color='lightgrey', alpha=0.5, linewidth=0.2)
        x_index = np.arange(len(number_node))
        line1 = ax.errorbar(
            x_index, tp_server_cf_conf[:, 2], color=colordict['compute_forward'], lw=1, ls='-', marker=markerdict['compute_forward'], ms=5)
        line1_fill = ax.fill_between(x_index, tp_server_cf_conf[:, 1],
                                     tp_server_cf_conf[:, 3], color=colordict['compute_forward'], alpha=0.2)
        line2 = ax.errorbar(
            x_index, tp_server_sf_conf[:, 2], color=colordict['store_forward'], lw=1, ls='-', marker=markerdict['store_forward'], ms=5)
        line2_fill = ax.fill_between(x_index, tp_server_sf_conf[:, 1],
                                     tp_server_sf_conf[:, 3], color=colordict['store_forward'], alpha=0.2)
        ax.set_xlabel(r'Number of nodes $k$')
        ax.set_ylabel(r'Process latency on the Server ($ms$)')
        # ax.set_xlim([-0.2, 4.2])
        # ax.set_yticks(np.arange(0, 151, 30))
        ax.legend([line1, line2], ['pICA',
                                   'FastICA'], loc='upper right')
        plt.xticks(range(len(number_node)), number_node)
        plt.savefig('./emulator/measurement/process_latency_server.pdf',
                    dpi=600, bbox_inches='tight')
