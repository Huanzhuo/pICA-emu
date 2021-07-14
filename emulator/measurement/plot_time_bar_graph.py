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
    vnf1_s1_excel = "./emulator/measurement/vnf1-s1.csv"
    vnf2_s2_excel = "./emulator/measurement/vnf2-s2.csv"

    vnf1_s1 = np.genfromtxt(vnf1_s1_excel, delimiter=',', usecols=[0])
    vnf2_s2 = np.genfromtxt(vnf2_s2_excel, delimiter=',', usecols=[0])
    
    vnf1_s1 = vnf1_s1[~np.isnan(vnf1_s1)]
    vnf2_s2 = vnf2_s2[~np.isnan(vnf2_s2)]

    avg_vnf1 = sum(vnf1_s1)/len(vnf1_s1)
    avg_vnf2 = sum(vnf2_s2)/len(vnf2_s2)
    
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
        names = ['Vnf 1', 'Vnf 2']
        new_colors = [colordict['compute_forward'], colordict['store_forward_ia']]

        avg_vnf = [avg_vnf1, avg_vnf2]

        fig = plt.bar(names, avg_vnf, color=new_colors)
        plt.grid(True, linestyle='--', which='major', color='lightgrey', alpha=0.5, linewidth=0.2)
        plt.ylabel('Average time per vnf (s)')
        plt.savefig('./emulator/measurement/vnf_time.pdf', dpi=600, bbox_inches='tight')