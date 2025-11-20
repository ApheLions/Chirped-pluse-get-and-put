import numpy as np
import matplotlib.pyplot as plt
import pyperclip
import sys


start_freq=5250###MHz
end_freq=6000 ###MHz
frame_num=20   #one pulse valve n chirp


#####!!!!!!!!!! all in us
chirp_width=2
amp=1

m1_width=0.5

m2_width=0.5
gap_m2_nextm1=10  #FID收集时长

sampling_rate=25E9   #awg sampling rate
################!!!!!!!!!
###########################################
gap_m1_chirp = 0
gap_chirp_m2 = 0

start_shift = 1   #chirp start time delay
end_shift = 0


chirp_ratio=1
chirp_former_seg=1
if chirp_former_seg<1:
    chirp_ratio=2*chirp_former_seg-1


fir_dir=r"C:\Users\Public\Documents\for_remote\chirp_test_CH2OO"
fir_dir+='\\'

def output_time_range():      ##返回chirp m1 m2 的时间序列
    time_range_chirp = []
    time_range_m1 = []
    time_range_m2 = []

    start_shift_info=(0,start_shift,0)
    time_range_chirp.append(start_shift_info) #####起始0的部分

    time_tail=0+start_shift
    i=0
    while i< frame_num:
        time_head = time_tail
        time_tail = time_head + chirp_width
        chirp_info = (time_head, time_tail, (start_freq,end_freq))  #####逐段写入时间序列 item即为chirp范围
        time_range_chirp.append(chirp_info)
        time_range_m1.append((time_head - m1_width - gap_m1_chirp, time_head - gap_m1_chirp, 1))
        time_range_m2.append((time_tail+gap_chirp_m2,time_tail+gap_chirp_m2+m2_width,1))    #####这里把m1 m2值为1的时间序列也生成

        time_head = time_tail
        time_tail = time_head + chirp_gap
        chirp_gap_info = (time_head, time_tail, 0)  #####把chirp之间空置的部分也逐段写入
        time_range_chirp.append(chirp_gap_info)
        i+=1

    time_head = time_tail
    time_tail = time_head+ end_shift
    end_shift_info=(time_head,time_tail,0) #####末尾0的部分
    time_range_chirp.append(end_shift_info)

    return time_range_chirp,time_range_m1,time_range_m2   ######这里波形部分是完整的时间序列,但m1 m2的只有值为1的
                                                    ######### time_range的格式是(start,end,info) 之后会用分段函数以及分支语句去操作生产波形
def fill_m1_m2_time_range(time_range):
    filled_m_range=[]
    start_time=0
    for interval in time_range:
        start,end=interval[0],interval[1]
        if start_time<start:
            filled_m_range.append((start_time,start,0))
        filled_m_range.append(interval)
        start_time=end

    filled_m_range.append((start_time,t_total,0))
    return filled_m_range

def make_chirp(time,info,ratio=chirp_ratio,seg_set=chirp_former_seg):   ############仅output_wave调用 是一个分段函数函数体的部分
    #####如需输出强度线性变换的chirp，请设置ratio

    band_chirp_start, band_chirp_end = info
    k = (band_chirp_end - band_chirp_start) / time  ####chirp变化率
    t=np.linspace(0,time,int(sampling_rate * time*1e-6))
    if ratio!=1:
        ratio_amp=np.linspace(ratio,1,len(t))
    else:
        ratio_amp=np.ones(len(t))
    if seg_set!=1:

        for n,m in enumerate(t):
            if m<2.0:
                ratio_amp[n]=seg_set

    return ratio_amp*amp*np.cos(2 * np.pi * t * (band_chirp_start + 0.5 * k * t))


def output_wave(time_range):   ####### 根据时间序列产生波形

    wave = np.array([])
    sub_wave= np.array([])
    for item in time_range:
        # print(item)
        lens=int((item[1]-item[0])*sampling_rate/1e6)
        # print('lens='+str(lens)+'sss')
        if item[2]==0:
            sub_wave=np.zeros(lens)
        elif item[2]==1:
            sub_wave = np.ones(lens)
        else:
            sub_wave = make_chirp(item[1]-item[0],item[2])
        if len(sub_wave)%2==1:
            sub_wave.append(sub_wave[-1])
        wave = np.append(wave, sub_wave)

    return wave

def single_mk(m_time_range):
    lst_of_m_time_range = [list(t) for t in m_time_range]
    for item in lst_of_m_time_range[2:]:
        item[2]=0

    return lst_of_m_time_range


def pad_with_zeros(arr, target_len):
    current_len = len(arr)
    if current_len >= target_len:
        return arr  # 如果已经足够长或更长，则直接返回

    # 创建一个新数组，用0填充，并确保数据类型一致
    # np.zeros(shape, dtype)
    padded_arr = np.zeros(target_len, dtype=arr.dtype)

    # 将原始数据复制到新数组的前面
    padded_arr[:current_len] = arr
    return padded_arr

def on_mouse(event):   ###绘图后按下中间，复制当前坐标

    if event.button == 2 and event.inaxes:
        x_coord = event.xdata
        pyperclip.copy(str(x_coord))


chirp_gap=gap_m2_nextm1+gap_m1_chirp+m2_width+gap_chirp_m2

t_total=start_shift+end_shift+(chirp_width+chirp_gap)*frame_num

chirp_time_range,m1_time_range,m2_time_range=output_time_range()
m1_time_range=fill_m1_m2_time_range(m1_time_range)
m2_time_range=fill_m1_m2_time_range(m2_time_range)   ###########生产时间序列


##########################自定义时间序列

# chirp_time_range=[(0, 1, 0),  (1, 5, (6425, 7175)) ,(5, 25.5, 0),  (133.0, 134.5, (7425, 8175)), (25.5, 29.5, (6425, 7175)),(29.5, 50.0, 0)`]
#
# m1_time_range=[(0, 0.5, 0), (0.5, 1, 1), (1, 22.5, 0), (22.5, 23.0, 1), (23.0, 44.5, 0), (44.5, 45.0, 1), (45.0, 66.5, 0), (66.5, 67.0, 1), (67.0, 88.5, 0), (88.5, 89.0, 1), (89.0, 110.5, 0), (110.5, 111.0, 1), (111.0, 132.5, 0), (132.5, 133.0, 1), (133.0, 154.5, 0)]
#
# m2_time_range=[(0, 0.5, 0),(0.5, 1.0, 1),(1.0, 154, 0)]
#
# t_total=160
#
# sample_dot=np.arange(len(t))
#################################

# m2_time_range=m1_time_range
# m2_time_range=single_mk(m2_time_range)



t=np.linspace(0,t_total,int(sampling_rate * t_total*1e-6))  ###########这里的t_total是us
if len(t)%2==1:
    t.append(t[-1])
sample_dot=np.arange(len(t))
V = output_wave(chirp_time_range)

# sys.exit()
M1=output_wave(m1_time_range)
M2=output_wave(m2_time_range)

V = pad_with_zeros(V, len(t))
M1 = pad_with_zeros(M1, len(t))
M2 = pad_with_zeros(M2, len(t))

output_data = np.column_stack((V, M1, M2))

fig, ax = plt.subplots()
ax.plot(sample_dot,V,label="waveform")
ax.plot(sample_dot, M1-1.2,label="M1")
ax.plot(sample_dot, M2-2.4,label="M2")
plt.legend(loc=1)
fig.canvas.mpl_connect('button_press_event', on_mouse)
plt.show()
print("正在写入》》》")
print(" 请等待》》》")

file_name = f"{start_freq}MHz-{end_freq}MHz_{frame_num}frames_{gap_m2_nextm1}us_{chirp_width}uschirp-{sampling_rate/1e9}G.txt"
if chirp_former_seg!=1:
    file_name=file_name[:-4]+'set_'+str(chirp_former_seg)+'.txt'

np.savetxt(fir_dir+file_name, output_data, fmt='%.8f %d %d')
print(file_name)

