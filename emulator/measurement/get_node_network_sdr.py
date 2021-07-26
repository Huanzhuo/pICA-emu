import json
import numpy as np
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
    number_node = [0, 1, 2, 3, 4, 5, 6, 7, 8]
    conf_rate = 0.95
    number_test = 50

    fr = open('./emulator/MIMII/saxsNew.pkl', 'rb')
    saxs = pickle.load(fr)
    ss, aa, xx = saxs

    accuracy_cf = np.zeros(number_test)
    accuracy_sf = np.zeros(number_test)
    for node in number_node:
        path_server_compute_client = './emulator/measurement/' + \
            str(node)+'s/server_cf.csv'
        path_server_compute_client_2 = './emulator/measurement/' + \
            str(node)+'s/server_cf_2.csv'
        path_server_store_client = './emulator/measurement/' + \
            str(node)+'s/server_sf.csv'
        node_accuracy_cf = []
        node_accuracy_cf_2 = []
        node_accuracy_sf = []

        for test_id in range(number_test):
            s = ss[test_id]
            x = xx[test_id]

            w = np.array(json.loads(measure_read_csv_to_2dlist(path_server_compute_client)[test_id][3].replace('|', ',')))
            hat_s = np.dot(w, x)
            node_accuracy_cf = np.append(node_accuracy_cf, pybss_tb.bss_evaluation(s, hat_s, type='sdr'))

            w = np.array(json.loads(measure_read_csv_to_2dlist(path_server_compute_client_2)[test_id][3].replace('|', ',')))
            hat_s = np.dot(w, x)
            node_accuracy_cf_2 = np.append(node_accuracy_cf_2, pybss_tb.bss_evaluation(s, hat_s, type='sdr'))

            w = np.array(json.loads(measure_read_csv_to_2dlist(path_server_store_client)[test_id][3].replace('|', ',')))
            hat_s = np.dot(w, x)
            node_accuracy_sf = np.append(node_accuracy_sf, pybss_tb.bss_evaluation(s, hat_s, type='sdr'))

        measure_write('pICA_accuracy_cf', node_accuracy_cf)
        measure_write('pICA_accuracy_cf_2', node_accuracy_cf_2)
        measure_write('pICA_accuracy_sf', node_accuracy_sf)