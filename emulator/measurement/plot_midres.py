from librosa.core.convert import note_to_svara_c
from utils import *
import numpy as np
import matplotlib.pyplot as plt
import matplotlib
from pybss_testbed import *
matplotlib.use('TkAgg')


colordict = {
    'cf':'#FF7F50',
    'sf':'#8085E8',
    'pica': '#FF7F50',  #'FFD700'
    'pica_seq': '#FF7F50',
    'aeica': '#40E0D0',
    'aeica_seq': '#3CB371',
    'fastica': '#8085E8',
    'darkblue': '#024B7A',
    'lightblue': '#3F9ABF',
    'midblue': '#7ACFE5'
}
markerdict = {
    'cf':'d',
    'sf':'o',
    'pica': 'd',
    'pica_seq': 'd',
    'aeica': '^',
    'aeica_seq': 'v',
    'fastica': 'o'
}
barwidth = 0.1
figwidth = 6.5
figheight = 6.5 / 1.618

fr = open('emulator/MIMII/saxsNew.pkl','rb')
saxs = pickle.load(fr)
ss,aa,xx = saxs

def read_service_latency_sdr(filename = 'emulator/measurement/tmp/rec_intermediate_ws_all.csv'):
    res_time =[]
    res_sdr = []
    table = measure_read_csv_to_2dlist(filename)
    line_client = table[0]
    time0 = float(line_client[3])
    n_vnf = int(line_client[1])
    for i in range(1,n_vnf+2):
        line = table[i]
        l = (len(line)-3)//4
        for k in range(l):
            time = float(line[int(k*4+1+3)]) - time0
            time = time
            W = np.array(measure_jsonstr_to_arr(line[int(k*4+3+3)]))
            S = ss[0]
            X = xx[0]
            hat_S = np.dot(W,X)
            sdr = pybss_tb.bss_evaluation(S, hat_S, type='psnr')
            res_time.append(time)
            res_sdr.append(sdr)
    return np.array(res_time),np.array(res_sdr)

def read_computing_latency_sdr(filename = 'emulator/measurement/tmp/rec_intermediate_ws_all.csv'):
    res_time =[]
    res_sdr = []
    table = measure_read_csv_to_2dlist(filename)
    line_client = table[0]
    time0 = float(line_client[3])
    time_compute = 0
    n_vnf = int(line_client[1])
    for i in range(1,n_vnf+2):
        line = table[i]
        l = (len(line)-3)//4
        time0 = float(line[int(0*4+1+3)])
        for k in range(l):
            _time = float(line[int(k*4+1+3)]) - time0 + time_compute
            W = np.array(measure_jsonstr_to_arr(line[int(k*4+3+3)]))
            S = ss[0]
            X = xx[0]
            hat_S = np.dot(W,X)
            sdr = pybss_tb.bss_evaluation(S, hat_S, type='psnr')
            res_time.append(_time)
            res_sdr.append(sdr)
        time_compute = _time
        
    return np.array(res_time),np.array(res_sdr)

with plt.style.context(['science', 'ieee']):
    fig = plt.figure(figsize=(figwidth,  figheight))
    ax = fig.add_subplot(1, 1, 1)
    ax.yaxis.grid(True, linestyle='--', which='major',
                    color='lightgrey', alpha=0.5, linewidth=0.2)
    def draw_line(filename,color):
        x,y =read_computing_latency_sdr(filename)
        # x,y =read_service_latency_sdr(filename)
        line = ax.plot(x, y, color=color)#,s=20)
        parameter = np.polyfit(x, y, 2)
        #x = np.arange(80,160000,80)
        x = np.arange(min(x),max(x),0.01)
        y2 = parameter[-3] * x ** 2 + parameter[-2] * x + parameter[-1] #parameter[-4] * x ** 3 + 
        # line = ax.errorbar(x, y2, color='#CD5C5C', lw=1, ls='-')        
        return line

    line1 = draw_line('emulator/measurement/tmp/rec_intermediate_ws_all2.csv','red')
    line2 = draw_line('emulator/measurement/tmp/rec_intermediate_ws_all.csv','black')
    ax.set_xlabel(r'Transimission Latency $t_t$ $(ms)$')
    ax.set_ylabel(r'SDR $(dB)$')
    #ax.set_xticks(np.arange(1, 10000, 1000))
    ax.set_xlim([-0.5, 10])
    # ax.set_xticks([100,1000,10000])
    ax.set_yticks(np.arange(0, 40, 5))
    ax.set_ylim([0, 40])
    # ax.set_xscale('log')
    #plt.xticks(x0)
    ax.legend([line1,line2], [
        'kernel_space','user_space' ], loc='upper left')
    plt.savefig('eval_latency_sdr.pdf',dpi=1200, bbox_inches='tight')