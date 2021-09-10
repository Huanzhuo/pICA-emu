import numpy as np
import scipy.stats as st

import matplotlib
import matplotlib.pyplot as plt
from matplotlib import gridspec

matplotlib.use('TkAgg')

print(matplotlib.get_configdir())

if __name__ == '__main__':
    number_node = [0, 1, 2, 3, 4, 5, 6, 7]
    conf_rate = 0.95
    number_test = 50

    data = np.load('emulator/measurement/results_v4/time_iteration.npy')

    l_1 = np.array([1280])
    l_2 = np.array([2560])
    l_3 = np.array([5120])
    l_4 = np.array([10240])
    l_5 = np.array([20480])
    l_6 = np.array([40960])
    l_7 = np.array([81920])
    l_8 = np.array([160000])
    l_1_step = np.array([1280])
    l_2_step = np.array([2560])
    l_3_step = np.array([5120])
    l_4_step = np.array([10240])
    l_5_step = np.array([20480])
    l_6_step = np.array([40960])
    l_7_step = np.array([81920])
    l_8_step = np.array([160000])
    for i in np.arange(8):
        for j in np.arange(50):
            tmp = data[j, i, :]
            index = np.where(tmp != 0)
            tmp_data = tmp[index]
            if tmp_data.size == 0:
                print(str(j) + '-th test, no computing on the ' +
                      str(i) + '-th node')
            elif tmp_data[0] == 1280:
                l_1 = np.concatenate([l_1, tmp_data[1:]])
                l_1_step = np.append(l_1_step, len(tmp_data[1:]))
            elif tmp_data[0] == 2560:
                l_2 = np.concatenate([l_2, tmp_data[1:]])
                l_2_step = np.append(l_2_step, len(tmp_data[1:]))
            elif tmp_data[0] == 5120:
                l_3 = np.concatenate([l_3, tmp_data[1:]])
                l_3_step = np.append(l_3_step, len(tmp_data[1:]))
            elif tmp_data[0] == 10240:
                l_4 = np.concatenate([l_4, tmp_data[1:]])
                l_4_step = np.append(l_4_step, len(tmp_data[1:]))
            elif tmp_data[0] == 20480:
                l_5 = np.concatenate([l_5, tmp_data[1:]])
                l_5_step = np.append(l_5_step, len(tmp_data[1:]))
            elif tmp_data[0] == 40960:
                l_6 = np.concatenate([l_6, tmp_data[1:]])
                l_6_step = np.append(l_6_step, len(tmp_data[1:]))
            elif tmp_data[0] == 81920:
                l_7 = np.concatenate([l_7, tmp_data[1:]])
                l_7_step = np.append(l_7_step, len(tmp_data[1:]))
            elif tmp_data[0] == 160000:
                l_8 = np.concatenate([l_8, tmp_data[1:]])
                l_8_step = np.append(l_8_step, len(tmp_data[1:]))

    lk = np.zeros([2, 8])
    # lk_time =
    i = 0
    for l_k in [l_1, l_2, l_3, l_4, l_5, l_6, l_7, l_8]:
        lk[0, i] = l_k[0]
        if len(l_k[1:]) == 0:
            lk[1, i] = 0
        else:
            lk[1, i] = sum(l_k[1:])/len(l_k[1:])
        i += 1

    with plt.style.context(['science', 'ieee']):
        fig_width = 6.5
        barwidth = 0.2
        bardistance = barwidth * 1.4
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
        colorlist = ['r', 'b', 'y', 'g', 'm', 'c', 'k', 'gold']

        plt.rcParams.update({'font.size': 11})

        fig = plt.figure(figsize=(fig_width, fig_width / 1.618))
        ax = fig.add_subplot(1, 1, 1)
        ax.xaxis.grid(True, linestyle='--', which='major',
                      color='lightgrey', alpha=1, linewidth=0.2)
        ax.yaxis.grid(True, linestyle='--', which='both',
                      color='lightgrey', alpha=1, linewidth=0.2)
        ax_twin = ax.twinx()

        box_1 = ax.boxplot([l_1[1:], l_2[1:], l_3[1:], l_4[1:],
                            l_5[1:], l_6[1:], l_7[1:], l_8[1:]], positions=np.arange(8) - bardistance/2, vert=True, widths=barwidth, showfliers=False, showmeans=False, patch_artist=True,
                           boxprops=dict(
            color='black', facecolor=colordict['compute_forward'], lw=0.8, alpha=0.6),
            medianprops=dict(color='black', lw=2),
            capprops=dict(color='black', lw=0.8),
            whiskerprops=dict(color='black', lw=0.8),
            flierprops=dict(
            color=colordict['compute_forward'], markeredgecolor=colordict['compute_forward'], ms=3),
            meanprops=dict(markerfacecolor='black', markeredgecolor='black', ms=3))
        box_2 = ax_twin.boxplot([l_1_step[1:], l_2_step[1:], l_3_step[1:], l_4_step[1:],
                            l_5_step[1:], l_6_step[1:], l_7_step[1:], l_8_step[1:]], positions=np.arange(8) + bardistance/2, vert=True, widths=barwidth, showfliers=False, showmeans=False, patch_artist=True,
                           boxprops=dict(
            color='black', facecolor=colordict['store_forward'], lw=0.8, alpha=0.6),
            medianprops=dict(color='black', lw=2),
            capprops=dict(color='black', lw=0.8),
            whiskerprops=dict(color='black', lw=0.8),
            flierprops=dict(
            color=colordict['store_forward'], markeredgecolor=colordict['store_forward'], ms=3),
            meanprops=dict(markerfacecolor='black', markeredgecolor='black', ms=3))
        i = 0
        for element in [l_1, l_2, l_3, l_4, l_5, l_6, l_7, l_8]:
            x_index = i * \
                np.ones(len(element[1:],)) + \
                np.random.normal(0, 0.02, len(element[1:]))
            sct_1 = ax.scatter(
                x_index - bardistance/2, element[1:], color=colordict['compute_forward'], facecolor='none', alpha=1, s=8, marker='D', label='Time')
            # ax.text(i-0.2, max(element[1:])*1.2, r'$'+str(len(element[1:]))+r'$', rotation=0)
            i += 1
        i = 0
        for element in [l_1_step, l_2_step, l_3_step, l_4_step, l_5_step, l_6_step, l_7_step, l_8_step]:
            x_index = i * \
                np.ones(len(element[1:],)) + \
                np.random.normal(0, 0.02, len(element[1:]))
            sct_2 = ax_twin.scatter(
                x_index + bardistance/2, element[1:], color=colordict['store_forward'], facecolor='none', alpha=1, s=15, marker='o', label='Number')
            # ax.text(i-0.2, max(element[1:])*1.2, r'$'+str(len(element[1:]))+r'$', rotation=0)
            i += 1
        ax.set_xlabel(r'Size $\beta_k$ of cached data ${}_{\beta_k}X$ in percentage')
        ax.set_ylabel(r'Time of unit iteration ($ms$)')
        ax_twin.set_ylabel(r'Number of unit iteration')
        # ax.set_xticks(np.arange(0, 9, 4))
        # ax.set_xlim([-0.2, 4.2])
        ax.set_ylim([0.3, 250])
        ax_twin.set_ylim([0.3, 250])
        # ax.set_xticks([1280, 10240, 160000])
        # ax.set_yticks(np.arange(0, 176, 50))
        # ax_twin.set_yticks(np.arange(0, 13, 3))
        # ax.set_xscale('log')
        ax.set_yscale('log')
        ax_twin.set_yscale('log')
        # ax.legend([box_1["boxes"][0], box_2["boxes"][0]], ['Time', 'Number'], loc='upper left', ncol = 2)
        ax.legend([sct_1, sct_2], ['Time of unit iteration', 'Number of unit iteration'],
                  loc='upper left', ncol=1)
        # plt.xticks(np.arange(8), lk[0, :]/max(lk[0, :])*100)
        plt.xticks(np.arange(8), ['0.8\%', '1.6\%', '3.2\%',
                   '6.4\%', '12.8\%', '25.6\%', '51.2\%', '100\%'])
        plt.savefig('./emulator/measurement/plot/iteration_time_lk.pdf',
                    dpi=600, bbox_inches='tight')

        # plt.rcParams.update({'font.size': 11})

        # fig = plt.figure(figsize=(fig_width, fig_width * 2))
        # ax = fig.add_subplot(111, projection='3d')
        # ax.xaxis.grid(True, linestyle='--', which='major',
        #               color='lightgrey', alpha=1, linewidth=0.2)
        # ax.yaxis.grid(True, linestyle='--', which='major',
        #               color='lightgrey', alpha=1, linewidth=0.2)
        # ax.zaxis.grid(False)
        # x_index = np.arange(data.shape[1])
        # for i in np.arange(data.shape[1]):
        #     for j in np.arange(number_test):
        #         y_index = data[j, i, 0]
        #         z_tmp = data[j, i, 1:]
        #         z_index = np.where(z_tmp != 0)
        #         z_value = z_tmp[z_index]
        #         ax.scatter3D(x_index[i], y_index, z_value, color=colorlist[i])
        # ax.view_init(15, 70)
        # ax.set_xlabel(r'Node index')
        # ax.set_ylabel(r'Size of subset data $l_k$')
        # ax.set_zlabel(r'Computing time per iteration step ($ms$)')
        # # ax.set_xlim([-0.2, 4.2])
        # ax.set_xticks(np.arange(0, 9, 4))
        # ax.set_yticks(np.arange(0, 160001, 80000))
        # ax.set_zticks(np.arange(0, 176, 50))
        # # ax.set_zscale('log')
        # # ax.legend([line1, line2, line3], ['pICA',
        # #                                   'FastICA', 'pICA hbh'], loc='upper left')
        # plt.xticks(np.arange(0, 9, 4), ['1', '5', 'RA'])
        # plt.savefig('./emulator/measurement/plot/iteration_time_lk.pdf',
        #             dpi=600, bbox_inches='tight')
