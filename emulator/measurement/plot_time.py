import json
import numpy as np
import scipy.stats as st

import matplotlib
import matplotlib.pyplot as plt
from matplotlib import gridspec

matplotlib.use('TkAgg')

print(matplotlib.get_configdir())

if __name__ == '__main__':
    # txt paths of store-forward(client vnf1 vnf2) and compute-forward(server)
    path_time_compute_client = "./emulator/measurement/client_cf.csv"
    path_time_store_client = "./emulator/measurement/client_sf.csv"

    service_latency_compute_forward = np.loadtxt(path_time_compute_client)
    service_latency_store_forward = np.loadtxt(path_time_store_client)

    # service_latency_compute_forward = np.loadtxt(path_time_compute_client, delimiter=',', usecols=range(2))[:, -1]
    # service_latency_store_forward = np.loadtxt(path_time_store_client, delimiter=',', usecols=range(2))[:, -1]

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
        x_step = np.arange(len(service_latency_compute_forward))
        line1, = ax.plot(x_step, service_latency_compute_forward, color=colordict['compute_forward'], marker=markerdict['compute_forward'], ms=3, ls='-')
        line2, = ax.plot(x_step, service_latency_store_forward, color=colordict['store_forward'], marker=markerdict['store_forward'], ms=3, ls='-')
        # line3, = ax.plot(x_step, processing_time_ia_net_server, color=colordict['store_forward_ia'], marker=markerdict['store_forward_ia'], ms=3, ls='--')
        ax.set_xlabel(r'Meaurement index')
        ax.set_ylabel(r'Service latency ($s$)')
        # ax.set_xlim([-0.5, 1.5])
        ax.set_ylim([9, 10])
        ax.legend([line1, line2], ['Compute-and-Forward', 'Store-and-Forward'], loc='upper right')
        plt.savefig('./emulator/measurement/service_latency_all.pdf',
                    dpi=600, bbox_inches='tight')