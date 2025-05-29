import pyvisa
import time

class E36313A:
    def __init__(self, ip='192.168.0.5'):
        """
        - Initialize the class
        """
        self.__ip = ip
        self.__inst = None
        self.__settings_dict: dict[int, dict] = {}
        self.__channels = [1, 2, 3]

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
            print(f"[E36313A 연결 성공] {idn}")
            return True

        except Exception as e:
            print(f"[E36313A 연결 실패] {e}")
            return False

    def scpi_write(self, cmd):
        """
        - Send an SCPI command
        """
        try:
            self.__inst.write(cmd)
            print(f"[WRITE] {cmd}")
            time.sleep(0.2)
        except Exception as e:
            print(f"[명령 실패]: {cmd}, [오류]: {e}")

    def scpi_query(self, cmd):
        """
        - Send an SCPI query, read response
        """
        try:
            resp = self.__inst.query(cmd).strip()
            print(f"[QUERY] {cmd} → {resp}")
            time.sleep(0.2)
            return resp
        except Exception as e:
            print(f"[명령 실패]: {cmd}, [오류]: {e}")
            return None

    def pwr_on(self, ch):
        """
        - Turn on the output of a specific channel
        """
        try:
            self.scpi_write(f"INST:NSEL {ch}")
            self.scpi_write(f"OUTP ON")
            print(f"[출력 ON] - CH{ch}의 출력 ON")
            return True
        except Exception as e:
            print(f"[오류- 설정 실패] CH{ch}의 출력 ON 실패")
            return False, e

    def pwr_off(self, ch):
        """
        - Turn off the output of a specific channel
        """
        try:
            self.scpi_write(f"INST:NSEL {ch}")
            self.scpi_write(f"OUTP OFF")
            print(f"[출력 OFF] - CH{ch}의 출력 OFF")
            return True
        except Exception as e:
            print(f"[오류- 설정 실패] CH{ch}의 출력 OFF 실패")
            return False, e

    def setting(self, settings_dict: dict[int, dict], ch_list):
        """
        - Apply settings (voltage, current, protection) to multiple channels
        """
        self.__settings_dict = settings_dict

        for ch in ch_list:
            setting = self.__settings_dict.get(ch)

            try:
                voltage = setting.get("voltage", 0.0)
                current = setting.get("current", 0.0)
                ovp = setting.get("ovp", 0.0)
                ocp_state = setting.get("ocp", False)
                output_state = setting.get("output", False)

                self.scpi_write(f"INST:NSEL {ch}")
                self.scpi_write(f"VOLT {voltage}")
                self.scpi_write(f"CURR {current}")
                self.scpi_write(f"VOLT:PROT {ovp}")
                self.scpi_write("VOLT:PROT:STAT ON")
                self.scpi_write(f"CURR:PROT:STAT {'ON' if ocp_state else 'OFF'}")
                self.scpi_write(f"OUTP {'ON' if output_state else 'OFF'}")

                print(
                    f"[CH{ch}] [설정값] → V:{voltage}, I:{current}, OVP:{ovp}, OCP:{'ON' if ocp_state else 'OFF'}, OUT:{'ON' if output_state else 'OFF'}")
                return True

            except Exception as e:
                print(f"[CH{ch}] [오류 - 설정 실패]: {e}")
                return False, e

    def status_voltage(self, ch):
        """
        - Return the current voltage of a specific channel
        """
        try:
            self.scpi_write(f"INST:NSEL {ch}")
            voltage = self.scpi_query("MEAS:VOLT?")

            volt = float(voltage)

            return volt

        except Exception as e:
            print(f"[CH{ch}] [오류 - 현재 전압 상태]: {e}")
            return False, e

    def status_ch(self, ch):
        """
        - Return the current voltage, current, and output state of a specific channel
        """
        try:
            self.scpi_write(f"INST:NSEL {ch}")
            voltage = self.scpi_query("MEAS:VOLT?")
            current = self.scpi_query("MEAS:CURR?")
            output = self.scpi_query("OUTP?")
            status = {
                "voltage": float(voltage),
                "current": float(current),
                "output": (output == '1')
            }
            print(
                f"[CH{ch}] [현재 상태] → V:{status['voltage']}V, I:{status['current']}A, 출력:{'ON' if status['output'] else 'OFF'}")
            return True, status

        except Exception as e:
            print(f"[CH{ch}] [오류 - 현재 상태]: {e}")
            return False, e

    def status_all(self):
        """
        - Return the current voltage, current, and output state of all channels
        """
        statuses = {}
        for ch in self.__channels:
            statuses[ch] = self.status_ch(ch)
        return statuses

    def full_status_all(self):
        """
        - Return full status including protection for all channels
        """
        statuses = {}
        for ch in self.__channels:
            try:
                self.scpi_write(f"INST:NSEL {ch}")
                voltage = float(self.scpi_query("MEAS:VOLT?"))
                current = float(self.scpi_query("MEAS:CURR?"))
                output = (self.scpi_query("OUTP?") == '1')
                ovp = float(self.scpi_query("VOLT:PROT?"))
                ovp_on = self.scpi_query("VOLT:PROT:STAT?") == '1'
                ocp_on = self.scpi_query("CURR:PROT:STAT?") == '1'

                statuses[ch] = {
                    "voltage": voltage,
                    "current": current,
                    "output": output,
                    "ovp": ovp,
                    "ovp_on": ovp_on,
                    "ocp_on": ocp_on
                }

            except Exception as e:
                print(f"[CH{ch}] 상태 읽기 실패: {e}")
                statuses[ch] = None
                return False, e

        return statuses

    def set_channel_voltage(self, channel, voltage):
        """
        - Set voltage for a specific channel
        """
        try:
            self.scpi_write(f'APPL CH{channel},{voltage},1')
            print(f'[설정] 채널 {channel} 전압을 {voltage}V로 설정')
            return True

        except Exception as e:
            print(f'[오류] 채널 {channel} 전압 설정 실패: {e}')
            return False

    def read_channel_voltage(self, channel):
        """
        - Return voltage from a specific channel
        """
        try:
            voltage = float(self.scpi_query(f'MEAS:VOLT? CH{channel}'))
            print(f'[성공] 채널 {channel} 전압은 {voltage}V')
            return voltage

        except Exception as e:
            print(f'[오류] 전압 읽기 실패 (CH{channel}): {e}')
            return None

    def apply_channel_setting(self, setting: dict, ch: int):
        """
        - Apply a full setting dictionary to a single channel
        """
        self.scpi_write(f"INST:NSEL {ch}")
        self.scpi_write(f"VOLT {setting['voltage']}")
        self.scpi_write(f"CURR {setting['current']}")
        self.scpi_write(f"VOLT:PROT {setting['ovp']}")
        self.scpi_write("VOLT:PROT:STAT ON")
        self.scpi_write(f"CURR:PROT:STAT {'ON' if setting.get('ocp') else 'OFF'}")
        if setting.get('output'):
            self.scpi_write("OUTP ON")
            return True

        else:
            self.scpi_write("OUTP OFF")
            return False

    def buff_clear(self):
        """
        - Clear instrument status and error buffer
        """
        self.__inst.write("*CLS")

    def close(self):

        if self.__inst:
            self.__inst.close()
            print("[연결 종료]")

if __name__ == "__main__":
    psu = E36313A(ip='192.168.0.3')