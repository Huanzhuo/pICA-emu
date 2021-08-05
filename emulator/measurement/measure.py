import time
import json
import pickle

def measure_write(filename,contents):
    filename = 'tmp/' + filename
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



if __name__ == '__main__':
    #table1 = measure_read_csv_to_2dlist(filename)
    pass