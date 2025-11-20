############ LECROY的自动采集程序
############ 采集的时域信号为 .sV格式
############ 自动采集时会有独立的小窗口，勿关 （若关闭采集会停止，请重启程序）



import threading
import TeledyneLeCroyPy
import numpy as np
import time
from datetime import datetime
import sys
import tkinter as tk
from tkinter.scrolledtext import ScrolledText
from tkinter import font
visaResourceAddr = 'TCPIP::192.168.137.6::inst0::INSTR'

os = TeledyneLeCroyPy.LeCroyWaveRunner(visaResourceAddr)

acqs_accu_num = 100000
save_file_dir = r'D:\Data\251118_laser_nozzle_test\nomal'
save_file_name = '251118_laser_test_CH2F2_6bar'

instant_acq_num=0
total_acq_num=0

def get_wavedesc():
    os.write('CORD HI')  # High-Byte first
    os.write('COMM_FORMAT DEF9,WORD,BIN')  # Communication Format: DEF9 (this is the #9 specification; WORD (reads the samples as 2 Byte integer; BIN (reads in Binary)
    os.write('CHDR OFF')  # Command Header OFF (fewer characters to transfer)
    os.write('C1:WF? DESC')
    # time.sleep(.1)
    raw_bytes = os.resource.read_raw()
    raw_bytes = raw_bytes[16:]
    wavedesc_dict = TeledyneLeCroyPy.parse_wavedesc_block(raw_bytes)
    return wavedesc_dict

def get_accu_num():
    data = get_wavedesc()
    accu_num = data['SWEEPS_PER_ACQ']
    return accu_num

def clear_current_accu():
    os.write('CLSW')
    print('cleared')

def save_wave(file_path):
    print(file_path)
    data = os.get_waveform(n_channel=1)
    t, v = data['waveforms'][0]['Time (s)'], data['waveforms'][0]['Amplitude (V)']

    accu_num = data['wavedesc']['SWEEPS_PER_ACQ']
    print(accu_num)
    acqs_num_str = str(round(accu_num / 1000.0, 1)) + 'k'
    if file_path.endswith('.sV'):
        file_path.replace('.sV', acqs_num_str + '.sV')
    else:
        file_path = file_path + '_' + acqs_num_str + '.sV'
    np.savetxt(file_path, np.column_stack((t, v)), fmt='%.6e')

print(os.idn)


def auto_function():

    root = tk.Tk()
    root.title("正在采集...   请勿关闭 🚀")


    my_font = font.Font(family="微软雅黑", size=14)



    text_box = ScrolledText(root, width=50, height=10, font=my_font)
    text_box.pack(expand=True, fill='both')  # 允许窗口大小改变

    def update_text():
        global instant_acq_num
        try:
            num = get_accu_num()
            sample_rate = (num - instant_acq_num) / 2
            if sample_rate>200:
                sample_rate=0
        except Exception as e:
            print(f"获取累计数失败: {e}")
            num = 0
            sample_rate = 0

        instant_acq_num = num
        current_time = datetime.now().strftime("%H:%M:%S")
        if instant_acq_num > acqs_accu_num:
            print("正在保存")
            global total_acq_num
            file_name_s = round(total_acq_num / 1000, 1)
            total_acq_num += acqs_accu_num
            file_name_e = round(total_acq_num / 1000, 1)
            filepath = save_file_dir + '\\' + save_file_name + '_' + str(file_name_s) + 'k-' + str(
                file_name_e) + 'k' + '.sV'
            save_wave(filepath)
            clear_current_accu()

        text_box.insert(tk.END, '⏰'+str(current_time) + '   当前采样数 : ' + str(instant_acq_num) + "  当前采样率 : " + str(sample_rate)+'\n')
        text_box.see(tk.END)  # 自动滚动到底部
        root.after(2000, update_text)  # 2秒后再次调用自己

    update_text()

    root.mainloop()



def main():

    thread = threading.Thread(target=auto_function, daemon=True)
    thread.start()

    while True:
        user_input = input().strip().lower()
        if user_input == 'q':
            print("退出程序...")
            sys.exit()
        # elif user_input == 'run':
        #     print("运行其他程序...")
        #     # 这里举例运行系统的计算器（Windows）
        #     # Linux/macOS请替换成相应命令
        #     try:
        #         subprocess.Popen('calc')  # Windows示例
        #     except Exception as e:
        #         print("运行失败:", e)
        else:
            print(f"未识别指令: {user_input}")

if __name__ == "__main__":
    print(f"当前保存文件夹 : {save_file_dir} ")
    main()

