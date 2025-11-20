
import faster_FFT_for_single_wave_cxl_update as FFT
import sys
import numpy as np
import time
from spectrum_plot import plotter
import matplotlib.pyplot as plt
time_start = time.perf_counter()

t_domain_file=r"C:\Users\mw304\Desktop\awg\shiyu\time_domain_1frame.txt"

try:#用于其他脚本调用，如average_and_FFT.py
    t_domain_file =sys.argv[1]

    print(t_domain_file)
except IndexError:
    pass


# t,V=np.loadtxt(t_domain_file,usecols=(0,1),unpack=True,delimiter=',')
t,V=np.loadtxt(t_domain_file,usecols=(0,1),unpack=True)

fid_gap=10*1e-6
end=acq=10.21*1e-6
acq_len=7.45*1e-6



frame=5
start_freq=18000
freq_step=3000

time_intervals=[]
freq_intervals=[]
for i in range(frame):
    time_intervals.append((end-acq_len,end))
    end+=fid_gap
    freq_intervals.append((start_freq,freq_step+start_freq))
    start_freq+=freq_step

# time_intervals[2]=(23.11e-6,30.21e-6)

print('选择的时间范围为：')
for tt in time_intervals:
    print(f'   {tt}')

groups = []


plt.plot(t, V, )

for item in time_intervals:
    plt.axvspan(item[0], item[1], color='yellow', alpha=0.5)

plt.title("Time Domain Spectrum")
plt.text(0.00002, 0, "黄色区域为选定的傅里叶变换范围，关闭此图即开始进行傅里叶变换", ha='center', va='bottom', fontsize=12, color='black')
plt.show()



for start, end in time_intervals:
    # 找出t中满足 start <= t <= end 的索引布尔数组
    mask = (t >= start) & (t <= end)


    t_sub = t[mask]
    V_sub = V[mask]

    groups.append((t_sub, V_sub))

freq=np.array([])
insi=np.array([])

for i in freq_intervals:

    print(i)
# sys.exit()




for i, (t_sub, V_sub) in enumerate(groups):

    # print(len(t_sub))
    # print(t_sub[0],t_sub[-1])
    sub_freq,sub_ins=FFT.FFT_array(V_sub, start_freq=freq_intervals[i][0], end_freq=freq_intervals[i][-1],orsampling_rate=80E9)
    freq=np.append(freq,sub_freq)
    insi=np.append(insi,sub_ins)

    # print(len(freq))

graph=plotter(freq, insi)
graph.plot_xy()
graph.show()

# print(len(freq))

# plt.plot(freq,insi)
# plt.show()
out = np.zeros((np.size(freq), 2))
out[:, 0] = freq
out[:, 1] = insi
save_filename=t_domain_file[:-4]+'_fft.dat'
np.savetxt(save_filename, out, delimiter='\t')
time_end = time.perf_counter()

print(f"程序运行时间：{time_end - time_start} 秒")
