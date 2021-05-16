# -*- coding: utf-8 -*-

# @Author: Shenyunbin
# @email : yunbin.shen@mailbox.tu-dresden.de / shenyunbin@outlook.com
# @create: 2021-04-25
# @modify: 2021-04-25
# @desc. : [description]

import numpy as np
import warnings

class ICANetwork():
    def __init__(self) -> None:
        self.max_iter = 200
        self.tol = 1e-4
        self.dynamic_adj_coef = 2
        self.grad_var_tol = 0.9
        self.proc_len_multiplier = self.dynamic_adj_coef
        pass

    # Pica 改进后的矩阵白化, 多了一个V的逆矩阵, 加快后面计算
    def _whiten_with_inv_v(self, X):
        X -= X.mean(axis=-1)[:, np.newaxis]
        A = np.dot(X, X.T)
        np.clip(A, 1e-15, None, out=A)
        D, P = np.linalg.eig(A)
        D = np.diag(abs(D))
        D_half = np.sqrt(np.linalg.inv(D))
        V = np.dot(D_half, P.T)
        V_inv = np.dot(P, np.sqrt(D))
        X1 = np.sqrt(X.shape[1]) * np.dot(V, X)
        return X1, V, V_inv

    # 来自于Fastica的tanh函数
    def _logcosh(self, x, alpha=1.0):
        x *= alpha
        gx = np.tanh(x, x)
        g_x = np.empty(x.shape[0])
        for i, gx_i in enumerate(gx):
            g_x[i] = (alpha * (1 - gx_i ** 2)).sum()
        return gx, g_x

    def _exp(self, x):
        exp = np.exp(-(x ** 2) / 2)
        gx = x * exp
        g_x = (1 - x ** 2) * exp
        return gx, g_x.sum(axis=-1)

    def _cube(self, x):
        return x ** 3, (3 * x ** 2).sum(axis=-1)

    # 来自于FastICA的去相关化
    def _sym_decorrelation(self, W):
        S, U = np.linalg.eigh(np.dot(W, W.T))
        np.clip(S, 1e-15, None, out=S)
        return np.linalg.multi_dot([U * (1. / np.sqrt(S)), U.T, W])

    # 来自于FastICA的牛顿迭代
    def _newton_iteration(self, W, X):
        gbx, g_bx = self._logcosh(np.dot(W, X))
        W1 = self._sym_decorrelation(np.dot(gbx, X.T) - g_bx[:, None] * W)
        lim = max(abs(abs(np.diag(np.dot(W1, W.T))) - 1))
        return W1, lim

    # Pica 带有梯度下降速率判断的GDR牛顿迭代

    def _ica_par(self, W, X, grad_var_tol):
        self.Stack = []
        _sum = 0
        _max = 0
        for _ in range(self.max_iter):
            W, lim = self._newton_iteration(W, X)
            self.Stack.append(lim)
            if lim < self.tol:
                break
            if lim > _max:
                _max = lim
            _sum += lim
            if _sum < grad_var_tol*0.5*(_max+self.Stack[-1])*len(self.Stack):
                break
        else:
            warnings.warn(
                'PICA did not converge. Consider increasing tolerance or the maximum number of iterations.')
        print('*** ica iter:',_)
        return W, lim

    def pica_nw(self, init_settings, ica_buf):
        # read settings
        proc_len = init_settings['proc_len']
        W = init_settings['W']
        proc_len_multiplier = init_settings['proc_len_multiplier']
        _X = ica_buf.extract_n(proc_len)
        _X, V, V_inv = self._whiten_with_inv_v(_X)
        W = self._sym_decorrelation(np.dot(W, V_inv))
        W, lim = self._ica_par(W, _X, self.grad_var_tol)
        W = np.dot(W, V)
        if lim < self.tol:
            proc_len_multiplier *= 2
        else:
            proc_len_multiplier //= 2
        proc_len *= proc_len_multiplier
        if lim < self.tol:
            proc_len_multiplier *= self.dynamic_adj_coef
        else:
            proc_len_multiplier = max(
                self.dynamic_adj_coef, proc_len_multiplier//self.dynamic_adj_coef)
        proc_len *= proc_len_multiplier
        # save settings
        init_settings['proc_len'] = proc_len
        init_settings['proc_len_multiplier'] = proc_len_multiplier
        init_settings['W'] = W
        

    def fastica_nw(self, init_settings, ica_buf):
        W = init_settings['W']
        _X =  getattr(ica_buf,'buffer')
        _X, V, V_inv = self._whiten_with_inv_v(_X)
        W = self._sym_decorrelation(np.dot(W, V_inv))
        W, _ = self._ica_par(W, _X, 0)
        init_settings['W'] = np.dot(W, V)
        


icanetwork = ICANetwork()