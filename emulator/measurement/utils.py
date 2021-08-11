import time
import json
import pickle

def measure_write(filename,contents):
    filename = '' + filename
    try:
        f = open("./emulator/measurement/"+filename+".csv","r")
        data = f.read()
    except Exception:
        data = ''
    data = data + ','.join(map(str,contents)) + ',\n'
    with open("./emulator/measurement/"+filename+".csv",'w') as f:
        f.write(data)
    f.close()

def measure_arr_to_jsonstr(numpy_arr):
    if numpy_arr is not None:
        return json.dumps([[y for y in x] for x in numpy_arr], separators=('|', ':'))
    else:
        return ''

def measure_jsonstr_to_arr(jsonstr):
    return json.loads(jsonstr.replace('|',','))

def measure_read_csv_to_2dlist(filename):
    f = open(filename,'r')
    lines = f.readlines()
    return [line.split(',') for line in lines]

def measure_write_table(filename,contents_list):
    for contents in contents_list:
        measure_write(filename,contents)

def measure_read_cols_from_2dlist(_2dlist,_col_name=None,position=-1):
    if position == -1:
        for i in range(len(_2dlist[0])):
            if _2dlist[0][i] == _col_name:
                position = i+1
    res = []
    for i in range(len(_2dlist)):
        res.append(float(_2dlist[i][position]))
    if position == -1:
        return []
    else:
        return res
    
