import time
import json


def measure_write(filename,times):
    try:
        f = open("measurement/"+filename+".csv","r")
        data = f.read()
    except Exception:
        data = ''
    data = data + ','.join(map(str,times)) + ',\n'
    with open("measurement/"+filename+".csv",'w') as f:
        f.write(data)
    f.close()


# def measure_time(marker,init_settings,time=time.time()):
#     if '@t' in init_settings:
#         init_settings['@t']+=[time]
#     else:
#         init_settings['@t']=[time]
#     if '@m' in init_settings:
#         init_settings['@m']+=[marker]
#     else:
#         init_settings['@m']=[marker]

# def measure_time_save(init_settings):
#     x0 = init_settings['@t'][0]
#     init_settings['@t'] = [str(x-x0) for x in init_settings['@t']]
#     f = open("measure/measure.csv","r")
#     data = f.read()
#     data = data + ','.join(init_settings['@m']) + ',\n'
#     data = data + ','.join(init_settings['@t']) + ',\n'

#     with open('measure/measure.csv','w') as f:
#         f.write(data)
#     f.close()

    # arr = json.load(open('measure/measure.json', 'r'))
    # dct = {}
    # x0 = init_settings['@t'][0]
    # init_settings['@t'] = [x-x0 for x in init_settings['@t']]
    # for key,value in zip(init_settings['@m'],init_settings['@t']):
    #     dct[key] = value
    # arr.append(dct)
    # json.dump(arr,open('measure/measure.json', 'w'))