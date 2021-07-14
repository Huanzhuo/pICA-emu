# -*- coding: utf-8 -*-

# @Author: Shenyunbin
# @email : yunbin.shen@mailbox.tu-dresden.de / shenyunbin@outlook.com
# @create: 2020-01-01
# @modify: 2021-04-05
# @desc. : [description]

import numpy as np
from scipy.io import wavfile
import random
import glob
import time
import museval
import math
#import librosa
from sklearn.decomposition import FastICA
from pesq import pesq
'''
# FAST BSS TESTBED Version 0.1.0:

    timer_start(self):
    timer_value(self):
    timer_suspend(self):
    timer_resume(self):
    wavs_to_matrix_S(self, folder_address, duration, source_number):
    generate_matrix_A(self, S, mixing_type="random", max_min=(1, 0.01), mu_sigma=(0, 1)):
    generate_matrix_S_A_X(self, folder_address, wav_range, source_number, 
        mixing_type="random", max_min=(1, 0.01), mu_sigma=(0, 1)):
    fast_psnr(self, S, hat_S):
    bss_evaluation(self, S, hat_S, type='fast_psnr'):

# Basic definition:

    S: Source signals. shape = (source_number, time_slots_number)
    X: Mixed source signals. shape = (source_number, time_slots_number)
    A: Mixing matrix. shape = (source_number, source_number)
    B: Separation matrix. shape = (source_number, source_number)
    hat_S: Estimated source signals durch ICA algorithms. 
        shape = (source_number, time_slots_number)

# Notes:

    X = A @ S
    S = B @ X
    B = A ^ -1
'''


class PyFastbssTestbed:

    def __init__(self):
        self.timer_start_time = 0
        self.timer_suspend_time = 0

    def timer_start(self):
        '''
        # timer_start(self):

        # Usage:

            Start the timer
        '''
        self.timer_start_time = time.time()

    def timer_value(self):
        '''
        # timer_value(self):

        # Usage:

            Get the current time

        # Output:

            The current value (i.e. time) of the timer
        '''
        return 1000*(time.time()-self.timer_start_time)

    def timer_suspend(self):
        '''
        # timer_suspend(self):

        # Usage:

            Suspend the timer
        '''
        self.timer_suspend_time = time.time()

    def timer_resume(self):
        '''
        # timer_resume(self):

        # Usage:

            Resume the timer
        '''
        #print("suspend: ", time.time() - self.timer_suspend_time)
        self.timer_start_time = self.timer_start_time + \
            time.time() - self.timer_suspend_time

    def get_wav_filenames(self, folder_address, source_number):
        wav_path = folder_address + '/*.wav'
        wav_filenames = glob.glob(wav_path)
        return random.sample(wav_filenames, source_number)

    def wav_filenames_to_matrix_S(self, filenames, duration):
        S = []
        for filename in filenames:
            sample_rate,_s = wavfile.read(filename)
            _s = np.mean(_s,axis=1)
            wav_length = np.shape(_s)[-1]
            wav_range = int(duration*sample_rate)
            if wav_range > wav_length:
                raise ValueError('Error - wav_to_S : The wav_range too big !')
            wav_start = int(0.5*wav_length) - int(0.5*wav_range)
            wav_stop = int(0.5*wav_length) + int(0.5*wav_range)
            _single_source = _s[wav_start:wav_stop]
            _single_source = _single_source / np.mean(abs(_single_source))
            S.append(_single_source)
        return np.asarray(S)



    def wavs_to_matrix_S(self, folder_address, duration, source_number):
        '''
        # wavs_to_matrix_S(self, folder_address, duration, source_number):

        # Usage:

            Input the wav files to generate the source signal matrix S

        # Parameters:

            folder_address: Define folder adress, in which the *.wav files exist. 
                The wav files must have only 1 channel.

            duration: The duration of the output original signals, 
                i.e. the whole time domain of the output matrix S

            source number: The number of the source signals in matrix S

        # Output:

            Matrix S.
            The shape of the S is (source number, time slots number), 
            the wav files are randomly selected to generate the matrix S.
        '''
        wav_path = folder_address + '/*.wav'
        wav_filenames = glob.glob(wav_path)
        random_indexs = random.sample(range(len(wav_filenames)), source_number)
        S = []
        for i in range(source_number):
            sample_rate,_s = wavfile.read(wav_filenames[random_indexs[i]])
            _s = np.mean(_s,axis=1)
            wav_length = np.shape(_s)[-1]
            wav_range = int(duration*sample_rate)
            if wav_range > wav_length:
                raise ValueError('Error - wav_to_S : The wav_range too big !')
            wav_start = int(0.5*wav_length) - int(0.5*wav_range)
            wav_stop = int(0.5*wav_length) + int(0.5*wav_range)
            _single_source = _s[wav_start:wav_stop]
            _single_source = _single_source / np.mean(abs(_single_source))
            S.append(_single_source)
        return np.asarray(S)

    def generate_matrix_A(self, S, mixing_type="random", max_min=(1, 0.01), mu_sigma=(0, 1), source_number=None):
        '''
        # generate_matrix_A(self, S, mixing_type="random", max_min=(1,0.01), mu_sigma=(0,1)):

        # Usage:

            Generate the mixing matrix A according to the size of the source signal matrix S

        # Parameters:

            mixing_type:
                'random': The value of a_i_j are in interval (minimum_value, minimum_value) 
                    randomly distributed 
                'normal': The value of a_i_j (i==j) are equal to 1. The value of a_i_j (i!=j) 
                    are normal distributed, the distribution correspond with N(mu,sigma) 
                    normal distirbution, where the mu is the average value of the a_i,j (i!=j) , 
                    and the sigma is the variance of the a_i_j (i!=j).

            max_min: max_min = (minimum_value, minimum_value), are used when the  mixing_type
                is 'random'

            mu_sigma: mu_sigma = (mu, sigma), are used when the mix_type is 'normal'

        # Output:

            Mixing matrix A.
        '''
        if source_number is None:
            source_number = np.shape(S)[0]
        A = np.zeros([source_number, source_number])
        if source_number < 2:
            raise ValueError(
                'Error - mixing matrix : The number of the sources must more than 1!')
        if mixing_type == "random":
            A = np.ones((source_number, source_number), np.float)
            for i in range(source_number):
                for j in range(source_number):
                    if i != j:
                        A[i, j] = max_min[1] + \
                            (max_min[0]-max_min[1])*random.random()
        elif mixing_type == "normal":
            for i in range(source_number):
                for j in range(source_number):
                    _random_number = abs(np.random.normal(
                        mu_sigma[0], mu_sigma[1], 1))
                    while(_random_number >= 0.99):
                        _random_number = abs(np.random.normal(
                            mu_sigma[0], mu_sigma[1], 1))
                    A[i, j] = _random_number
            for i in range(source_number):
                A[i, i] = 1
        return A

    def generate_matrix_S_A_X(self, folder_address, wav_range, source_number, mixing_type="random", max_min=(1, 0.01), mu_sigma=(0, 1)):
        '''
        # generate_matrix_S_A_X(self, folder_address, wav_range, source_number, 
        # mixing_type="random", max_min=(1, 0.01), mu_sigma=(0, 1)):

        # Usage:

            Generate the mixing matrix S,A,X according to the size of the source 
            signal matrix S

        # Parameters:

            folder_address: Define folder adress, in which the *.wav files exist. 
                The wav files must have only 1 channel.

            duration: The duration of the output original signals, 
                i.e. the whole time domain of the output matrix S

            source number: The number of the source signals in matrix S 

            mixing_type:
                'random': The value of a_i_j are in interval (minimum_value, minimum_value) 
                    randomly distributed 
                'normal': The value of a_i_j (i==j) are equal to 1. The value of a_i_j (i!=j) 
                    are normal distributed, the distribution correspond with N(mu,sigma) 
                    normal distirbution, where the mu is the average value of the a_i,j (i!=j) , 
                    and the sigma is the variance of the a_i_j (i!=j).

            max_min: max_min = (minimum_value, minimum_value), are used when the  mixing_type
                is 'random'

            mu_sigma: mu_sigma = (mu, sigma), are used when the mix_type is 'normal'

        # Output:

            Matrix S, A, X.
            The shape of the S and X are (source number, time slots number), 
            the shape of A is (time slots number, time slots number), the wav files are 
            randomly selected to generate the matrix S, A, X.
        '''
        S = self.wavs_to_matrix_S(folder_address, wav_range, source_number)
        A = self.generate_matrix_A(S, mixing_type, max_min, mu_sigma)
        X = np.dot(A, S)
        return S, A, X
    
    def cep_distance(self, S, hat_S):
        a_ni = [[0]*11 for _ in range(11)]
        a_i = [0]*11
        E = [0]*10
        R = [0]*11
        SampleRate = 16000
        size = len(S)
        window = int(SampleRate * 0.02)
        FrameSize = int(size // window)
        
        def calculate_R(data, frame):
            for k in range(11):
                R[k] = 0
                for m in range(frame * window,(frame + 1) * window - k):
                    R[k] += (data[m] * data[m + k])
            return 1

        def give_E(n):
            if n == 0:
                print('error!')
            if n == 1:
                E[0] = R[0]
            E[n] = (1 - math.pow(a_ni[n][n], 2)) * E[n - 1]
            return E[n]

        def give_a(n, i):
            if (n == 1) and (i == 1):
                if R[0] != 0:
                    a_ni[1][1] = R[1] / R[0]
                else:
                    a_ni[1][1] = R[1]
            elif n == i:
                sum = 0;
                for j in range(1,n):
                    sum += (a_ni[n - 1][j] * R[n - j])
                a_ni[n][n] = R[n] - sum
                give_E(n - 1)
                if E[n - 1] != 0:
                    a_ni[n][n] /= E[n - 1]
            else:
                a_ni[n][i] = a_ni[n - 1][i] - a_ni[n][n] * a_ni[n - 1][n - i]
            return a_ni[n][i]

        def set_a(data, frame):
            calculate_R(data, frame)
            for n in range(1,11):
                for i in range(n,0,-1):
                    give_a(n, i)
                    if n == 10:
                        a_i[i] = a_ni[n][i]
            return 1

        def give_c(data, c_n, L, frame):
            set_a(data, frame)
            c_n[0] = 0
            c_n[1] = a_i[1]
            for n in range(2,L+1):
                sum = 0
                for k in range(1,n):
                    if (k <= 10):
                        sum += (n - k) * c_n[n - k] * a_i[k]
                c_n[n] = 1 / n * sum
                if (n <= 10):
                    c_n[n] = c_n[n] + a_i[n]

        N = FrameSize
        L = 10
        D = 0
        for n in range(FrameSize):
            c_undist = [0]*(L + 1)
            c_dist = [0]*(L + 1)
            give_c(S, c_undist, L, n)
            give_c(hat_S, c_dist, L, n)
            F = 0
            for k in range(1,L+1):
                F += math.pow(c_undist[k] - c_dist[k], 2)
            F *= 2
            F = np.sqrt(F)
            D += F
        D /= N
        return D

    def mos_score(self, S, hat_S):
        D_cep = self.cep_distance(S,hat_S)
        return 3.56 - 0.8 * D_cep + 0.04 * (D_cep ** 2) 

    def fast_psnr(self, S, hat_S):
        '''
        # fast_psnr(self, S, hat_S):

        # Usage:

            Calculate the psnr of the estimated source signals (matrix hat_S)

        # Parameters:

            S: Reference source signal (matrix S)

            hat_S: Estimated source signal (matrix hat_S)

        # Output:

            The mean value of psnr of each sources
        '''
        original_hat_S = hat_S
        S = np.dot(np.diag(1/(np.max(abs(S), axis=1))), S)
        hat_S = np.dot(np.diag(1/(np.max(abs(hat_S), axis=1))), hat_S)
        amplitude_signal = 0
        amplitude_noise = 0
        sorted_hat_S = []
        for _source in S:
            _differences = []
            for _hat_source in hat_S:
                _differences.append(
                    np.sum(np.abs(np.abs(_source)-np.abs(_hat_source))))
            _row_index = int(np.argmin(_differences))
            sorted_hat_S.append(original_hat_S[_row_index])
            amplitude_noise += np.min(_differences)
            amplitude_signal += np.sum(np.abs(_source))
        if amplitude_noise == 0:
            #raise ValueError('Error - SNR : No noise exists!')
            return np.inf, S
        SNR = 20 * np.log10(amplitude_signal / amplitude_noise)
        return SNR, np.asarray(sorted_hat_S)

    def bss_evaluation(self, S, hat_S, type='fast_psnr'):
        '''
        # fast_psnr(self, S, hat_S):

        # Usage:

            Calculate the psnr, sdr, sir, sar, perm of the estimated 
            source signals (matrix hat_S)

        # Parameters:

            S: Reference source signal (matrix S)

            hat_S: Estimated source signal (matrix hat_S)

            type: 
                'fast_psnr': calculate the mean value of psnr of each source
                'sdr': calculate the mean value of sdr of each source
                'sir': calculate the mean value of sir of each source
                'sar': calculate the mean value of sar of each source
                'perm': calculate the mean value of perm of each source

        # Output:

            The mean value of psnr, sdr, sir, sar, perm of each source

        # Note:

            The type 'fast_psnr' is much faster than others. For the number of
            the sources are more than 5, it is better to use 'fast_psnr'
        '''
        psnr, hat_S = self.fast_psnr(S, hat_S)
        #hat_S = np.abs(hat_S)
        #S = np.abs(S)
        S = 32768 * np.dot(np.diag(1/(np.max(abs(S), axis=1))), S)
        hat_S = 32768 * np.dot(np.diag(1/(np.max(abs(hat_S), axis=1))), hat_S)
        if type == 'cep':
            ceps = [self.cep_distance(S[i],hat_S[i]) for i in range(S.shape[0])]
            return np.mean(ceps)
        elif type == 'mos_cep':
            mos_ceps = [self.mos_score(S[i],hat_S[i]) for i in range(S.shape[0])]
            return np.mean(mos_ceps)
        elif type == 'mos_lqo':
            mos_lqos = []
            for i in range(S.shape[0]):
                try:
                    mos_lqos += [pesq(16000, S[i],hat_S[i], 'wb')]
                except Exception:
                    pass
            #mos_lqos = [pesq(16000, S[i],hat_S[i], 'wb') for i in range(S.shape[0])]
            return np.mean(mos_lqos)
        elif type == 'psnr':
            return psnr
        sdr, isr, sir, sar, perm = museval.metrics.bss_eval(S, hat_S)
        if type == 'sdr':
            return np.mean(sdr)
        elif type == 'sir':
            return np.mean(sir)
        elif type == 'sar':
            return np.mean(sar)
        elif type == 'perm':
            return np.mean(perm)
        else:
            raise ValueError(
                'Error - bss evaluation : False type, the type must be psnr, sdr, sir, sar or perm.')

# pyfastbss testbed
pybss_tb = PyFastbssTestbed()