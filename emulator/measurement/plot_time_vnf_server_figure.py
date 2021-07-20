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

    counter = 0
    
    average_processing_time = []
    while counter < 10:
        i = 0
        average_processing_time_vnf = []

        while i < counter:
            
            nodes_excel = "./emulator/measurement/1s/"+str(counter)+"_nodes/vnf"+str(i)+"-s"+str(i)+".csv"
            nodes = np.loadtxt(nodes_excel, delimiter=',', dtype=None, usecols=[3])
            nodes = np.resize(nodes, 31)
            average_processing_time_vnf.append(np.average(nodes))
            i += 1

        server_excel = "./emulator/measurement/1s/"+str(counter)+"_nodes/server_cf.csv"
        server = np.loadtxt(server_excel, delimiter=',', dtype=None, usecols=[1])
        server = np.resize(server, 31)
        
        average_processing_time.append(np.sum(average_processing_time_vnf) + np.average(server))
        average_processing_time_vnf.clear()
        counter += 2 
    
    counter = 0
    average_processing_time_sf = []
    while counter < 10:
        server_excel = "./emulator/measurement/1s/"+str(counter)+"_nodes/server_sf.csv"
        server = np.loadtxt(server_excel, delimiter=',', dtype=None, usecols=[1])
        server = np.resize(server, 31)
        
        average_processing_time_sf.append(np.average(server))
        counter += 2 

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

        
        average_processing_time_array = np.array(average_processing_time)
        #average_processing_time_array *= 1000

        average_processing_time_sf_array = np.array(average_processing_time_sf)

        print(average_processing_time)

        x_axis = [0, 2, 4, 6, 8]

        plt.scatter(x_axis, average_processing_time_array, color=colordict['compute_forward'], marker=markerdict['compute_forward'], ls='-')
        plt.plot(x_axis, average_processing_time_array, color=colordict['compute_forward'], marker=markerdict['compute_forward'], ls='-', label="Compute Forward")

        plt.scatter(x_axis, average_processing_time_sf_array, color=colordict['store_forward'], marker=markerdict['store_forward'], ls='-')
        plt.plot(x_axis, average_processing_time_sf_array, color=colordict['store_forward'], marker=markerdict['store_forward'], ls='-', label="Store Forward")
        plt.legend(loc="upper left")
        plt.ylim(1.5, 4.5)

        plt.ylabel('Processing time of VNF + server (s)')
        plt.xlabel('Number of nodes ')

        plt.savefig('./emulator/measurement/processing_time_vnf_and_server.pdf', dpi=600, bbox_inches='tight')
        