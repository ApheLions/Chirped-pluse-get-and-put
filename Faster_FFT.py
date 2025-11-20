#######################################
#用于傅里叶变换单个文件
#多个脚本引用此中函数，谨慎改动
#采样率自动识别，但只适应于目前的采样方式，如果有改变需要变动
#######################################


import os.path
import scipy.fftpack
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.widgets as widgets
import sys
from spectrum_plot import plotter
import time

sampling_rate = 25E9  # GS/s uncomment this line to switch to 2-8
# sampling_rate = 50E9  # GS/s uncomment this line to switch to 8-16
# sampling_rate = 80E9
#################################
file_path = r"E:\Data\250503_CH2I2+O2+SO2\+H2O\250503_CH2I2+O2+SO2+H2O_1200V_helm_Ne_960us_delay_(0-410w)average.txt"
#################################
# str='newos'

##################################
try:#用于其他脚本调用，如average_and_FFT.py
    data =sys.argv[1]
    file_path=data
    print("FFt被调用")
except IndexError:
    pass
#################################


# is_newocs=0
# if 'newos' in file_path:
#     is_newocs=1
#     sampling_rate = 80E9
#     print('sampling_rate'+' : '+str(sampling_rate))
# # s=input()


def FFT(file_path, FID_start=0.0, FID_stop=999.9, save_suffix='_FFT', no_window=False, zero_padding=0, interp=False, max_rows=None):
    # if save_suffix, then save else not save
    directory = os.path.dirname(file_path)
    file_name_ = os.path.basename(file_path)

    # if is_newocs:   ####################for SDA ocs read file

        # with open(file_path, 'r') as f:  # 打开文件并跳过前5行
        #     pr_text=15
        #     print("跳过前"+str(pr_text)+'行')
        #     for _ in range(pr_text):
        #         next(f)
        #
        #     times,signal=np.loadtxt(f,  delimiter=',',usecols=(0, 1), unpack=True)
        # times, signal = np.loadtxt(file_path, delimiter=' ', usecols=(0, 1), unpack=True)
    # else:
    with open(file_path) as f:
        signal = np.loadtxt(f, usecols=-1, max_rows=max_rows)
    times=np.loadtxt(file_path,usecols=(0,))
    global sampling_rate
    if times[1]-times[0] < 1.5e-11:
        sampling_rate=80E9

    elif times[1]-times[0] > 3e-11:
        sampling_rate = 25E9
    else:
        sampling_rate = 50E9
    print(sampling_rate)

    print(file_name_)
    newosfreqin6to18=0
    if 'new8_16' in file_path:
        newosfreqin6to18=1
    freqs, ft = FFT_array(signal, FID_start, FID_stop, no_window, zero_padding, interp,newosfreqin6to18)


    if save_suffix:
        out = np.zeros((np.size(freqs), 2))
        out[:, 0] = freqs
        out[:, 1] = ft
        # save_filename = directory + '\\' + file_name_ + '_' + 'FFT.dat'
        save_filename = os.path.join(directory, file_name_) + save_suffix + ('_no_window.dat' if no_window else '.dat')
        f = np.savetxt(save_filename, out, delimiter='\t')
        print(save_filename)
    return freqs, ft


def FFT_array(signal, FID_start=0.0, FID_stop=999.9, no_window=False, zero_padding=0, interp=False,newosfreqin6to18=0,start_freq=4800,end_freq=19000,orsampling_rate=0):
    """

    :param signal:
    :param FID_start:
    :param FID_stop:
    :param no_window:
    :param zero_padding: if -1, zero padding to two times size, else other ,unit us
    :param interp: interpolate array to double length6
    :return:
    """
    # origin, window is peformed after padding, now padding first, then window, then padding

    global sampling_rate
    if orsampling_rate!=0:
        sampling_rate=orsampling_rate

    print("sampling_rate = "+str(sampling_rate))
    print("start_freq = " + str(start_freq))
    print("end_freq = " + str(end_freq))

    signal = signal[round(sampling_rate*1E-6 * FID_start):round(sampling_rate*1E-6 * FID_stop)]

    sampling_rate_factor = 1
    # todo: interp is not applied
    if interp:
        N = len(signal)
        X = np.arange(0, 2 * N, 2)
        X_new = np.arange(2 * N)
        signal = np.interp(X_new, X, signal)
        sampling_rate_factor = 2
    if zero_padding != -1:
        signal = np.pad(signal, (0, round(zero_padding * 1E-6 * (sampling_rate * sampling_rate_factor))), 'constant')
    else:
        signal = np.pad(signal, (0, np.size(signal)), 'constant')
    if no_window:
        window = 1
    else:
        window = np.kaiser(np.size(signal), 9.5)
    signal = signal * window
    signal = np.pad(signal, (0, np.size(signal)), 'constant')


    fft = abs(scipy.fftpack.fft(signal)) / (  ( np.size(signal)/(sampling_rate * sampling_rate_factor)*1E6-FID_start ) * (sampling_rate * sampling_rate_factor) * 1E-10 )
    freq = (scipy.fftpack.fftfreq(np.size(signal), 1 / (sampling_rate * sampling_rate_factor))) / 1E6


    # if sampling_rate<30E9 or sampling_rate>70E9:
    #     start_freq = 2000
    #
    #     end_freq = 10000
    # if newosfreqin6to18:
    #     start_freq = 6000
    #
    #     end_freq = 20000


    freq_spacing = (freq[100] - freq[0]) / 100
    start_idx, end_idx = round(start_freq/freq_spacing), round(end_freq/freq_spacing)
    freqs = freq[start_idx: end_idx]
    ft = fft[start_idx: end_idx]

    # for i, row in enumerate(freq):
    #     if row >= 2000 and row <= 10000:
    #         freqs.append(row)
    #         ft.append(fft[i])

    return freqs, ft


if __name__ == '__main__':
    # by default, no zero padding is performed
    # freqs, out = FFT(file_path, save_suffix='_FFT_zero_padding_to_50us', zero_padding=10)
    # freqs, out = FFT(file_path, save_suffix='_FFT_end_to_200us', FID_stop=200)

    freqs, out = FFT(file_path, save_suffix='_FFT')
    # freqs, out = FFT(file_path, save_suffix='_FFT_no_window', no_window=True)
    # freqs, out = FFT(file_path, save_suffix='_FFT_interp', interp=True)
    graph=plotter(freqs, out)
    graph.plot_xy()
    graph.show()
    # plt.xlim((5249.94, 5250.14))
    print("Check for plot, data has finished saving")
