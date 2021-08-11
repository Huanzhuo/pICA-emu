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
    node_number = [1, 4, 7, 2, 3, 5, 6]
    dataset_number = 50
    test_mode_total = ['_cf', '_sf', '_cf_hbh']  # _sf _cf _cf_hbh
    conf_rate = 0.95

    fr = open('./emulator/MIMII/saxsNew.pkl', 'rb')
    saxs = pickle.load(fr)
    ss, aa, xx = saxs

    for node_k in node_number:
        for test_mode in test_mode_total:
            if test_mode != '_sf':
                compute_timestamp_k = np.arange(0, (node_k+1)*2+1)
                compute_accuracy_k = np.arange(0, (node_k+1)*2+1)
            else:
                compute_timestamp_k = np.arange(0, 3)
                compute_accuracy_k = np.arange(0, 3)

            for dataset_id in range(0, dataset_number):
                print('Processing ' + str(node_k) +
                        ' nodes with '+str(dataset_id)+'-th dataset.')
                path_client_cf = './emulator/measurement/results_v4/' + \
                    str(node_k)+'s/client'+test_mode+'.csv'
                w = np.array(json.loads(measure_read_csv_to_2dlist(
                    path_client_cf)[dataset_id][9].replace('|', ',')))
                accuracy = get_accuracy(ss[dataset_id], xx[dataset_id], w)
                timestamp_client = np.loadtxt(
                    path_client_cf, delimiter=',', usecols=[3, 5, 7])[dataset_id]
                timestamp_accuracy = np.array(
                    [timestamp_client[0]-timestamp_client[0], accuracy])
                compute_timestamp = timestamp_client[0]-timestamp_client[0]
                compute_accuracy = accuracy

                if test_mode != '_sf':
                    for vnf in range(0, node_k):
                        path_vnf_csv = './emulator/measurement/results_v4/' + \
                            str(node_k)+'s/vnf' + str(vnf) + \
                            '-s' + str(vnf)+test_mode+'.csv'
                        timestamp = np.loadtxt(path_vnf_csv, delimiter=',',
                                                usecols=[3, 7])[dataset_id]

                        w_pre = np.array(json.loads(measure_read_csv_to_2dlist(
                            path_vnf_csv)[dataset_id][5].replace('|', ',')))
                        accuracy_pre = get_accuracy(
                            ss[dataset_id], xx[dataset_id], w_pre)
                        timestamp_accuracy_pre = np.array([
                            timestamp[0]-timestamp_client[0], accuracy_pre])
                        compute_timestamp = np.append(
                            compute_timestamp, timestamp[0]-timestamp_client[0])
                        compute_accuracy = np.append(
                            compute_accuracy, accuracy_pre)

                        w = np.array(json.loads(measure_read_csv_to_2dlist(
                            path_vnf_csv)[dataset_id][9].replace('|', ',')))
                        accuracy = get_accuracy(
                            ss[dataset_id], xx[dataset_id], w)
                        timestamp_accuracy = np.array(
                            [timestamp_accuracy_pre[0] + timestamp[1], accuracy])
                        compute_timestamp = np.append(
                            compute_timestamp, timestamp_accuracy_pre[0] + timestamp[1])
                        compute_accuracy = np.append(
                            compute_accuracy, accuracy)

                path_server_cf = './emulator/measurement/results_v4/' + \
                    str(node_k)+'s/server'+test_mode+'.csv'
                timestamp = np.loadtxt(path_server_cf, delimiter=',',
                                        usecols=[1, 5])[dataset_id]

                w_pre = np.array(json.loads(measure_read_csv_to_2dlist(
                    path_server_cf)[dataset_id][3].replace('|', ',')))
                accuracy_pre = get_accuracy(
                    ss[dataset_id], xx[dataset_id], w_pre)
                timestamp_accuracy_pre = np.array([timestamp[0] -
                                                    timestamp_client[0], accuracy_pre])
                compute_timestamp = np.append(
                    compute_timestamp, timestamp[0] - timestamp_client[0])
                compute_accuracy = np.append(
                    compute_accuracy, accuracy_pre)

                w = np.array(json.loads(measure_read_csv_to_2dlist(
                    path_server_cf)[dataset_id][7].replace('|', ',')))
                accuracy = get_accuracy(ss[dataset_id], xx[dataset_id], w)
                timestamp_accuracy = np.array(
                    [timestamp_accuracy_pre[0] + timestamp[1], accuracy])
                compute_timestamp = np.append(
                    compute_timestamp, timestamp_accuracy_pre[0] + timestamp[1])
                compute_accuracy = np.append(compute_accuracy, accuracy)
                print(compute_timestamp)
                print(compute_accuracy)
                compute_timestamp_k = np.column_stack(
                    (compute_timestamp_k, compute_timestamp))
                compute_accuracy_k = np.column_stack(
                    (compute_accuracy_k, compute_accuracy))

            measure_write_table('/results_v4/'+str(node_k)+'s/pICA_accuracy' +
                        test_mode, compute_accuracy_k)
            measure_write_table('/results_v4/'+str(node_k)+'s/pICA_time' +
                        test_mode, compute_timestamp_k)
