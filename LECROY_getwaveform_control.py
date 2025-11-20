

####LECROY的示波器控制程序




import TeledyneLeCroyPy
import numpy as np
import time, datetime

visaResourceAddr = 'TCPIP::192.168.137.6::inst0::INSTR'

o = TeledyneLeCroyPy.LeCroyWaveRunner(visaResourceAddr)


print(o.idn) # Prings e.g. LECROY,WAVERUNNER9254M,LCRY4751N40408,9.2.0


def get_wavedesc():
    o.write('CORD HI')  # High-Byte first
    o.write('COMM_FORMAT DEF9,WORD,BIN')  # Communication Format: DEF9 (this is the #9 specification; WORD (reads the samples as 2 Byte integer; BIN (reads in Binary)
    o.write('CHDR OFF')  # Command Header OFF (fewer characters to transfer)
    o.write('C1:WF? DESC')
    # time.sleep(.1)
    raw_bytes = o.resource.read_raw()
    raw_bytes = raw_bytes[16:]
    wavedesc_dict = TeledyneLeCroyPy.parse_wavedesc_block(raw_bytes)
    return wavedesc_dict

def get_accu_num():
    data = get_wavedesc()
    accu_num = data['SWEEPS_PER_ACQ']
    return accu_num

def save_wave(file_path):
    data = o.get_waveform(n_channel=1)
    t, v = data['waveforms'][0]['Time (s)'], data['waveforms'][0]['Amplitude (V)']
    accu_num = data['wavedesc']['SWEEPS_PER_ACQ']
    print(accu_num)
    acqs_num_str = str(round(accu_num / 1000.0, 1)) + 'k'
    if file_path.endswith('.sV'):
        file_path.replace('.sV', acqs_num_str + '.sV')
    else:
        file_path = file_path + '_' + acqs_num_str + '.sV'
    np.savetxt(file_path, np.column_stack((t, v)), fmt='%.6e')


def print_current_accu_num():
    global old_accu_num, old_accu_time
    new_accu_time = time.time()
    new_accu_num = get_accu_num()
    if old_accu_num:
        delta_time = new_accu_time - old_accu_time
        delta_accu_num = new_accu_num - old_accu_num
        print(f'current accu num: {new_accu_num},距离上一次时间经过:{delta_time:.1f}s,采集速率:{delta_accu_num/delta_time:.0f}次/s')
    else:
        print(f'current accu num: {new_accu_num}')
    old_accu_num = new_accu_num
    old_accu_time = new_accu_time

def clear_current_accu():
    o.write('CLSW')
    print('cleared')

def check_length():
    data = get_wavedesc()
    length = data['WAVE_ARRAY_COUNT']
    print(length)


old_accu_time = 0
old_accu_num = 0
while True:
    try:
        text = input('file path?:')
        if text:
            if text == 'q':
                break
            elif text == 'an' or text == 'a':
                print_current_accu_num()
            elif text == 'c' or text == 'clear':
                clear_current_accu()
            elif text == 'cl':
                check_length()
            else:
                save_wave(text)
    except Exception as e:
        print('error!', e)
        break