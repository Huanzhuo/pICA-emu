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


def get_accuracy(s, x, w):
    hat_s = np.dot(w, x)
    accuracy = pybss_tb.bss_evaluation(s, hat_s, type='sdr')
    return accuracy


if __name__ == '__main__':
    node_number = [2]
    dataset_id = 0
    test_mode = '_cf'  # _sf _cf _cf_false

    fr = open('./emulator/MIMII/saxsNew.pkl', 'rb')
    saxs = pickle.load(fr)
    ss, aa, xx = saxs

    # node_k = node_number[1]
    for node_k in node_number:
        path_client_cf = './emulator/measurement/' + \
            str(node_k)+'s/client'+test_mode+'.csv'
        w = np.array(json.loads(measure_read_csv_to_2dlist(
            path_client_cf)[dataset_id][9].replace('|', ',')))
        accuracy = get_accuracy(ss[dataset_id], xx[dataset_id], w)
        timestamp_client = np.loadtxt(
            path_client_cf, delimiter=',', usecols=[3, 5, 7])[dataset_id]
        timestamp_accuracy = [timestamp_client[0] -
                              timestamp_client[0], accuracy]
        pICA_k = [timestamp_client[0]-timestamp_client[0], accuracy]
        print(timestamp_accuracy)

        if test_mode != '_sf':
            for vnf in range(0, node_k):
                path_vnf_csv = './emulator/measurement/' + \
                    str(node_k)+'s/vnf' + str(vnf) + \
                    '-s' + str(vnf)+test_mode+'.csv'
                w_pre = np.array(json.loads(measure_read_csv_to_2dlist(
                    path_vnf_csv)[dataset_id][5].replace('|', ',')))
                accuracy_pre = get_accuracy(
                    ss[dataset_id], xx[dataset_id], w_pre)
                w = np.array(json.loads(measure_read_csv_to_2dlist(
                    path_vnf_csv)[dataset_id][9].replace('|', ',')))
                accuracy = get_accuracy(ss[dataset_id], xx[dataset_id], w)

                timestamp = np.loadtxt(path_vnf_csv, delimiter=',',
                                       usecols=[3, 7])[dataset_id]

                timestamp_accuracy_pre = [
                    timestamp[0]-timestamp_client[0], accuracy_pre]
                pICA_k = np.row_stack((pICA_k, timestamp_accuracy_pre))
                print(timestamp_accuracy_pre)

                timestamp_accuracy = [pICA_k[-1, 0] + timestamp[1], accuracy]
                pICA_k = np.row_stack((pICA_k, timestamp_accuracy))
                print(timestamp_accuracy)

        path_server_cf = './emulator/measurement/' + \
            str(node_k)+'s/server'+test_mode+'.csv'
        w_pre = np.array(json.loads(measure_read_csv_to_2dlist(
            path_server_cf)[dataset_id][3].replace('|', ',')))
        accuracy_pre = get_accuracy(ss[dataset_id], xx[dataset_id], w_pre)
        w = np.array(json.loads(measure_read_csv_to_2dlist(
            path_server_cf)[dataset_id][7].replace('|', ',')))
        accuracy = get_accuracy(ss[dataset_id], xx[dataset_id], w)

        timestamp = np.loadtxt(path_server_cf, delimiter=',',
                               usecols=[1, 5])[dataset_id]

        timestamp_accuracy_pre = [timestamp[0] -
                                  timestamp_client[0], accuracy_pre]
        pICA_k = np.row_stack((pICA_k, timestamp_accuracy_pre))
        print(timestamp_accuracy_pre)

        timestamp_accuracy = [pICA_k[-1, 0] + timestamp[1], accuracy]
        pICA_k = np.row_stack((pICA_k, timestamp_accuracy))
        print(timestamp_accuracy)

        measure_write('pICA_'+str(dataset_id)+test_mode, pICA_k)
