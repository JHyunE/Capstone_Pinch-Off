import pyvisa
import time
import math

class SMB100B:
    """
    - Initialize the class
    """
    def __init__(self, ip='169.254.144.100'):
        self.__ip = ip
        self.__inst = None
        self.__freq_hz = None
        self.__dbm = None

    def set_ip(self, ip: str):
        """
        - Set the IP address
        """
        self.__ip = ip

    def get_ip(self):
        """
        - Return the current IP address
        """
        return self.__ip

    def connect_device(self):
        """
        - Connect to the device
        """
        try:
            resource = f"TCPIP0::{self.__ip}::5025::SOCKET"
            rm = pyvisa.ResourceManager()
            self.__inst = rm.open_resource(resource)
            self.__inst.write_termination = '\n'
            self.__inst.read_termination = '\n'

            idn = self.__inst.query("*IDN?").strip()
            print(f"[SMB100B 연결 성공] {idn}")
            return True

        except Exception as e:
            print(f"[SMB100B 연결 실패] {e}")
            return False

    def set_frequency(self, freq_hz):
        """
        - Set the output frequency(Unit: Hz)
        """
        self.__freq_hz = freq_hz

        try:
            self.__inst.write(f"SOUR:FREQ {self.__freq_hz}")
            print(f"[주파수 설정] {self.__freq_hz} Hz")
            time.sleep(0.1)
            return True

        except Exception as e:
            print(f"[오류 - 주파수 설정] {e}")
            return False, e

    def set_power(self, dbm):
        """
        - Set the output power level(unit: dBm)
        """
        self.__dbm = dbm

        try:
            self.__inst.write(f"SOUR:POW {self.__dbm}")
            print(f"[출력 설정] {self.__dbm} dBm")
            time.sleep(0.1)
            return True

        except Exception as e:
            print(f"[오류 - 출력 설정] {e}")
            return False, e

    def rf_on(self):
        """
        - Enable RF output
        """
        try:
            self.__inst.write("OUTP ON")
            print("[RF 출력] ON")
            return True
        except Exception as e:
            print(f"[오류 - RF 출력 ON] {e}")
            return False, e

    def rf_off(self):
        """
        - Disable RF output
        """
        try:
            self.__inst.write("OUTP OFF")
            print("[RF 출력] OFF")
            return True
        except Exception as e:
            print(f"[오류 - RF 출력 OFF] {e}")
            return False, e

    def query_status(self):
        """
        - Return the current status(frequency, power, RMS voltage, RF state)
        """
        if not self.connect_device():
            return
        try:
            freq = float(self.__inst.query("SOUR:FREQ?").strip())
            power_dbm = float(self.__inst.query("SOUR:POW?").strip())
            rf = self.__inst.query("OUTP?").strip()

            # dBm → mV RMS 변환 (50Ω 기준)
            v_rms = 10 ** (power_dbm / 20) * math.sqrt(50)
            v_mvrms = v_rms * 1000  # mV

            settings_dict = {"freq": freq, "dBm": power_dbm, "RMS": v_mvrms, "RF_ON": rf == '1'}

            print("[상태 확인]")
            print(f' - 주파수     : {settings_dict["freq"]:.3e} Hz')
            print(f' - 출력 전력  : {settings_dict["power_dbm"]:.2f} dBm')
            print(f' - 전압 (RMS) : {settings_dict["RMS"]:.2f} mV')
            print(f' - RF 출력    : {settings_dict["RF_ON"]}')

            return settings_dict

        except Exception as e:
            print(f"[오류 - 상태 쿼리] {e}")
            return  False, e

    def get_frequency(self):
        """
        - Return the currently set output frequency(unit: Hz)
        """
        return float(self.__inst.query("SOUR:FREQ?"))

    def get_power(self):
        """
        - Return the currently set output power(unit: dBm)
        """
        return float(self.__inst.query("SOUR:POW?"))

    def get_output_status(self):
        """
        - Return True if RF output is ON, False otherwise
        """
        return self.__inst.query("OUTP?").strip() == "1"

    def close(self):
        """
        - Close the connection to the device
        """
        if self.__inst:
            self.__inst.close()
            print("[연결 종료]")