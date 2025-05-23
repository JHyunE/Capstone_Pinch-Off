import os
import csv
from datetime import datetime
import time

from util import bin16_to_hex4, hex4_to_bin16
from SPI import write_register, read_register
from SHT85 import getTempHumid

def save_settings_csv(log_folder, kp, ki, init_dco, freq, power, voltage_1_1, voltage_1_2, voltage_1_3, voltage_2_1, voltage_2_2, voltage_2_3, idx, temp, humid):
    os.makedirs(log_folder, exist_ok=True)
    path = os.path.join(log_folder, 'setting_log.csv')
    file_exists = os.path.isfile(path)
    with open(path, 'a', newline='') as csvfile:
        writer = csv.writer(csvfile)
        if not file_exists:
            writer.writerow(['index', 'kp', 'ki', 'init_dco', 'freq_Hz', 'power_dBm', 'voltage_INST1_CH1_V', 'voltage_INST1_CH2_V', 'voltage_INST1_CH3_V', 'voltage_INST2_CH1_V', 'voltage_INST2_CH2_V', 'voltage_INST2_CH3_V', 'Temperature', 'Humidity'])
        writer.writerow([idx, kp, ki, init_dco, freq, power, voltage_1_1, voltage_1_2, voltage_1_3, voltage_2_1, voltage_2_2, voltage_2_3, round(temp, 2), round(humid, 2)])
    return True, path

def append_marker_data(log_folder, freq_hz, amplitude_dbm, freq, voltage_1_1, voltage_1_2, voltage_1_3, voltage_2_1, voltage_2_2, voltage_2_3, idx):
    os.makedirs(log_folder, exist_ok=True)
    path = os.path.join(log_folder, 'marker_table.csv')
    file_exists = os.path.isfile(path)
    with open(path, 'a', newline='') as csvfile:
        writer = csv.writer(csvfile)
        if not file_exists:
            writer.writerow(['index', 'freq_Hz', 'voltage_INST1_CH1_V', 'voltage_INST1_CH2_V', 'voltage_INST1_CH3_V', 'voltage_INST2_CH1_V', 'voltage_INST2_CH2_V', 'voltage_INST2_CH3_V', 'peak_freq_Hz', 'amplitude_dBm', 'jitter_ps', 'sno_1kHz', 'sno_10kHz', 'sno_100kHz', 'sno_1MHz', 'sno_10MHz'])
        writer.writerow([idx, freq, voltage_1_1, voltage_1_2, voltage_1_3, voltage_2_1, voltage_2_2, voltage_2_3, freq_hz, amplitude_dbm])
    return True, path

def append_phase_data(log_folder, jitter, sno_1khz, sno_10khz, sno_100khz, sno_1mhz, sno_10mhz):
    path = os.path.join(log_folder, 'marker_table.csv')

    with open(path, 'r', newline='') as csvfile:
        rows = list(csv.reader(csvfile))

    header = rows[0]
    data_rows = rows[1:]

    last_row = data_rows[-1]

    while len(last_row) < len(header):
        last_row.append('')

    if 'jitter_ps' not in header:
        header.append('jitter_ps')
        last_row.append(jitter)
    else:
        idx_jitter = header.index('jitter_ps')
        last_row[idx_jitter] = jitter

    if 'sno_1kHz' not in header:
        header.append('sno_1kHz')
        last_row.append(sno_1khz)
    else:
        idx_1khz = header.index('sno_1kHz')
        last_row[idx_1khz] = sno_1khz

    if 'sno_10kHz' not in header:
        header.append('sno_10kHz')
        last_row.append(sno_10khz)
    else:
        idx_10khz = header.index('sno_10kHz')
        last_row[idx_10khz] = sno_10khz

    if 'sno_100kHz' not in header:
        header.append('sno_100kHz')
        last_row.append(sno_100khz)
    else:
        idx_100khz = header.index('sno_100kHz')
        last_row[idx_100khz] = sno_100khz

    if 'sno_1MHz' not in header:
        header.append('sno_1MHz')
        last_row.append(sno_1mhz)
    else:
        idx_1mhz = header.index('sno_1MHz')
        last_row[idx_1mhz] = sno_1mhz

    if 'sno_10MHz' not in header:
        header.append('sno_10MHz')
        last_row.append(sno_10mhz)
    else:
        idx_10mhz = header.index('sno_10MHz')
        last_row[idx_10mhz] = sno_10mhz

    data_rows[-1] = last_row

    with open(path, 'w', newline='') as csvfile:
        writer = csv.writer(csvfile)
        writer.writerow(header)
        writer.writerows(data_rows)
    return True, path

def measurement(
    init_dco_single,
    init_dco_sweep,
    dco_start,
    dco_stop,
    dco_step,
    en_dsm,
    dlf_mode,
    kp_single,
    kp_sweep,
    kp_start,
    kp_stop,
    kp_step,
    ki_single,
    ki_sweep,
    ki_start,
    ki_stop,
    ki_step,
    sau,
    sgu,
    psu1,
    psu2,
    log_path,
    capture_path,
    freq_sweep,
    freq_single,
    freq_start,
    freq_stop,
    freq_step,
    offset_start,
    offset_stop,
    span_hz,
    rbw_ratio,
    volt_sweep_1_1,
    volt_single_1_1,
    volt_start_1_1,
    volt_stop_1_1,
    volt_step_1_1,
    power_dbm,
    current_1_1,
    volt_sweep_1_2,
    volt_single_1_2,
    volt_start_1_2,
    volt_stop_1_2,
    volt_step_1_2,
    current_1_2,
    volt_sweep_1_3,
    volt_single_1_3,
    volt_start_1_3,
    volt_stop_1_3,
    volt_step_1_3,
    current_1_3,
    volt_sweep_2_1,
    volt_single_2_1,
    volt_start_2_1,
    volt_stop_2_1,
    volt_step_2_1,
    current_2_1,
    volt_sweep_2_2,
    volt_single_2_2,
    volt_start_2_2,
    volt_stop_2_2,
    volt_step_2_2,
    current_2_2,
    volt_sweep_2_3,
    volt_single_2_3,
    volt_start_2_3,
    volt_stop_2_3,
    volt_step_2_3,
    current_2_3
    ):
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")

    local_folder = os.path.join(log_path, timestamp)
    os.makedirs(local_folder, exist_ok=True)

    dco_values = []

    binary_reg1 = list("0000000010000111")

    if init_dco_sweep:
        val = dco_start
        while val <= dco_stop:
            dco_values.append(val)
            val += dco_step
    else:
        dco_values.append(init_dco_single)

    kp_values = []
    ki_values = []

    binary_reg0 = list("0111011100011001")

    binary_reg0[15 - 4] = str(en_dsm)
    binary_reg0[15 - 6] = str(dlf_mode)

    if kp_sweep:
        val = kp_start
        while val <= kp_stop:
            kp_values.append(val)
            val += kp_step
    else:
        kp_values.append(kp_single)

    if ki_sweep:
        val = ki_start
        while val <= ki_stop:
            ki_values.append(val)
            val += ki_step
    else:
        ki_values.append(ki_single)

    freq_values = []
    volt_values_1_1 = []
    volt_values_1_2 = []
    volt_values_1_3 = []
    volt_values_2_1 = []
    volt_values_2_2 = []
    volt_values_2_3 = []

    if freq_sweep == True:
        val = freq_start
        while val <= freq_stop:
            freq_values.append(val)
            val += freq_step
            val = round(val, 10)
    else :
        freq_values.append(freq_single)

    if volt_sweep_1_1 == True:
        vv = volt_start_1_1
        while vv <= volt_stop_1_1:
            volt_values_1_1.append(vv)
            vv += volt_step_1_1
            vv = round(vv, 10)
    else :
        volt_values_1_1.append(volt_single_1_1)

    if volt_sweep_1_2 == True:
        vv = volt_start_1_2
        while vv <= volt_stop_1_2:
            volt_values_1_2.append(vv)
            vv += volt_step_1_2
            vv = round(vv, 10)
    else :
        volt_values_1_2.append(volt_single_1_2)

    if volt_sweep_1_3 == True:
        vv = volt_start_1_3
        while vv <= volt_stop_1_3:
            volt_values_1_3.append(vv)
            vv += volt_step_1_3
            vv = round(vv, 10)
    else :
        volt_values_1_3.append(volt_single_1_3)

    if volt_sweep_2_1 == True:
        vv = volt_start_2_1
        while vv <= volt_stop_2_1:
            volt_values_2_1.append(vv)
            vv += volt_step_2_1
            vv = round(vv, 10)
    else :
        volt_values_2_1.append(volt_single_2_1)

    if volt_sweep_2_2 == True:
        vv = volt_start_2_2
        while vv <= volt_stop_2_2:
            volt_values_2_2.append(vv)
            vv += volt_step_2_2
            vv = round(vv, 10)
    else :
        volt_values_2_2.append(volt_single_2_2)

    if volt_sweep_2_3 == True:
        vv = volt_start_2_3
        while vv <= volt_stop_2_3:
            volt_values_2_3.append(vv)
            vv += volt_step_2_3
            vv = round(vv, 10)
    else :
        volt_values_2_3.append(volt_single_2_3)

    total_idx = 1

    for idx, dco in enumerate(dco_values):
        dco_bin = f"{int(dco):010b}"
        binary_reg1[6:] = list(dco_bin)

        hex_val = bin16_to_hex4("".join(binary_reg1))

        try:
            write_register(1, hex_val)
            reg1 = read_register(2, 20)
            reg1 = hex4_to_bin16(f"{reg1[2]:02X}{reg1[3]:02X}")
        except Exception as e:
            print("reg1"+str(e))
            return False, e
        for idx_kp, kp in enumerate(kp_values):
            kp_bin = f"{int(kp):04b}"
            binary_reg0[4:8] = list(kp_bin)
            for idx_ki, ki in enumerate(ki_values):
                ki_bin = f"{int(ki):04b}"
                binary_reg0[0:4] = list(ki_bin)
                hex_val = bin16_to_hex4("".join(binary_reg0))

                try:
                    write_register(0, hex_val)
                    reg0 = read_register(2, 20)
                    reg0 = hex4_to_bin16(f"{reg0[0]:02X}{reg0[1]:02X}")
                except Exception as e:
                    print("reg0"+str(e))
                    return False, e
                for idx_freq, freq in enumerate(freq_values):
                        sgu.set_frequency(freq)
                        sgu.set_power(power_dbm)
                        sgu.rf_on()

                        for idx_vol_1_1, voltage_1_1 in enumerate(volt_values_1_1):
                            ch_settings_1_1 = {
                                1: {
                                    'voltage': voltage_1_1,
                                    'current': current_1_1,
                                    'ovp': voltage_1_1 + 2.0,
                                    'ocp': False,
                                    'output': True
                                }
                            }

                            for idx_vol_1_2, voltage_1_2 in enumerate(volt_values_1_2):
                                ch_settings_1_2 = {
                                    2: {
                                        'voltage': voltage_1_2,
                                        'current': current_1_2,
                                        'ovp': voltage_1_2 + 2.0,
                                        'ocp': False,
                                        'output': True
                                    }
                                }

                                for idx_vol_1_3, voltage_1_3 in enumerate(volt_values_1_3):
                                    ch_settings_1_3 = {
                                        3: {
                                            'voltage': voltage_1_3,
                                            'current': current_1_3,
                                            'ovp': voltage_1_3 + 2.0,
                                            'ocp': False,
                                            'output': True
                                        }
                                    }

                                    for idx_vol_2_1, voltage_2_1 in enumerate(volt_values_2_1):
                                        ch_settings_2_1 = {
                                            1: {
                                                'voltage': voltage_2_1,
                                                'current': current_2_1,
                                                'ovp': voltage_2_1 + 2.0,
                                                'ocp': False,
                                                'output': True
                                            }
                                        }

                                        for idx_vol_2_2, voltage_2_2 in enumerate(volt_values_2_2):
                                            ch_settings_2_2 = {
                                                2: {
                                                    'voltage': voltage_2_2,
                                                    'current': current_2_2,
                                                    'ovp': voltage_2_2 + 2.0,
                                                    'ocp': False,
                                                    'output': True
                                                }
                                            }

                                            for idx_vol_2_3, voltage_2_3 in enumerate(volt_values_2_3):
                                                ch_settings_2_3 = {
                                                    3: {
                                                        'voltage': voltage_2_3,
                                                        'current': current_2_3,
                                                        'ovp': voltage_2_3 + 2.0,
                                                        'ocp': False,
                                                        'output': True
                                                    }
                                                }

                                                psu1.setting(ch_settings_1_1, [1])
                                                psu1.setting(ch_settings_1_2, [2])
                                                psu1.setting(ch_settings_1_3, [3])
                                                psu2.setting(ch_settings_2_1, [1])
                                                psu2.setting(ch_settings_2_2, [2])
                                                psu2.setting(ch_settings_2_3, [3])

                                                (a_temp, a_humid) = getTempHumid()

                                                save_settings_csv(local_folder, int("".join(reg0[4:8]), 2), int("".join(reg0[0:4]), 2), int("".join(reg1), 2), freq, power_dbm, voltage_1_1, voltage_1_2, voltage_1_3, voltage_2_1, voltage_2_3, voltage_2_3,  total_idx, a_temp, a_humid)
                                                sau.set_spectrum()
                                                sau.set_rbw_spectrum(3e3)
                                                sau.set_vbw_spectrum(30e3)
                                                time.sleep(1)
                                                sau.remove_spectrum_table()
                                                sau.auto_set_all()
                                                time.sleep(15)

                                                sau.set_span(span_hz)
                                                time.sleep(5)
                                                sau.set_spectrum_table()
                                                time.sleep(1)
                                                sau.marker_peak_search()
                                                time.sleep(2)

                                                peak_freq = sau.get_marker()
                                                time.sleep(2)
                                                peak_amp = sau.get_marker_value()
                                                time.sleep(2)
                                                peak_amp = float(peak_amp)
                                                time.sleep(2)

                                                sau.capture_spectrum(capture_path, f'{total_idx}.')

                                                psu1_pwr_1 = psu1.status_voltage(1)
                                                psu1_pwr_2 = psu1.status_voltage(2)
                                                psu1_pwr_3 = psu1.status_voltage(3)
                                                psu2_pwr_1 = psu2.status_voltage(1)
                                                psu2_pwr_2 = psu2.status_voltage(2)
                                                psu2_pwr_3 = psu2.status_voltage(3)

                                                append_marker_data(local_folder, peak_freq, peak_amp, freq, psu1_pwr_1, psu1_pwr_2, psu1_pwr_3, psu2_pwr_1, psu2_pwr_2, psu2_pwr_3, total_idx)
                                                sau.remove_spectrum_table()
                                                time.sleep(1)

                                                sau.set_phase_noise()
                                                sau.set_verify_off()
                                                time.sleep(1)

                                                sau.remove_noise_table()
                                                time.sleep(1)
                                                sau.set_noise_table()
                                                time.sleep(1)
                                                jitter = sau.set_jitter(offset_start, offset_stop, rbw_ratio)
                                                sno = sau.get_spot_noise()
                                                time.sleep(2)
                                                append_phase_data(local_folder, jitter, sno[0]["Phase_noise_dBc/Hz"], sno[1]["Phase_noise_dBc/Hz"], sno[2]["Phase_noise_dBc/Hz"], sno[3]["Phase_noise_dBc/Hz"], sno[4]["Phase_noise_dBc/Hz"])

                                                sau.capture_phase_noise(capture_path, f'{total_idx}.')

                                                psu1.buff_clear()
                                                psu2.buff_clear()

                                                sau.remove_noise_table()
                                                time.sleep(2)
                                                total_idx += 1
    print("측정이 종료됨.")
