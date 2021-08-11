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
    transmission_latency_cf = np.zeros(number_test)
    computing_vnf_latency_hbh = np.zeros(number_test)
    transmission_latency_cf_hbh = np.zeros(number_test)
    transmission_latency_sf = np.zeros(number_test)
    computing_server_latency_cf = np.zeros(number_test)
    computing_server_latency_cf_hbh = np.zeros(number_test)
    computing_server_latency_sf = np.zeros(number_test)
    for node in number_node:
        path_client_cf = './emulator/measurement/results_v4/' + \
            str(node)+'s/client_cf.csv'
        path_client_cf_hbh = './emulator/measurement/results_v4/' + \
            str(node)+'s/client_cf_hbh.csv'
        path_client_sf = './emulator/measurement/results_v4/' + \
            str(node)+'s/client_sf.csv'
        path_server_cf = './emulator/measurement/results_v4/' + \
            str(node)+'s/server_cf.csv'
        path_server_cf_hbh = './emulator/measurement/results_v4/' + \
            str(node)+'s/server_cf_hbh.csv'
        path_server_sf = './emulator/measurement/results_v4/' + \
            str(node)+'s/server_sf.csv'

        client_cf = np.loadtxt(
            path_client_cf, delimiter=',', usecols=[5, 7])
        client_cf_hbh = np.loadtxt(
            path_client_cf_hbh, delimiter=',', usecols=[5, 7])
        client_sf = np.loadtxt(
            path_client_sf, delimiter=',', usecols=[5, 7])
        server_cf = np.loadtxt(
            path_server_cf, delimiter=',', usecols=[5])
        server_cf_hbh = np.loadtxt(
            path_server_cf_hbh, delimiter=',', usecols=[5])
        server_sf = np.loadtxt(
            path_server_sf, delimiter=',', usecols=[5])

        service_latency_cf = np.row_stack(
            (service_latency_cf, client_cf[:, 1]))
        service_latency_cf_hbh = np.row_stack(
            (service_latency_cf_hbh, client_cf_hbh[:, 1]))
        service_latency_sf = np.row_stack(
            (service_latency_sf, client_sf[:, 1]))
        transmission_latency_cf = np.row_stack(
            (transmission_latency_cf, client_cf[:, 0]))
        transmission_latency_cf_hbh = np.row_stack(
            (transmission_latency_cf_hbh, client_cf_hbh[:, 0]))
        transmission_latency_sf = np.row_stack(
            (transmission_latency_sf, client_sf[:, 0]))
        computing_server_latency_cf = np.row_stack(
            (computing_server_latency_cf, server_cf))
        computing_server_latency_cf_hbh = np.row_stack(
            (computing_server_latency_cf_hbh, server_cf_hbh))
        computing_server_latency_sf = np.row_stack(
            (computing_server_latency_sf, server_sf))

    service_latency_cf = service_latency_cf[1:, :]
    service_latency_cf_hbh = service_latency_cf_hbh[1:, :]
    service_latency_sf = service_latency_sf[1:, :]
    transmission_latency_cf = transmission_latency_cf[1:, :]
    transmission_latency_cf_hbh = transmission_latency_cf_hbh[1:, :]
    transmission_latency_sf = transmission_latency_sf[1:, :]
    computing_server_latency_cf = computing_server_latency_cf[1:, :]
    computing_server_latency_cf_hbh = computing_server_latency_cf_hbh[1:, :]
    computing_server_latency_sf = computing_server_latency_sf[1:, :]

    ts_cf_conf = get_conf_interval(number_node, service_latency_cf, conf_rate)
    ts_cf_hbh_conf = get_conf_interval(
        number_node, service_latency_cf_hbh, conf_rate)
    ts_sf_conf = get_conf_interval(number_node, service_latency_sf, conf_rate)
    tt_cf_conf = get_conf_interval(
        number_node, transmission_latency_cf, conf_rate)
    tt_cf_hbh_conf = get_conf_interval(
        number_node, transmission_latency_cf_hbh, conf_rate)
    tt_sf_conf = get_conf_interval(
        number_node, transmission_latency_sf, conf_rate)
    tc_server_cf_conf = get_conf_interval(
        number_node, computing_server_latency_cf, conf_rate)
    tc_server_cf_hbh_conf = get_conf_interval(
        number_node, computing_server_latency_cf_hbh, conf_rate)
    tc_server_sf_conf = get_conf_interval(
        number_node, computing_server_latency_sf, conf_rate)

    # codes for plot figures
    with plt.style.context(['science', 'ieee']):
        fig_width = 6.5
        barwidth = 0.2
        bardistance = barwidth * 1.1
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

        fig = plt.figure(figsize=(fig_width, fig_width * 1.2))
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
            x_index, tt_cf_conf[:, 2], color=colordict['compute_forward'], lw=1, ls='--', marker=markerdict['compute_forward'], ms=5)
        line3_fill = ax.fill_between(x_index, tt_cf_conf[:, 1],
                                     tt_cf_conf[:, 3], color=colordict['compute_forward'], alpha=0.2)
        line4 = ax.errorbar(
            x_index, tt_sf_conf[:, 2], color=colordict['store_forward'], lw=1, ls='--', marker=markerdict['store_forward'], ms=5)
        line4_fill = ax.fill_between(x_index, tt_sf_conf[:, 1],
                                     tt_sf_conf[:, 3], color=colordict['store_forward'], alpha=0.2)
        line5 = ax.errorbar(
            x_index, tc_server_cf_conf[:, 2], color=colordict['compute_forward'], lw=1, ls='-.', marker=markerdict['compute_forward'], ms=5)
        line5_fill = ax.fill_between(x_index, tc_server_cf_conf[:, 1],
                                     tc_server_cf_conf[:, 3], color=colordict['compute_forward'], alpha=0.2)
        line6 = ax.errorbar(
            x_index, tc_server_sf_conf[:, 2], color=colordict['store_forward'], lw=1, ls='-.', marker=markerdict['store_forward'], ms=5)
        line6_fill = ax.fill_between(x_index, tc_server_sf_conf[:, 1],
                                     tc_server_sf_conf[:, 3], color=colordict['store_forward'], alpha=0.2)
        line7 = ax.errorbar(
            x_index, ts_cf_hbh_conf[:, 2], color=colordict['store_forward_ia'], lw=1, ls='-', marker=markerdict['store_forward_ia'], ms=5)
        line7_fill = ax.fill_between(x_index, ts_cf_hbh_conf[:, 1],
                                     ts_cf_hbh_conf[:, 3], color=colordict['store_forward_ia'], alpha=0.2)
        line8 = ax.errorbar(
            x_index, tt_cf_hbh_conf[:, 2], color=colordict['store_forward_ia'], lw=1, ls='--', marker=markerdict['store_forward_ia'], ms=5)
        line8_fill = ax.fill_between(x_index, tt_cf_hbh_conf[:, 1],
                                     tt_cf_hbh_conf[:, 3], color=colordict['store_forward_ia'], alpha=0.2)
        line9 = ax.errorbar(
            x_index, tc_server_cf_hbh_conf[:, 2], color=colordict['store_forward_ia'], lw=1, ls='-.', marker=markerdict['store_forward_ia'], ms=5)
        line9_fill = ax.fill_between(x_index, tc_server_cf_hbh_conf[:, 1],
                                     tc_server_cf_hbh_conf[:, 3], color=colordict['store_forward_ia'], alpha=0.2)
        ax.set_xlabel(r'Number of nodes $k$')
        ax.set_ylabel(r'Latency ($s$)')
        # ax.set_xlim([-0.2, 4.2])
        ax.set_yticks(np.arange(0, 18.1, 3))
        ax.legend([line1, line2, line3, line4, line5, line6], [r'$t_s$ of pICA', r'$t_s$ of FastICA', r'$t_t$ of pICA',
                  r'$t_t$ of FastICA', r'$t_c$ on the Server with pICA', r'$t_c$ on the Server with FastICA'], loc='upper right', ncol=2)
        plt.xticks(range(len(number_node)), number_node)
        plt.savefig('./emulator/measurement/plot/all_latency_emu.pdf',
                    dpi=600, bbox_inches='tight')

        fig = plt.figure(figsize=(fig_width, fig_width / 1.618))
        ax = fig.add_subplot(1, 1, 1)
        ax.yaxis.grid(True, linestyle='--', which='major',
                      color='lightgrey', alpha=0.5, linewidth=0.2)
        x_index = np.arange(len(number_node))
        bar1 = ax.bar(x_index - bardistance, tt_cf_conf[:, 2], barwidth,
                      fill=True, color=colordict['compute_forward'], edgecolor='#FFFFFF', ecolor='#555555', hatch='\\')
        bar2 = ax.bar(x_index - bardistance, tc_server_cf_conf[:, 2], barwidth, bottom=tt_cf_conf[:, 2], fill=True,
                      color=colordict['compute_forward'], edgecolor='#FFFFFF', ecolor='#555555', hatch='//')
        bar3 = ax.bar(x_index, tt_sf_conf[:, 2], barwidth,
                      fill=True, color=colordict['store_forward'], edgecolor='#FFFFFF', ecolor='#555555', hatch='/')
        bar4 = ax.bar(x_index, tc_server_sf_conf[:, 2], barwidth, bottom=tt_sf_conf[:, 2], fill=True,
                      color=colordict['store_forward'], edgecolor='#FFFFFF', ecolor='#555555', hatch='//')
        bar5 = ax.bar(x_index + bardistance, tt_cf_hbh_conf[:, 2], barwidth, fill=True,
                      color=colordict['store_forward_ia'], edgecolor='#FFFFFF', ecolor='#555555', hatch='\\')
        bar6 = ax.bar(x_index + bardistance, tc_server_cf_hbh_conf[:, 2], barwidth, bottom=tt_cf_hbh_conf[:, 2], fill=True,
                      color=colordict['store_forward_ia'], edgecolor='#FFFFFF', ecolor='#555555', hatch='//')
        line1 = ax.errorbar(
            x_index - bardistance, ts_cf_conf[:, 2], color=colordict['compute_forward'], lw=1, ls='-', marker=markerdict['compute_forward'], ms=5)
        line1_fill = ax.fill_between(x_index - bardistance, ts_cf_conf[:, 1],
                                     ts_cf_conf[:, 3], color=colordict['compute_forward'], alpha=0.2)
        line2 = ax.errorbar(
            x_index, ts_sf_conf[:, 2], color=colordict['store_forward'], lw=1, ls='-', marker=markerdict['store_forward'], ms=5)
        line2_fill = ax.fill_between(x_index, ts_sf_conf[:, 1],
                                     ts_sf_conf[:, 3], color=colordict['store_forward'], alpha=0.2)
        line3 = ax.errorbar(
            x_index + bardistance, ts_cf_hbh_conf[:, 2], color=colordict['store_forward_ia'], lw=1, ls='-', marker=markerdict['store_forward_ia'], ms=5)
        line3_fill = ax.fill_between(x_index + bardistance, ts_cf_hbh_conf[:, 1],
                                     ts_cf_hbh_conf[:, 3], color=colordict['store_forward_ia'], alpha=0.2)
        ax.set_xlabel(r'Number of nodes $k$')
        ax.set_ylabel(r'Latency ($s$)')
        ax.set_yticks(np.arange(0, 18.1, 3))
        ax.legend([line1, line2, line3, bar1, bar2, bar3, bar4, bar5, bar6], [r'$t_s$ of pICA', r'$t_s$ of FastICA', r'$t_t$ of pICA hbh',
                  r'$t_t$ of pICA', r'$t_c$ of pICA on the Server', r'$t_t$ of FastICA',  r'$t_c$ of pICA on the Server', r'$t_t$ of pICA hbh', r'$t_c$ of pICA hbh on the Server'], loc='upper left', ncol=2)
        plt.xticks(range(len(number_node)), number_node)
        plt.savefig('./emulator/measurement/plot/all_latency_emu_bar.pdf',
                    dpi=600, bbox_inches='tight')
