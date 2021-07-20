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
    nodes_0_cf_excel = "./emulator/measurement/1s/0_nodes/client_cf.csv"
    nodes_0_sf_excel = "./emulator/measurement/1s/0_nodes/client_sf.csv"

    nodes_2_cf_excel = "./emulator/measurement/client_cf.csv"
    nodes_2_sf_excel = "./emulator/measurement/client_sf.csv"

    nodes_4_cf_excel = "./emulator/measurement/1s/4_nodes/client_cf.csv"
    nodes_4_sf_excel = "./emulator/measurement/1s/4_nodes/client_sf.csv"

    nodes_6_cf_excel = "./emulator/measurement/1s/6_nodes/client_cf.csv"
    nodes_6_sf_excel = "./emulator/measurement/1s/6_nodes/client_sf.csv"

    nodes_8_cf_excel = "./emulator/measurement/1s/8_nodes/client_cf.csv"
    nodes_8_sf_excel = "./emulator/measurement/1s/8_nodes/client_sf.csv"


    
    cf_service_latency_nodes_2 = np.loadtxt(nodes_2_cf_excel, delimiter=',', dtype=None, usecols=[1])
    cf_service_latency_nodes_2 = np.resize(cf_service_latency_nodes_2, 31)

    sf_service_latency_nodes_2 = np.loadtxt(nodes_2_sf_excel, delimiter=',', dtype=None, usecols=[1])
    sf_service_latency_nodes_2 = np.resize(sf_service_latency_nodes_2, 31)

    cf_service_latency_nodes_0 = np.loadtxt(nodes_0_cf_excel, delimiter=',', dtype=None, usecols=[5])
    cf_service_latency_nodes_0 = np.resize(cf_service_latency_nodes_0, 31)

    sf_service_latency_nodes_0 = np.loadtxt(nodes_0_sf_excel, delimiter=',', dtype=None, usecols=[5])
    sf_service_latency_nodes_0 = np.resize(sf_service_latency_nodes_0, 31)    

    cf_service_latency_nodes_4 = np.loadtxt(nodes_4_cf_excel, delimiter=',', dtype=None, usecols=[5])
    cf_service_latency_nodes_4 = np.resize(cf_service_latency_nodes_4, 31)

    sf_service_latency_nodes_4 = np.loadtxt(nodes_4_sf_excel, delimiter=',', dtype=None, usecols=[5])
    sf_service_latency_nodes_4 = np.resize(sf_service_latency_nodes_4, 31)    

    cf_service_latency_nodes_6 = np.loadtxt(nodes_6_cf_excel, delimiter=',', dtype=None, usecols=[5])
    cf_service_latency_nodes_6 = np.resize(cf_service_latency_nodes_6, 31)

    sf_service_latency_nodes_6 = np.loadtxt(nodes_6_sf_excel, delimiter=',', dtype=None, usecols=[5])
    sf_service_latency_nodes_6 = np.resize(sf_service_latency_nodes_6, 31)  

    cf_service_latency_nodes_8 = np.loadtxt(nodes_8_cf_excel, delimiter=',', dtype=None, usecols=[5])
    cf_service_latency_nodes_8 = np.resize(cf_service_latency_nodes_8, 31)

    sf_service_latency_nodes_8 = np.loadtxt(nodes_8_sf_excel, delimiter=',', dtype=None, usecols=[5])
    sf_service_latency_nodes_8 = np.resize(sf_service_latency_nodes_8, 31)      
    
    #service_latency_compute_forward = np.loadtxt(path_time_compute_client, delimiter=',', dtype=None, usecols=[1])
    #service_latency_store_forward = np.loadtxt(path_time_store_client, delimiter=',', dtype=None, usecols=[1])
    
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

        average_latency_cf = [np.average(cf_service_latency_nodes_0), np.average(cf_service_latency_nodes_2), np.average(cf_service_latency_nodes_4), np.average(cf_service_latency_nodes_6), np.average(cf_service_latency_nodes_8)]
        average_latency_sf = [np.average(sf_service_latency_nodes_0), np.average(sf_service_latency_nodes_2), np.average(sf_service_latency_nodes_4), np.average(sf_service_latency_nodes_6), np.average(sf_service_latency_nodes_8)]

        average_latency_cf_array = np.array(average_latency_cf)
        #average_latency_cf_array *= 1000

        average_latency_sf_array = np.array(average_latency_sf)
        #average_latency_sf_array *= 1000

        x_axis = [0, 2, 4, 6, 8]

        plt.scatter(x_axis, average_latency_cf_array, color=colordict['compute_forward'], marker=markerdict['compute_forward'], ls='-')
        plt.plot(x_axis, average_latency_cf_array, color=colordict['compute_forward'], marker=markerdict['compute_forward'], ls='-', label="Computer Forward")

        plt.scatter(x_axis, average_latency_sf_array, color=colordict['store_forward'], marker=markerdict['store_forward'], ls='-')
        plt.plot(x_axis, average_latency_sf_array, color=colordict['store_forward'], marker=markerdict['store_forward'], ls='-', label="Store Forward")

        plt.legend(loc="upper left")
        plt.ylim(7, 10.5)

        plt.ylabel('Service latency (s)')
        plt.xlabel('Number of nodes ')

        plt.savefig('./emulator/measurement/end-to-end-service-latency.pdf', dpi=600, bbox_inches='tight')
        