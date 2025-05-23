import pyvisa
import time
from datetime import datetime

class FSV3000:
    def __init__(self, ip='192.168.0.6'):
        self.__ip = ip
        self.__inst = None
        self.__center_freq_hz = None
        self.__span_hz = None
        self.__ref_level_dbm = None
        self.__rbw_spectrum = None
        self.__vbw_spectrum = None
        self.__rbw_ratio = None
        self.__freq_hz = None
        self.__usb_path = None
        self.__offset_start = None
        self.__offset_stop = None

        self.sau_usb_dir = "D:/"

    def set_ip(self, ip: str):
        self.__ip = ip

    def get_ip(self):
        return self.__ip

    def connect_device(self):
        try:
            resource = f"TCPIP0::{self.__ip}::5025::SOCKET"
            rm = pyvisa.ResourceManager()
            self.__inst = rm.open_resource(resource)
            self.__inst.write_termination = '\n'
            self.__inst.read_termination = '\n'

            idn = self.__inst.query("*IDN?").strip()
            print(f"[FSV3000 연결 성공] {idn}")
            return True

        except Exception as e:
            print(f"[FSV3000 연결 실패] {e}")
            return False, e

    def set_frequency(self, center_freq_hz):
        self.__center_freq_hz = center_freq_hz
        try:
            self.__inst.write(f"FREQ:CENT {self.__center_freq_hz}")
            print(f"[주파수 설정] {self.__center_freq_hz:.3e} Hz")
            return True

        except Exception as e:
            print(f"[오류 - 주파수 설정] {e}")
            return False, e

    def set_span(self, span_hz):
        self.__span_hz = span_hz
        try:
            self.__inst.write(f"FREQ:SPAN {self.__span_hz}")
            print(f"[Sapn 설정] {self.__span_hz:.3e} Hz")
            return True

        except Exception as e:
            print(f"[오류 - Span 설정] {e}")
            return False, e

    def set_amplitude(self, ref_level_dbm):
        self.__ref_level_dbm = ref_level_dbm
        try:
            self.__inst.write(f"DISP:WIND:TRAC:Y:RLEV {self.__ref_level_dbm}")
            print(f"[Level 설정] {self.__ref_level_dbm:.2f} dBm")
            return True

        except Exception as e:
            print(f"[오류 - Level 설정] {e}")

    def set_rbw_spectrum(self, rbw):
        self.__rbw_spectrum = rbw

        self.__inst.write(f"SENS:BAND:RES {self.__rbw_spectrum}")
        print(f"[Spectrum RBW 설정] {self.__rbw_spectrum} Hz")

    def set_vbw_spectrum(self, vbw):
        self.__vbw_spectrum = vbw

        self.__inst.write(f"SENS:BAND:VID {self.__vbw_spectrum}")
        print(f"[Spectrum VBW 설정] {self.__vbw_spectrum} Hz")

    def set_resolution_bw(self, rbw_ratio):
        self.__rbw_ratio = rbw_ratio
        try:
            self.__inst.write(f"SENS:LIST:BWID:RAT {self.__rbw_ratio}")
            print(f"[RBW 설정] {self.__rbw_ratio} %")
            return True

        except Exception as e:
            print(f"[오류 - RBW 설정] {e}")
            return False, e

    def set_verify_off(self):
        self.__inst.write("SENS:FREQ:VER:STAT OFF")
        self.__inst.write("SENS:POW:RLEV:VER:STAT OFF")

    def single_sweep(self):
        try:
            self.__inst.write("INIT:CONT OFF")
            self.__inst.write("INIT:IMM")
            print("[Single Sweep] 실행")
            time.sleep(1)
            return True

        except Exception as e:
            print(f"[오류 - Single Sweep] {e}")
            return False, e

    def continuous_sweep(self):
        try:
            self.__inst.write("INIT:CONT ON")
            print("[Continuous Sweep] 실행")
            time.sleep(1)
            return True

        except Exception as e:
            print(f"[오류 - Continuous Sweep] {e}")
            return False, e

    def get_trace(self):
        try:
            self.__inst.write("FORM ASC")
            data = self.__inst.query("TRAC? TRACE1")
            trace_data = list(map(float, data.strip().split(',')))
            print(f"[Trace 획득] {(trace_data)} 포인트")
            return trace_data

        except Exception as e:
            print(f"[오류 - Trace] {e}")
            return False, e

    def auto_set_all(self):
        try:
            self.__inst.write("INIT:CONT OFF")
            self.__inst.write("SENS:ADJ:ALL")
            print("[Auto Set] 전체 자동 설정 실행됨")
            return True

        except Exception as e:
            print(f"[오류 - Auto Set - All] {e}")
            return False, e

    def auto_set_freq(self):
        try:
            self.__inst.write("SENS:ADJ:FREQ;*WAI")
            self.__inst.write("SENS:SWEep:OPTimize AUTO")
            print(f"[Auto Set] Freq 자동 설정 실행됨")
            return True

        except Exception as e:
            print(f"[오류 - Auto Set - FREQ] {e}")
            return False, e

    def auto_set_level(self):
        try:
            self.__inst.write("SENS:ADJ:LEV;*WAI")
            print(f"[Auto Set] Level 자동 설정 실행됨")
            return True

        except Exception as e:
            print(f"[오류 - Auto Set - Level] {e}")
            return False, e

    def set_offset_start(self, offset_start):
        self.__offset_start = offset_start

        try:
            self.__inst.write(f"SENS:FREQ:STAR {self.__offset_start}")
            print(f"[오프셋 시작 설정 완료]: {self.__offset_start}")
            return True
        except Exception as e:
            print(f"[오류 - 오프셋 시작 설정] {e}")

    def set_offset_stop(self, offset_stop):
        self.__offset_stop = offset_stop

        try:
            self.__inst.write(f"SENS:FREQ:STOP {self.__offset_stop}")
            print(f"[오프셋 종료 설정 완료]: {self.__offset_stop}")
            return True
        except Exception as e:
            print(f"[오류 - 오프셋 종료 설정] {e}")

    def set_spectrum_table(self):
        try:
            self.__inst.write("INIT:IMM")
            temp = self.__inst.query("LAY:ADD:WIND? '1',BEL,MTAB")
            print(f"[Spectrum Marker table 설정 완료]")
            return True

        except Exception as e:
            print(f"[오류 - Spectrum Marker table 설정] {e}")
            return False, e

    def remove_spectrum_table(self):
        try:
            self.__inst.write("INIT:IMM")
            self.__inst.write("LAY:REM:WIND '2'")
            self.__inst.write("LAY:REM:WIND '3'")
            self.__inst.write("LAY:REM:WIND '4'")
            self.__inst.write("LAY:REM:WIND '5'")
            print(f"[Spectrum Marker table 삭제 완료]")
            return True

        except Exception as e:
            print(f"[오류 - Spectrum Marker table 삭제] {e}")
            return False, e

    def set_noise_table(self):
        try:
            self.__inst.write("INIT:IMM")
            temp = self.__inst.query("LAY:ADD:WIND? '1',BEL,RNO")
            temp = self.__inst.query("LAY:ADD:WIND? '2',BEL,SNO")
            print(f"[Phase noise table 설정 완료]")
            return True

        except Exception as e:
            print(f"[오류 - Phase noise table 설정] {e}")
            return False, e

    def remove_noise_table(self):
        try:
            self.__inst.write("INIT:IMM")
            self.__inst.write("LAY:REM:WIND '2'")
            self.__inst.write("LAY:REM:WIND '3'")
            self.__inst.write("LAY:REM:WIND '4'")
            self.__inst.write("LAY:REM:WIND '5'")
            print(f"[Phase noise table 삭제 완료]")
            return True

        except Exception as e:
            print(f"[오류 - Phase noise table 삭제] {e}")
            return False, e

    def set_spectrum(self):
        try:
            self.__inst.write("INST:SEL 'Spectrum'")
            time.sleep(5.0)
            print(f"[Spectrum 전환] 완료")
            return True

        except Exception as e:
            print(f"[오류 - Spectrum 전환] {e}")
            return False, e

    def set_phase_noise(self):
        try:
            self.__inst.write("INST:SEL 'PNOISE'")
            time.sleep(15.0)
            self.__inst.write("SENS:FREQ:VER:STAT OFF")
            self.__inst.write("SENS:POW:RLEV:VER:STAT OFF")
            print(f"[Phase noise 전환] 완료")
            return True

        except Exception as e:
            print(f"[오류 - Phase noise 전환] {e}")
            return False, e

    def set_jitter(self, offset_start, offset_stop, rbw_ratio):
        self.__offset_start = offset_start
        self.__offset_stop = offset_stop
        self.__rbw_ratio = rbw_ratio

        self.__inst.write(f"SENS:FREQ:STAR {self.__offset_start}")
        self.__inst.write(f"SENS:FREQ:STOP {self.__offset_stop}")
        self.__inst.write(f"SENS:LIST:BWID:RAT {self.__rbw_ratio}")
        time.sleep(5)
        print(f"[오프셋 시작 설정 완료]: {self.__offset_start}")
        print(f"[오프셋 종료 설정 완료]: {self.__offset_stop}")
        print(f"[RBW 설정] {self.__rbw_ratio} %")

        self.__inst.write("SENS:ADJ:ALL")
        print("[Auto Set] 전체 자동 설정 실행됨")
        time.sleep(15.0)

        self.__inst.write("INIT:CONT OFF")
        self.__inst.write("INIT:IMM")
        print("[Single Sweep] 실행")
        time.sleep(5.0)

        jitter_sec = self.__inst.query("FETC:PNO:RMS?")
        jitter_ps = float(jitter_sec) * 1e12
        print(f"Residual RMS Jitter: {jitter_ps:.2f} ps")
        return jitter_ps

    def capture_spectrum(self, path, postfix=None):
        nowtime = datetime.now().strftime("%Y%m%d_%H%M%S")
        self.__usb_path = path
        try:
            self.__inst.write("INST:SEL 'Spectrum'")
            time.sleep(5.0)
            self.__inst.write("HCOP:DEST 'MMEM'")
            self.__inst.write("HCOP:DEV:LANG JPG")
            self.__inst.write(f"MMEM:NAME '{self.__usb_path}/{f"{postfix}" if postfix else ''}spectrum_{nowtime}'")
            self.__inst.write("HCOP:IMM")
            print(f"[Spectrum Capture] 파일 저장: {self.__usb_path}")
            return True

        except Exception as e:
            print(f"[오류 - Spectrum Captrue] {e}")
            return False, e

    def capture_phase_noise(self, path, postfix=None):
        nowtime = datetime.now().strftime("%Y%m%d_%H%M%S")
        self.__usb_path = path
        try:
            self.__inst.write("INST:SEL 'PNOISE'")
            time.sleep(15.0)  # Ensure time for phase noise initialization
            self.__inst.write("HCOP:DEST 'MMEM'")
            self.__inst.write("HCOP:DEV:LANG JPG")
            self.__inst.write(f"MMEM:NAME '{self.__usb_path}/{f"{postfix}" if postfix else ''}phase_noise_{nowtime}'")
            self.__inst.write("HCOP:IMM")
            print(f"[Phase Noise Capture] 파일 저장: {self.__usb_path}")
            return True

        except Exception as e:
            print(f"[오류 - 위상잡음 캡처] {e}")
            return False, e

    def query_status(self):
        try:
            freq = float(self.__inst.query("FREQ:CENT?").strip())
            span = float(self.__inst.query("FREQ:SPAN?").strip())
            level = float(self.__inst.query("DISP:WIND:TRAC:Y:RLEV?").strip())
            rbw = float(self.__inst.query("BAND:RES?").strip())

            status_dict = {"Center_freq": freq, "Span": span, "Ref_level": level, "RBW": rbw}

            print("[상태 확인]")
            print(f" - Center Freq. : {status_dict[freq]:.3e} Hz")
            print(f" - Span         : {status_dict[span]:.3e} Hz")
            print(f" - Ref. Level   : {status_dict[level]:.2f} dBm")
            print(f" - RBW          : {status_dict[rbw]:.2e} Hz")
            return status_dict

        except Exception as e:
            print(f"[오류 - 상태 확인] {e}")

    def set_marker(self, freq_hz):
        self.__freq_hz = freq_hz
        try:
            self.__inst.write(f"CALC:MARK1:X {self.__freq_hz}")
            print(f"[Marker 설정] {self.__freq_hz:.3e} Hz")
            return True

        except Exception as e:
            print(f"[오류 - Marker 설정] {e}")
            return False, e

    def marker_peak_search(self):
        try:
            self.__inst.write("CALC:MARK:MAX")
            print("[피크 탐색]")
            return True

        except Exception as e:
            print(f"[오류 - 피크 탐색] {e}")
            return  False, e

    def get_marker(self):
        try:
            result = self.__inst.query("CALC:MARK1:X?").strip()
            print(f"[Marker 위치] {float(result):.3e} Hz")
            return float(result)

        except Exception as e:
            print(f"[오류 - Marker 쿼리] {e}")
            return False, e

    def get_marker_value(self):
        try:
            #value = self.__inst.query("CALC:MARK:Y?")
            value = self.__inst.query("CALC:MARK1:Y?").strip()
            print(f"[마커 읽기]: {value} dBm")
            return value

        except Exception as e:
            print(f"[오류 - 마커 읽기] {e}")
            return e

    def get_all_markers(self):
        try:
            markers_data = []
            self.__inst.query("CALC:MARK:COUN? ")
            count = int(self.__inst.read())

            for i in range(1, count + 1):
                self.__inst.write(f"CALC:MARK{i}:STAT ON")  # Ensure marker is active
                x_val = float(self.__inst.query(f"CALC:MARK{i}:X?").strip())
                y_val = float(self.__inst.query(f"CALC:MARK{i}:Y?").strip())
                markers_data.append({"Marker": f"M{i}", "X_Value_Hz": x_val, "Y_Value_dB": y_val})

            print("[마커 테이블 읽기 완료]")
            for m in markers_data:
                print(f"{m['Marker']}: {m['X_Value_Hz']:.6e} Hz, {m['Y_Value_dB']:.2f} dB")

            return markers_data

        except Exception as e:
            print(f"[오류 - 모든 마커 정보 읽기] {e}")
            return False, e

    def get_spot_noise(self):
        sno_data = []

        for i in range(1, 6):
            x_raw = self.__inst.query(f"CALC:SNO{i}:X?").strip()
            try:
                offset_freq = float(x_raw) if x_raw else 1.0
            except ValueError:
                offset_freq = 1.0

            if i == 1:
                phase_noise = None
            else:
                phase_noise = self.__inst.query(f"CALC:SNO{i}:Y?").strip()
                try:
                    phase_noise = float(phase_noise) if phase_noise else 1.0
                except ValueError:
                    phase_noise = 1.0

            sno_data.append({"SNO": f"M{i}", "Offset_freq_Hz": offset_freq, "Phase_noise_dBc/Hz": phase_noise})
        return sno_data

    def buff_clear(self):
        self.__inst.write("*CLS")

    def close(self):
        if self.__inst:
            self.__inst.close()
            print("[연결 종료]")

if __name__ == "__main__":
    sau = FSV3000(ip='192.168.0.6')
    sau.connect_device()
    sau.close()