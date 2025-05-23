from tkinter.ttk import Label, Frame
import re

def set_label_text(label: Label, text: str):
    label["text"] = text

def check_ip(ip: str) -> bool:
    rule = re.compile(r'^(([0-9]|[1-9][0-9]|1[0-9]{2}|2[0-4][0-9]|25[0-5])\.){3}([0-9]|[1-9][0-9]|1[0-9]{2}|2[0-4][0-9]|25[0-5])$')
    return rule.match(ip) is not None

def toggle_frame(frame: Frame, show: bool):
    if show:
        frame.grid()
    else:
        frame.grid_remove()

def change_freq_unit(freq: float, unit: str) -> float:
    if unit == "Hz":
        return freq
    elif unit == "kHz":
        return freq * 1e3
    elif unit == "MHz":
        return freq * 1e6
    elif unit == "GHz":
        return freq * 1e9
    else:
        raise ValueError(f"오류")

def bin16_to_hex4(bin_str):
    return f"{int(bin_str, 2):04X}"

def hex4_to_bin16(hex_str):
    return f"{format(int(hex_str, 16), '016b')}"

def dec_to_bin4(n):
    return format(n, '04b')

def dec_to_bin_n(n, width):
    return format(n, f'0{width}b')