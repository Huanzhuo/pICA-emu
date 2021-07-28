import time
import json
import pickle


n_vnf = 7
mode = 'cf'
n_start = 0
n_test = 1
en_user_space = False
en_lite_mode = True
test_topo_settings={'n_vnf':n_vnf,'mode':mode}
test_client_settings={'user_space':en_user_space,'n_vnf':n_vnf,'mode':mode,'n_start':n_start,'n_test':n_test}
test_vnf_settings={'user_space':en_user_space,'n_vnf':n_vnf,'mode':mode,'lite_mode':en_lite_mode,'n_start':n_start}
test_server_settings={'n_vnf':n_vnf,'mode':mode,'lite_mode':en_lite_mode}





def measure_write(filename,contents):
    filename = 'tmp/midres_' + mode + '_s' + str(n_vnf) + 'x' + str(n_start) + 'us' + str(en_user_space) + 'lite' + str(en_lite_mode)
    try:
        f = open("measurement/"+filename+".csv","r")
        data = f.read()
    except Exception:
        data = ''
    data = data + ','.join(map(str,contents)) + ',\n'
    with open("measurement/"+filename+".csv",'w') as f:
        f.write(data)
    f.close()

def measure_write_table(filename,contents_list):
    for contents in contents_list:
        measure_write(filename,contents)

def measure_arr_to_jsonstr(numpy_arr):
    if numpy_arr is not None:
        return json.dumps([[float(y) for y in x] for x in numpy_arr], separators=('|', ':'))
    else:
        return ''

def measure_jsonstr_to_arr(jsonstr):
    return json.loads(jsonstr.replace('|',','))

def measure_read_csv_to_2dlist(filename):
    f = open("measurement/1s/"+filename+".csv",'r')
    lines = f.readlines()
    return [line.split(',') for line in lines]


