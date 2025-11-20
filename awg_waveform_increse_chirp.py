##############  每段chirp内容不同 阶梯提升

import numpy as np
import matplotlib.pyplot as plt
import pyperclip
import sys




start_freq=4500
end_freq=10000
freq_gap=1100 #####!!!!!!!!!! all in MHz

amp=1
start_shift = 1
end_shift = 0
# chirp_gap=20     #####!!!!!!!!!! all in us
chirp_width=2

m1_width=0.5
gap_m1_chirp=0.0
m2_width=0.5          #####!!!!!!!!!! all in us
gap_chirp_m2=0.0
gap_m2_nextm1=7  ##### 示波器采集时间  chirp间隔等于 此值+m1_width+gap_m1_chirp+chirp_width+gap_chirp_m2
gap_m2_nextm1+=m1_width


sampling_rate=50E9






def output_freq_range():   ###############返回chirp的频率序列
    freq_tail=start_freq
    freq_range=[]
    while(freq_tail<end_freq):
        freq_head=freq_tail
        freq_tail=freq_head+freq_gap
        range=(freq_head,freq_tail)
        freq_range.append(range)

    return freq_range

def output_time_range():      ##返回chirp m1 m2 的时间序列
    time_range_chirp = []
    time_range_m1 = []
    time_range_m2 = []

    start_shift_info=(0,start_shift,0)
    time_range_chirp.append(start_shift_info) #####起始0的部分

    time_tail=0+start_shift
    for i,item in enumerate(freq_range): #####遍历chirp的频率序列
        time_head = time_tail
        time_tail = time_head + chirp_width
        chirp_info=(time_head,time_tail,item) #####逐段写入时间序列 item即为chirp范围

        time_range_chirp.append(chirp_info)
        time_range_m1.append((time_head-m1_width-gap_m1_chirp,time_head-gap_m1_chirp,1))
        time_range_m2.append((time_tail+gap_chirp_m2,time_tail+gap_chirp_m2+m2_width,1))    #####这里把m1 m2值为1的时间序列也生成

        time_head=time_tail
        time_tail=time_head+chirp_gap
        chirp_gap_info=(time_head,time_tail,0)  #####把chirp之间空置的部分也逐段写入
        time_range_chirp.append(chirp_gap_info)

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


def make_chirp(time_start,time_end,info):   ############仅output_wave调用 是一个分段函数函数体的部分
    if info == 0:
        return lambda t: 0
    elif info ==1:
        return lambda t: 1
    else:
        # print(time_start,time_end,info)
        band_chirp_start, band_chirp_end = info
        k=(band_chirp_end-band_chirp_start)/(time_end-time_start)   #####chirp的变化率
        return lambda t: amp*np.cos(2 * np.pi * t * (band_chirp_start -k * time_start + 0.5 * k * t))  ######f(t)=f0+(t-t0)*k



def output_wave(time_range):   ####### 根据时间序列产生波形
    conditions = []
    funcs = []
    for i, (start, end, info) in enumerate(time_range):
        if i < len(time_range) - 1:
            cond = (t >= start) & (t < end)  #######左闭右开
        else:
            cond = (t >= start) & (t <= end)  #######最后一段包含右端点
        conditions.append(cond)  ############### 根据condition去分段
        funcs.append(make_chirp(start,end,info))
    return np.piecewise(t, conditions, funcs)    ##########分段函数

def single_mk(m_time_range):
    lst_of_m_time_range = [list(t) for t in m_time_range]
    for item in lst_of_m_time_range[2:]:
        item[2]=0

    return lst_of_m_time_range

def on_mouse(event):

    if event.button == 2 and event.inaxes:
        x_coord = event.xdata
        pyperclip.copy(str(x_coord))

def band_repeat(nparr,repeat_num,pad=0):
    repeat_arr=np.tile(nparr,repeat_num)

    #重复的时候为了均匀 把末尾一截给舍掉了，这是因为开头有为0的部分，即为start_shift,此时考虑是否补0
    if pad!=0:

        zero_length=int(pad*sampling_rate*1e-6)  #在此处为us，所以乘因子
        repeat_arr = np.pad(repeat_arr, (0, zero_length), mode='constant', constant_values=0)

    return repeat_arr


if __name__ == '__main__':

    chirp_gap=gap_m2_nextm1+gap_m1_chirp+m2_width+gap_chirp_m2
    # print(chirp_gap)
    # sys.exit()
    frame_num=(end_freq-start_freq)/freq_gap
    t_total=start_shift+end_shift+(chirp_width+chirp_gap)*frame_num    ######计算这些具体的值

    ##########此处为了重复 减去尾巴
    # t_total-=start_shift


    # print(t_total)
    # sys.exit()
    t=np.linspace(0,t_total,int(sampling_rate * t_total*1e-6))  ###########这里的t_total是us


    freq_range=output_freq_range()
    chirp_time_range,m1_time_range,m2_time_range=output_time_range()
    m1_time_range=fill_m1_m2_time_range(m1_time_range)
    # m2_time_range=fill_m1_m2_time_range(m2_time_range)   ###########生产时间序列

    m2_time_range=m1_time_range
    m2_time_range=single_mk(m2_time_range)

    # for t in chirp_time_range:
    #     print(t)
    #
    # for t in m2_time_range:
    #     print(t)

    # chirp_time_range=chirp_time_range[:-1]
    # chirp_time_range[-1]=(43.0, 50.0, 0)
    # m1_time_range[-1]=(41.0, 50.0, 0)
    # m2_time_range[-1]=(41.0, 50.0, 0)
    # print(chirp_time_range[-1])
    # print(m1_time_range[-1])
    # print(m2_time_range[-1])
    #
    #
    # sys.exit()

    # for i in chirp_time_range:
    #     print(i)
    # sys.exit()
####################################################################
    #######自定义chirp
    # chirp_time_range[1]= (1, 3, (4340,5090))
    #
    # chirp_time_range[3] =   (11.0, 13.0, (4635,5385))
    #
    # chirp_time_range[5] = (21.0, 23.0, (4685, 5435))
    #
    # chirp_time_range[7] = (31.0, 33.0, (4340,5090))
    #
    # chirp_time_range[9] = (41.0, 43.0, (4340,5090))
    #
    # for i in chirp_time_range:
    #     print(i)
    # sys.exit()
#########################################################################
    V = output_wave(chirp_time_range)
    M1=output_wave(m1_time_range)
    M2=output_wave(m2_time_range)

    repeat=5
    V=band_repeat(V,repeat,0)
    M1=band_repeat(M1,repeat,0)
    M2=band_repeat(M2,repeat,0)
    #######重复n次

    #######

    sample_dot = np.arange(len(V))

    output_data = np.column_stack((V, M1, M2))


    # sample_dot=band_repeat(sample_dot,3)


    fig, ax = plt.subplots()
    ax.plot(sample_dot,V,label="waveform")
    ax.plot(sample_dot, M1-2.2,label="M1")
    ax.plot(sample_dot, M2-3.4,label="M2")
    plt.legend(loc=1)
    fig.canvas.mpl_connect('button_press_event', on_mouse)
    plt.show()
    fir_dir = r"C:\Users\mw304\Desktop\awg\0908_input" + '\\'
    file_name = str(start_freq) + 'MHz-' + str(end_freq) + 'MHz_' + str(frame_num) + 'frames_'  + 'x'+str(repeat)+'.txt'
    print(file_name)
    np.savetxt(fir_dir + file_name, output_data, fmt='%.8f %d %d')

