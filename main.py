import tkinter as tk
from tkinter.ttk import Notebook, Label, Button, Frame, Entry, LabelFrame, Checkbutton, Progressbar, Combobox, Treeview
from tkinter import StringVar, DoubleVar, BooleanVar, IntVar, Radiobutton

from util import set_label_text, check_ip, toggle_frame, change_freq_unit, bin16_to_hex4

from E36313A import E36313A
from SMB100B import SMB100B
from FSV3000 import FSV3000
from measurement import measurement

from SPI import write_register, read_register

class Application:
    def __init__(self):
        self.__device_ip = {
            "E36313A - 1":  StringVar(value = "192.168.0.3"),
            "E36313A - 2":  StringVar(value = "192.168.0.4"),
            "SMB100B":      StringVar(value = "192.168.0.5"),
            "FSV3000":      StringVar(value = "192.168.0.6"),
        }

        self.reg_settings = {
            0: ("0111011100011001", {
                4: IntVar(value=1), 6: IntVar(value=0)}),
            1: ("0000000010000111", {}),
            15: ("0000000000000100", {
                0: IntVar(value=0), 1: IntVar(value=0),
                10: IntVar(value=0), 11: IntVar(value=0),
                12: IntVar(value=0), 13: IntVar(value=0),
            })
        }

        self.__var_kp = {
            "value": IntVar(value=7),
            "sweep": BooleanVar(value=False),
            "start": IntVar(value=7),
            "stop":  IntVar(value=7),
            "step":  IntVar(value=1),
        }

        self.__var_ki = {
            "value": IntVar(value=7),
            "sweep": BooleanVar(value=False),
            "start": IntVar(value=7),
            "stop":  IntVar(value=7),
            "step":  IntVar(value=1),
        }

        self.__var_init_dco = {
            "value": IntVar(value=135),
            "sweep": BooleanVar(value=False),
            "start": IntVar(value=135),
            "stop":  IntVar(value=135),
            "step":  IntVar(value=1),
        }

        self.__var_spi = [self.__var_kp, self.__var_ki, self.__var_init_dco]

        self.adv_addr = StringVar()
        self.adv_val = StringVar()

        self.__var_psu = {}

        self.__var_unit: StringVar = StringVar(value="MHz")
        self.__var_unit_center: StringVar = StringVar(value="GHz")
        self.__var_unit_span: StringVar = StringVar(value="MHz")
        self.__var_unit_offset_start: StringVar = StringVar(value="kHz")
        self.__var_unit_offset_stop: StringVar = StringVar(value="MHz")

        self.__var_freq: DoubleVar = DoubleVar(value=205.0)
        self.__var_freq_sweep: BooleanVar = BooleanVar(value=False)
        self.__var_freq_start = DoubleVar(value=1000.0)
        self.__var_freq_stop = DoubleVar(value=1000.0)
        self.__var_freq_step = DoubleVar(value=100.0)

        self.__var_pwr = DoubleVar(value=-10.0)
        self.__var_pwr_sweep: BooleanVar = BooleanVar(value=False)
        self.__var_pwr_start = DoubleVar(value=-10.0)
        self.__var_pwr_stop = DoubleVar(value=-10.0)
        self.__var_pwr_step = DoubleVar(value=1.0)

        self.__var_dir: StringVar = StringVar(value="D:\\")
        self.__var_center_freq_hz : DoubleVar = DoubleVar(value=1.0)
        self.__var_span_hz : DoubleVar = DoubleVar(value=100.0)
        self.__var_rbw_ratio : DoubleVar = DoubleVar(value=1.0)
        self.__var_offset_start : DoubleVar = DoubleVar(value=10.0)
        self.__var_offset_stop : DoubleVar = DoubleVar(value=100.0)

        self.__var_log_dir: StringVar = StringVar(value="./result")

        self.connection_state: list[bool] = []

        self.__psu1 = E36313A()
        self.__psu2 = E36313A()
        self.__sgu = SMB100B()
        self.__sau = FSV3000()

    def tab_connection(self, notebook: Notebook) -> None:
        tab = Frame(notebook)
        notebook.add(tab, text="장비 연결")

        labels_device: list[Label] = []
        entries_ip: list[Entry] = []

        def on_ip_change(var, title, *args):
            if check_ip(var.get()):
                title.configure(foreground="")
            else:
                title.configure(foreground="red")

        for row, (device, ip) in enumerate(self.__device_ip.items()):
            entry = Entry(tab, textvariable=ip)
            label = Label(tab, text=device)
            labels_device.append(label)
            entries_ip.append(entry)

            ip.trace("w", lambda *args, var=ip, title=label: on_ip_change(var, title, *args))

        for idx, label, entry in zip(range(len(self.__device_ip.items())), labels_device, entries_ip):
            label.grid(row=idx, column=0, sticky=tk.E, padx=10, pady=3)
            entry.grid(row=idx, column=1, sticky=tk.W)

        label_info: Label = Label(tab, foreground="blue")

        btn_connect: Button = Button(tab, text="장비 연결", command=lambda: self.connect_all(label_info))
        btn_connect.grid(row=len(labels_device), column=0, columnspan=2, pady=8)

        set_label_text(label_info, "장비 연결을 기다리는 중...")
        label_info.grid(row=len(labels_device) + 1, column=0, columnspan=2)

    def connect_all(self, label_info: Label):
        self.__psu1.set_ip(self.__device_ip["E36313A - 1"].get())
        self.__psu2.set_ip(self.__device_ip["E36313A - 2"].get())
        self.__sgu.set_ip(self.__device_ip["SMB100B"].get())
        self.__sau.set_ip(self.__device_ip["FSV3000"].get())

        self.connection_state = []
        self.connection_state.append(self.__psu1.connect_device())
        self.connection_state.append(self.__psu2.connect_device())
        self.connection_state.append(self.__sgu.connect_device())
        self.connection_state.append(self.__sau.connect_device())

        log_connect_state: list[str] = []
        for idx, state in enumerate(self.connection_state):
            if state:
                log_connect_state.append(f"{list(self.__device_ip.keys())[idx]} 연결 성공")
            else:
                log_connect_state.append(f"{list(self.__device_ip.keys())[idx]} 연결 실패")

        set_label_text(label_info, "\n".join(log_connect_state))

    def tab_spi(self, notebook: Notebook) -> None:
        tab = Frame(notebook)
        notebook.add(tab, text="SPI")

        left_frame = Frame(tab)
        left_frame.pack(side="left", padx=10, pady=10, anchor="n")

        mode_options = [
            ("Enable DSM", 0, [("Enable", 4, 1), ("Disable", 4, 0)]),
            ("DLF Mode", 0, [("DLF update", 6, 0), ("Free running", 6, 1)]),
            ("PLL Mode", 15, [("Conventional PLL", 0, 0), ("OSPLL", 0, 1)]),
            ("BBPD", 15, [("BBPD ON", 1, 0), ("BBPD OFF", 1, 1)]),
            ("Clock Source", 15, [("Use divider clk", 13, 0), ("Use mmpg clk", 13, 1)]),
            ("Divider Ratio", 15, [("Div 8", 12, 0), ("Div 16", 12, 1)]),
            ("Retime", 15, [("Retime OFF", 10, 0), ("Retime ON", 10, 1)]),
            ("Inversion", 15, [("Inversion OFF", 11, 0), ("Inversion ON", 11, 1)]),
        ]
        for label_text, reg, choices in mode_options:
            frame = LabelFrame(left_frame, text=label_text)
            frame.pack(fill="x", padx=5, pady=2)
            for i, (text, bit, val) in enumerate(choices):
                Radiobutton(frame, text=text, variable=self.reg_settings[reg][1][bit], value=val).pack(side="left",
                                                                                                          padx=5)

        for idx, (lbl, var) in enumerate([("kp_dco (0~15):", self.__var_kp),
                                          ("ki_dco (0~15):", self.__var_ki),
                                          ("init_dco (0~1023):", self.__var_init_dco)]):
            row = Frame(left_frame)
            row.pack(fill="x", padx=5, pady=2)
            Label(row, text=lbl, width=18, anchor="w").grid(row= 0, column = 0)
            Entry(row, textvariable=var["value"], width=6).grid(row= 0, column = 1)
            var["frame"] = Frame(row)
            Checkbutton(row, text="스윕 사용", variable=var["sweep"],
                                command=lambda index=idx: toggle_frame(self.__var_spi[index]["frame"],
                                                                       self.__var_spi[index]["sweep"].get())) \
                    .grid(row=0, column=2, sticky="w", padx=5)
            for row_idx, (label, val) in enumerate([("시작", var["start"]),
                                                ("종료", var["stop"]),
                                                ("스텝", var["step"])]):
                Label(var["frame"], text=label).pack(side="left")
                Entry(var["frame"], textvariable=val, width=7).pack(side="left")
            var["frame"].grid(row=1, column = 0, columnspan = 3)
            toggle_frame(var["frame"], var["sweep"].get())

        adv_frame = LabelFrame(left_frame, text="수동 입력")
        adv_frame.pack(fill="x", padx=5, pady=5)
        Label(adv_frame, text="주소 (Dec) :").grid(row=0, column=0, padx=5, sticky="e")
        Entry(adv_frame, textvariable=self.adv_addr, width=6).grid(row=0, column=1, padx=5)
        Label(adv_frame, text="값 (Hex) :").grid(row=0, column=2, padx=5, sticky="e")
        Entry(adv_frame, textvariable=self.adv_val, width=6).grid(row=0, column=3, padx=5)
        Button(adv_frame, text="쓰기", command=self.write_manual_register).grid(row=0, column=4, padx=10)

        self.status_label = Label(left_frame, text="", font=("Arial", 10))
        self.status_label.pack(pady=5)

        Button(left_frame, text="레지스터 쓰기", command=self.write_all_registers).pack(pady=5)

        right_frame = Frame(tab)
        right_frame.pack(side="right", padx=10, pady=10, anchor="n")

        self.tree = Treeview(right_frame, columns=("Address", "Value"), show="headings", height=20)
        self.tree.heading("Address", text="Address")
        self.tree.heading("Value", text="Value")
        self.tree.column("Address", width=80, anchor="center")
        self.tree.column("Value", width=100, anchor="center")
        self.tree.pack()

        Button(right_frame, text="레지스터 읽기", command=self.read_registers).pack(pady=5)

    def write_all_registers(self):
        for reg_addr, (default_bin, bit_settings) in self.reg_settings.items():
            print(reg_addr)
            binary = list(default_bin)
            for bit, var in bit_settings.items():
                binary[15 - bit] = str(var.get())
            try:
                if reg_addr == 0:
                    ki_bin = f"{int(self.__var_ki["value"].get()):04b}"
                    kp_bin = f"{int(self.__var_kp["value"].get()):04b}"
                    binary[0:4] = list(ki_bin)
                    binary[4:8] = list(kp_bin)
                elif reg_addr == 1:
                    init_bin = f"{self.__var_init_dco["value"].get():010b}"
                    binary[6:] = list(init_bin)
            except Exception as e:
                self.status_label.config(text=f"입력 오류: {e}", foreground="red")
                return

            hex_val = bin16_to_hex4("".join(binary))
            try:
                write_register(reg_addr, hex_val)
                self.status_label.config(text="쓰기 완료", foreground="green")
            except Exception as e:
                self.status_label.config(text=str(e), foreground="red")

    def write_manual_register(self):
        try:
            addr = int(self.adv_addr.get())
            val = self.adv_val.get().upper()
            if not (0 <= addr <= 255):
                raise ValueError("주소는 0~255")
            if not (len(val) == 4 and all(c in "0123456789ABCDEF" for c in val)):
                raise ValueError("4자리 16진수만 입력")
            write_register(addr, val)
            self.status_label.config(text="쓰기 완료", foreground="green")
        except Exception as e:
            self.status_label.config(text=f"입력 오류: {e}", foreground="red")

    def read_registers(self):
        try:
            a = read_register(2, 20)
            read_values = [f"{a[i]:02X}{a[i + 1]:02X}" for i in range(0, 40, 2)]
            addresses = [f"{hex(i)[2:].upper()}" for i in range(0, len(read_values))]
            self.tree.delete(*self.tree.get_children())
            for addr, val in zip(addresses, read_values):
                self.tree.insert("", "end", values=(addr, val))

            for reg_idx, val_hex in enumerate(read_values):
                reg_addr = reg_idx
                if reg_addr in self.reg_settings:
                    bin_val = f"{int(val_hex, 16):016b}"
                    for bit, var in self.reg_settings[reg_addr][1].items():
                        var.set(int(bin_val[15 - bit]))

                    if reg_addr == 0:
                        ki = int(bin_val[0:4], 2)
                        kp = int(bin_val[4:8], 2)
                        self.__var_ki["value"].set(ki)
                        self.__var_kp["value"].set(kp)
                    elif reg_addr == 1:
                        init_dco = int(bin_val[6:], 2)
                        self.__var_init_dco["value"].set(init_dco)

        except Exception as e:
            self.tree.delete(*self.tree.get_children())
            self.tree.insert("", "end", values=("오류", str(e)))

    def tab_E36313A(self, notebook: Notebook) -> None:
        tab = Frame(notebook)
        notebook.add(tab, text="전원 설정 (E36313A)")

        for idx_psu, key_psu in enumerate(["E36313A - 1", "E36313A - 2"]):
            frame_psu = LabelFrame(tab, text=key_psu)
            frame_psu.grid(row=idx_psu*2, column=0, sticky=tk.W, padx=10, pady=8)

            self.__var_psu[key_psu] = {}

            ctrl = Frame(frame_psu)
            ctrl.grid(row=0, column=0, sticky=tk.W, columnspan=3)

            Button(ctrl, text="전체 설정 적용", command=lambda  pk=key_psu: self.apply_setting_all(pk)).pack(side="left", padx=4)
            Button(ctrl, text="전체 ON", command=lambda pk=key_psu: self.channel_on_all(pk)).pack(side="left", padx=4)
            Button(ctrl, text="전체 OFF", command=lambda pk=key_psu: self.channel_off_all(pk)).pack(side="left", padx=4)

            self.__var_psu[key_psu]["err"] = StringVar(value="")

            for idx_ch, key_ch in enumerate([1, 2, 3]):
                f_ch = LabelFrame(frame_psu, text=f"채널 {idx_ch+1}")
                f_ch.grid(row=1, column=idx_ch, padx=4, pady=4, sticky=tk.N)

                v: dict[str, DoubleVar | BooleanVar | Frame] = {k: tk.DoubleVar() for k in ("voltage", "current", "ovp", "start", "stop", "step")}
                v["ocp"] = tk.BooleanVar()
                v["sweep"] = tk.BooleanVar()
                self.__var_psu[key_psu][key_ch] = v

                v["voltage"].set(0.9)
                v["current"].set(0.1)
                v["ovp"].set(10)
                v["start"].set(1.0)
                v["stop"].set(1.0)
                v["step"].set(0.1)

                row = 0
                for label, key, unit in [("전압", "voltage", "V"),
                                         ("전류", "current", "A"),
                                         ("OVP", "ovp",     "V")]:
                    Label(f_ch, text=label).grid(row=row, column=0, sticky="e")
                    Entry(f_ch, textvariable=v[key], width=6).grid(row=row, column=1)
                    Label(f_ch, text=unit).grid(row=row, column=2, sticky="w")
                    row += 1

                Checkbutton(f_ch, text="OCP 사용", variable=v["ocp"]).grid(row=row, column=0, columnspan=3, sticky="w")
                row += 1

                Checkbutton(f_ch, text="스윕 사용", variable=v["sweep"],
                                command=lambda pk=key_psu, ch=key_ch: toggle_frame(self.__var_psu[pk][ch]["sweep_frame"],
                                                                                   self.__var_psu[pk][ch]["sweep"].get())) \
                    .grid(row=row, column=0, columnspan=3, sticky="w")
                row += 1

                v["sweep_frame"] = Frame(f_ch)
                v["sweep_frame"].grid(row=row, column=0, columnspan=3, pady=4)

                for row_idx_2, (label, key) in enumerate([("시작", "start"),
                                                          ("종료", "stop"),
                                                          ("스텝", "step")]):
                    Label(v["sweep_frame"], text=label).grid(row=row_idx_2, column=0, sticky="e")
                    Entry(v["sweep_frame"], textvariable=v[key], width=5).grid(row=row_idx_2, column=1)
                    Label(v["sweep_frame"], text="V").grid(row=row_idx_2, column=2, sticky="w")

                btn_box: Frame = Frame(f_ch)
                btn_box.grid(row=row+3, column=0, columnspan=3)
                Button(btn_box, text="출력 ON", command=lambda pk=key_psu, ch=key_ch: self.channel_on(pk, ch)).pack(fill="x")
                Button(btn_box, text="출력 OFF", command=lambda pk=key_psu, ch=key_ch: self.channel_off(pk, ch)).pack(fill="x")
                Button(btn_box, text="설정 적용", command=lambda pk=key_psu, ch=key_ch: self.apply_setting(pk, ch)).pack(fill="x")

                v["sweep_frame"].grid_remove()

            Label(tab, textvariable=self.__var_psu[key_psu]["err"], foreground="red") \
                .grid(row=idx_psu * 2 + 1, column=0, sticky="w")

    def channel_on(self, pk, ch):
        if pk == 'E36313A - 1':
            self.__psu1.pwr_on(ch)
        elif pk == 'E36313A - 2':
            self.__psu2.pwr_on(ch)

    def channel_off(self, pk, ch):
        if pk == 'E36313A - 1':
            self.__psu1.pwr_off(ch)
        elif pk == 'E36313A - 2':
            self.__psu2.pwr_off(ch)

    def channel_on_all(self, pk):
        if pk == 'E36313A - 1':
            for i in range (1, 4):
                self.__psu1.pwr_on(i)
        elif pk == 'E36313A - 2':
            for i in range (1, 4):
                self.__psu2.pwr_on(i)

    def channel_off_all(self, pk):
        if pk == 'E36313A - 1':
            for i in range (1, 4):
                self.__psu1.pwr_off(i)
        elif pk == 'E36313A - 2':
            for i in range (1, 4):
                self.__psu2.pwr_off(i)

    def apply_setting(self, pk: str, ch: int):
        ch_settings = {'voltage': self.__var_psu[pk][ch]["voltage"].get(),
                       'current': self.__var_psu[pk][ch]["current"].get(),
                       'ovp': self.__var_psu[pk][ch]["ovp"].get(),
                       'ocp': self.__var_psu[pk][ch]["ocp"].get()}
        if pk == 'E36313A - 1':
            self.__psu1.apply_channel_setting(ch_settings, ch)
        elif pk == 'E36313A - 2':
            self.__psu2.apply_channel_setting(ch_settings, ch)

    def apply_setting_all(self, pk):
        for i in range(1, 4):
            ch_settings = {'voltage': self.__var_psu[pk][i]["voltage"].get(),
                           'current': self.__var_psu[pk][i]["current"].get(),
                           'ovp': self.__var_psu[pk][i]["ovp"].get(),
                           'ocp': self.__var_psu[pk][i]["ocp"].get()}
            if pk == 'E36313A - 1':
                self.__psu1.apply_channel_setting(ch_settings, i)
            elif pk == 'E36313A - 2':
                self.__psu2.apply_channel_setting(ch_settings, i)

    def tab_SMB100B(self, notebook: Notebook) -> None:
        tab = Frame(notebook)
        notebook.add(tab, text="RF 설정 (SMB100B)")

        frame_freq: LabelFrame = LabelFrame(tab, text="주파수 설정")
        frame_freq.grid(row=0, column=0, padx=10, pady=10, sticky="nw")

        label_freq: Label = Label(frame_freq, text="주파수")
        entry_freq: Entry = Entry(frame_freq, textvariable=self.__var_freq, width=10)
        combo_freq: Combobox = Combobox(frame_freq, textvariable=self.__var_unit, values=["Hz", "kHz", "MHz", "GHz"],
                                        width=5, state="readonly")
        chk_btn_freq_sweep: Checkbutton = Checkbutton(frame_freq, text="스윕 사용", variable=self.__var_freq_sweep,
                                                      command=lambda:toggle_frame(frame_freq_sweep,
                                                                                   self.__var_freq_sweep.get()))

        frame_freq_sweep: Frame = Frame(frame_freq)
        for row_idx, (label, var) in enumerate([("시작", self.__var_freq_start),
                                                ("종료", self.__var_freq_stop),
                                                ("스텝", self.__var_freq_step)]):
            Label(frame_freq_sweep, text=label).grid(row=row_idx, column=0, sticky="e")
            Entry(frame_freq_sweep, textvariable=var, width=7).grid(row=row_idx, column=1)
            Label(frame_freq_sweep, textvariable=self.__var_unit).grid(row=row_idx, column=2, sticky="w")

        label_freq.grid(row=0, column=0, sticky="e")
        entry_freq.grid(row=0, column=1)
        combo_freq.grid(row=0, column=2)
        chk_btn_freq_sweep.grid(row=1, column=0, columnspan=3, sticky="w")
        frame_freq_sweep.grid(row=2, column=0, columnspan=3)
        frame_freq_sweep.grid_remove()

        frame_pwr: LabelFrame = LabelFrame(tab, text="출력레벨 설정")
        frame_pwr.grid(row=0, column=1, padx=10, pady=10, sticky="nw")
        chk_btn_pwr_sweep: Checkbutton = Checkbutton(frame_pwr, text="스윕 사용", variable=self.__var_pwr_sweep,
                                                     command=lambda: toggle_frame(frame_pwr_sweep,
                                                                                  self.__var_pwr_sweep.get()))

        frame_pwr_sweep: Frame = Frame(frame_pwr)
        for row_idx, (label, var) in enumerate([("시작", self.__var_pwr_start),
                                                ("종료", self.__var_pwr_stop),
                                                ("스텝", self.__var_pwr_step)]):
            Label(frame_pwr_sweep, text=label).grid(row=row_idx, column=0, sticky="e")
            Entry(frame_pwr_sweep, textvariable=var, width=7).grid(row=row_idx, column=1)
            Label(frame_pwr_sweep, text="dBm").grid(row=row_idx, column=2, sticky="w")

        label_pwr: Label = Label(frame_pwr, text="출력레벨 (dBm)")
        label_pwr.grid(row=0, column=0, sticky="e")
        Entry(frame_pwr, textvariable=self.__var_pwr, width=10).grid(row=0, column=1)
        chk_btn_pwr_sweep.grid(row=1, column=0, columnspan=3, sticky="w")
        frame_pwr_sweep.grid(row=2, column=0, columnspan=2)
        frame_pwr_sweep.grid_remove()

        frame_ctrl: LabelFrame = LabelFrame(tab, text="설정 적용")
        frame_ctrl.grid(row=1, column=0, padx=10, pady=10)

        btn_apply_freq: Button = Button(frame_ctrl, text="주파수 설정 적용", command=lambda : self.__sgu.set_frequency(change_freq_unit(self.__var_freq.get(), self.__var_unit.get())))
        btn_apply_level: Button = Button(frame_ctrl, text="출력레벨 설정 적용", command=lambda : self.__sgu.set_power(self.__var_pwr.get()))
        btn_rf_on: Button = Button(frame_ctrl, text="RF 출력 ON", command=lambda : self.__sgu.rf_on())
        btn_rf_off: Button = Button(frame_ctrl, text="RF 출력 OFF", command=lambda : self.__sgu.rf_off())

        btn_apply_freq.grid(row=0, column=0, padx=5, pady=5)
        btn_apply_level.grid(row=0, column=1, padx=5, pady=5)
        btn_rf_on.grid(row=1, column=0, padx=5, pady=5)
        btn_rf_off.grid(row=1, column=1, padx=5, pady=5)

    def tab_FSV3000(self, notebook: Notebook) -> None:
        tab = Frame(notebook)
        notebook.add(tab, text="스펙트럼 분석기 (FSV3000)")

        frame_capture = LabelFrame(tab, text="스크린 캡처")
        frame_capture.pack(fill="both", padx=10, pady=10)

        frame_sau_dir: Frame = Frame(frame_capture)
        label_sau_dir: Label = Label(frame_sau_dir, text="USB 저장 경로:")
        entry_sau_dir: Entry = Entry(frame_sau_dir, textvariable=self.__var_dir, width=30)

        frame_ctrl: Frame = Frame(frame_capture)
        btn_auto_set: Button = Button(frame_ctrl, text="Auto Set - All", command=self.__sau.auto_set_all)
        btn_capture_spec: Button = Button(frame_ctrl, text="Power Spectrum Capture", command=lambda : self.__sau.capture_spectrum(self.__var_dir.get()))
        btn_capture_noise: Button = Button(frame_ctrl, text="Phase Noise Capture", command=lambda : self.__sau.capture_phase_noise(self.__var_dir.get()))

        frame_sau_dir.pack(side="top", pady=10)
        label_sau_dir.pack(side="left")
        entry_sau_dir.pack(side="left")

        frame_ctrl.pack(side="top")
        btn_auto_set.pack(side="left", padx=5)
        btn_capture_spec.pack(side="left", padx=5)
        btn_capture_noise.pack(side="left", padx=5)

        frame_auto_set = LabelFrame(tab, text="자동 설정")
        frame_auto_set.pack(fill="both", padx=10, pady=10)

        frame_btn_auto_set = Frame(frame_auto_set)
        frame_btn_auto_set.pack(pady=10)

        btn_auto_all: Button = Button(frame_btn_auto_set, text="ALL",
                                      command=lambda: self.__sau.auto_set_all())
        btn_auto_freq: Button = Button(frame_btn_auto_set, text="FREQ",
                                       command=lambda: self.__sau.auto_set_freq())
        btn_auto_level: Button = Button(frame_btn_auto_set, text="LEVEL",
                                       command=lambda: self.__sau.auto_set_level())

        btn_auto_all.pack(side="left", padx=5)
        btn_auto_freq.pack(side="left", padx=5)
        btn_auto_level.pack(side="left", padx=5)


        frame_setting: LabelFrame = LabelFrame(tab, text="파라미터 설정")
        frame_setting.pack(fill="both", padx=10, pady=10)

        frame_freq = Frame(frame_setting)
        frame_freq.pack(pady=5)

        label_freq: Label = Label(frame_freq, text="주파수")
        entry_freq: Entry = Entry(frame_freq, textvariable=self.__var_center_freq_hz, width=10)
        combo_freq: Combobox = Combobox(frame_freq, textvariable=self.__var_unit_center, values=["Hz", "kHz", "MHz", "GHz"],
                                        width=5, state="readonly")
        btn_freq: Button = Button(frame_freq, text="주파수 설정",
                                  command=lambda: self.__sau.set_frequency(change_freq_unit(self.__var_center_freq_hz.get(), self.__var_unit_center.get())))

        label_freq.pack(side="left", padx=5)
        entry_freq.pack(side="left", padx=5)
        combo_freq.pack(side="left", padx=5)
        btn_freq.pack(side="left", padx=5)

        frame_span = Frame(frame_setting)
        frame_span.pack(pady=5)

        label_span: Label = Label(frame_span, text="Span")
        entry_span: Entry = Entry(frame_span, textvariable=self.__var_span_hz, width=10)
        combo_span: Combobox = Combobox(frame_span, textvariable=self.__var_unit_span, values=["Hz", "kHz", "MHz", "GHz"],
                                        width=5, state="readonly")
        btn_span: Button = Button(frame_span, text="Span 설정",
                                  command=lambda: self.__sau.set_span(change_freq_unit(self.__var_span_hz.get(), self.__var_unit_span.get())))

        label_span.pack(side="left", padx=5)
        entry_span.pack(side="left", padx=5)
        combo_span.pack(side="left", padx=5)
        btn_span.pack(side="left", padx=5)

        frame_rbw = Frame(frame_setting)
        frame_rbw.pack(pady=5)

        label_rbw: Label = Label(frame_rbw, text="RBW")
        entry_rbw: Entry = Entry(frame_rbw, textvariable=self.__var_rbw_ratio, width=10)
        label_rbw_unit: Label = Label(frame_rbw, text="%")
        btn_rbw: Button = Button(frame_rbw, text="RBW 설정",
                                 command=lambda: self.__sau.set_resolution_bw(self.__var_rbw_ratio.get()))

        label_rbw.pack(side="left", padx=5)
        entry_rbw.pack(side="left", padx=5)
        label_rbw_unit.pack(side="left")
        btn_rbw.pack(side="left", padx=5)

        frame_offset_start = Frame(frame_setting)
        frame_offset_start.pack(pady=5)

        label_offset_start: Label = Label(frame_offset_start, text="Offset Start")
        entry_offset_start: Entry = Entry(frame_offset_start, textvariable=self.__var_offset_start, width=10)
        combo_offset_start: Combobox = Combobox(frame_offset_start, textvariable=self.__var_unit_offset_start, values=["Hz", "kHz", "MHz", "GHz"],
                                        width=5, state="readonly")
        btn_offset_start: Button = Button(frame_offset_start, text="Offset Start 설정",
                                          command=lambda: self.__sau.set_offset_start(change_freq_unit(self.__var_offset_start.get(), self.__var_unit_offset_start.get())))

        label_offset_start.pack(side="left", padx=5)
        entry_offset_start.pack(side="left", padx=5)
        combo_offset_start.pack(side="left", padx=5)
        btn_offset_start.pack(side="left", padx=5)

        frame_offset_stop = Frame(frame_setting)
        frame_offset_stop.pack(pady=5)

        label_offset_stop: Label = Label(frame_offset_stop, text="Offset Stop")
        entry_offset_stop: Entry = Entry(frame_offset_stop, textvariable=self.__var_offset_stop, width=10)
        combo_offset_stop: Combobox = Combobox(frame_offset_stop, textvariable=self.__var_unit_offset_stop,
                                                values=["Hz", "kHz", "MHz", "GHz"],
                                                width=5, state="readonly")
        btn_offset_stop: Button = Button(frame_offset_stop, text="Offset Stop 설정",
                                         command=lambda: self.__sau.set_offset_stop(change_freq_unit(self.__var_offset_stop.get(), self.__var_unit_offset_stop.get())))

        label_offset_stop.pack(side="left", padx=5)
        entry_offset_stop.pack(side="left", padx=5)
        combo_offset_stop.pack(side="left", padx=5)
        btn_offset_stop.pack(side="left", padx=5)

        frame_scene = LabelFrame(tab, text="화면 전환")
        frame_scene.pack(fill="both", padx=10, pady=10)

        frame_spectrum_btn = Frame(frame_scene)
        frame_spectrum_btn.pack(pady=10)

        btn_set_spec: Button = Button(frame_spectrum_btn, text="Set Spectrum Plot", command=lambda: self.__sau.set_spectrum())
        btn_set_marker_table: Button = Button(frame_spectrum_btn, text="Set Marker Table", command=lambda: self.__sau.set_spectrum_table())
        btn_remove_marker_table: Button = Button(frame_spectrum_btn, text="Remove Marker Table", command=lambda: self.__sau.remove_spectrum_table())

        btn_set_spec.pack(side="left", padx=5)
        btn_set_marker_table.pack(side="left", padx=5)
        btn_remove_marker_table.pack(side="left", padx=5)

        frame_phase_btn = Frame(frame_scene)
        frame_phase_btn.pack(pady=10)

        btn_set_noise: Button = Button(frame_phase_btn, text="Set Phase Noise Plot", command=lambda: self.__sau.set_phase_noise())
        btn_set_phase_table: Button = Button(frame_phase_btn, text="Set Phase Table", command=lambda: self.__sau.set_noise_table())
        btn_remove_phase_table: Button = Button(frame_phase_btn, text="Remove Phase Table", command=lambda: self.__sau.remove_noise_table())

        btn_set_noise.pack(side="left", padx=5)
        btn_set_phase_table.pack(side="left", padx=5)
        btn_remove_phase_table.pack(side="left", padx=5)

        frame_setting_btn = LabelFrame(tab, text="설정 버튼")
        frame_setting_btn.pack(fill="both", padx=10, pady=10)

        frame_setting_btn = Frame(frame_setting_btn)
        frame_setting_btn.pack(pady=10)

        btn_single_sweep: Button = Button(frame_setting_btn, text="Single Sweep", command=lambda: self.__sau.single_sweep())
        btn_continuous_sweep: Button = Button(frame_setting_btn, text="Continous Sweep", command=lambda: self.__sau.continuous_sweep())
        btn_marker_peak_search: Button = Button(frame_setting_btn, text="Search Marker Peak", command=lambda: self.__sau.marker_peak_search())
        btn_get_all_markers: Button = Button(frame_setting_btn, text="Get All Markers", command=lambda: self.__sau.get_marker_value())
        btn_verify_off: Button = Button(frame_setting_btn, text="Verify Off", command=lambda: self.__sau.set_verify_off())
        btn_set_jitter: Button = Button(frame_setting_btn, text="Jitter",
                                        command=lambda: self.__sau.set_jitter(change_freq_unit(self.__var_center_freq_hz.get(), self.__var_unit_center.get()),change_freq_unit(self.__var_offset_start.get(), self.__var_unit_offset_start.get()) ,change_freq_unit(self.__var_offset_stop.get(), self.__var_unit_offset_stop.get())))

        btn_single_sweep.pack(side="left", padx=5)
        btn_continuous_sweep.pack(side="left", padx=5)
        btn_marker_peak_search.pack(side="left", padx=5)
        btn_get_all_markers.pack(side="left", padx=5)
        btn_verify_off.pack(side="left", padx=5)
        btn_set_jitter.pack(side="left", padx=5)

    def tab_measurement(self, notebook: Notebook) -> None:
        tab = Frame(notebook)
        notebook.add(tab, text="측정 실행")

        p_frame = Frame(tab)
        p_frame.pack(pady=10)

        label_dir: Label = Label(p_frame, text="Power Supply & Signal Generator Log 저장 경로")
        entry_dir: Entry = Entry(p_frame, width=30, textvariable=self.__var_log_dir)

        label_dir.pack(side="top", padx=5)
        entry_dir.pack(side="top", fill="y")

        progress: Progressbar = Progressbar(tab, orient="horizontal", length=400, mode="determinate")
        progress.pack(pady=(5, 0))

        label_status: Label = Label(tab)
        set_label_text(label_status, "대기 중...")
        label_status.pack()

        btn_meas: Button = Button(tab, text="측정 시작", command=lambda: measurement(
                                                                                 self.__var_init_dco["value"].get(),
                                                                                 self.__var_init_dco["sweep"].get(),
                                                                                 self.__var_init_dco["start"].get(),
                                                                                 self.__var_init_dco["stop"].get(),
                                                                                 self.__var_init_dco["step"].get(),
                                                                                 self.reg_settings[0][1][4].get(),
                                                                                 self.reg_settings[0][1][6].get(),
                                                                                 self.__var_kp["value"].get(),
                                                                                 self.__var_kp["sweep"].get(),
                                                                                 self.__var_kp["start"].get(),
                                                                                 self.__var_kp["stop"].get(),
                                                                                 self.__var_kp["step"].get(),
                                                                                 self.__var_ki["value"].get(),
                                                                                 self.__var_ki["sweep"].get(),
                                                                                 self.__var_ki["start"].get(),
                                                                                 self.__var_ki["stop"].get(),
                                                                                 self.__var_ki["step"].get(),
                                                                                 self.__sau,
                                                                                 self.__sgu,
                                                                                 self.__psu1,
                                                                                 self.__psu2,
                                                                                 self.__var_log_dir.get(),
                                                                                 self.__var_dir.get(),
                                                                                 self.__var_freq_sweep.get(),
                                                                                 change_freq_unit(self.__var_freq.get(), self.__var_unit.get()),
                                                                                 change_freq_unit(self.__var_freq_start.get(), self.__var_unit.get()),
                                                                                 change_freq_unit(self.__var_freq_stop.get(), self.__var_unit.get()),
                                                                                 change_freq_unit(self.__var_freq_step.get(), self.__var_unit.get()),
                                                                                 change_freq_unit(self.__var_offset_start.get(), self.__var_unit_offset_start.get()),
                                                                                 change_freq_unit(self.__var_offset_stop.get(), self.__var_unit_offset_stop.get()),
                                                                                 change_freq_unit(self.__var_span_hz.get(), self.__var_unit_span.get()),
                                                                                 self.__var_rbw_ratio.get(),
                                                                                 self.__var_psu['E36313A - 1'][1]["sweep"].get(),
                                                                                 self.__var_psu['E36313A - 1'][1]["voltage"].get(),
                                                                                 self.__var_psu['E36313A - 1'][1]['start'].get(),
                                                                                 self.__var_psu['E36313A - 1'][1]['stop'].get(),
                                                                                 self.__var_psu['E36313A - 1'][1]['step'].get(),
                                                                                 self.__var_pwr.get(),
                                                                                 self.__var_psu['E36313A - 1'][1]['current'].get(),
                                                                                 self.__var_psu['E36313A - 1'][2]["sweep"].get(),
                                                                                 self.__var_psu['E36313A - 1'][2]["voltage"].get(),
                                                                                 self.__var_psu['E36313A - 1'][2]['start'].get(),
                                                                                 self.__var_psu['E36313A - 1'][2]['stop'].get(),
                                                                                 self.__var_psu['E36313A - 1'][2]['step'].get(),
                                                                                 self.__var_psu['E36313A - 1'][2]['current'].get(),
                                                                                 self.__var_psu['E36313A - 1'][3]["sweep"].get(),
                                                                                 self.__var_psu['E36313A - 1'][3]["voltage"].get(),
                                                                                 self.__var_psu['E36313A - 1'][3]['start'].get(),
                                                                                 self.__var_psu['E36313A - 1'][3]['stop'].get(),
                                                                                 self.__var_psu['E36313A - 1'][3]['step'].get(),
                                                                                 self.__var_psu['E36313A - 1'][3]['current'].get(),
                                                                                 self.__var_psu['E36313A - 2'][1]["sweep"].get(),
                                                                                 self.__var_psu['E36313A - 2'][1]["voltage"].get(),
                                                                                 self.__var_psu['E36313A - 2'][1]['start'].get(),
                                                                                 self.__var_psu['E36313A - 2'][1]['stop'].get(),
                                                                                 self.__var_psu['E36313A - 2'][1]['step'].get(),
                                                                                 self.__var_psu['E36313A - 2'][1]['current'].get(),
                                                                                 self.__var_psu['E36313A - 2'][2]["sweep"].get(),
                                                                                 self.__var_psu['E36313A - 2'][2]["voltage"].get(),
                                                                                 self.__var_psu['E36313A - 2'][2]['start'].get(),
                                                                                 self.__var_psu['E36313A - 2'][2]['stop'].get(),
                                                                                 self.__var_psu['E36313A - 2'][2]['step'].get(),
                                                                                 self.__var_psu['E36313A - 2'][2]['current'].get(),
                                                                                 self.__var_psu['E36313A - 2'][3]["sweep"].get(),
                                                                                 self.__var_psu['E36313A - 2'][3]["voltage"].get(),
                                                                                 self.__var_psu['E36313A - 2'][3]['start'].get(),
                                                                                 self.__var_psu['E36313A - 2'][3]['stop'].get(),
                                                                                 self.__var_psu['E36313A - 2'][3]['step'].get(),
                                                                                 self.__var_psu['E36313A - 2'][3]['current'].get()))
        btn_meas.pack(pady=10)

    def show(self, window: tk.Tk = tk.Tk()) -> None:
        window.title("AMS - 측정 자동화 시스템")

        notebook = Notebook(window)
        self.tab_connection(notebook)
        self.tab_spi(notebook)
        self.tab_E36313A(notebook)
        self.tab_SMB100B(notebook)
        self.tab_FSV3000(notebook)
        self.tab_measurement(notebook)
        notebook.pack(fill="both", expand=True)
        window.mainloop()

if __name__ == "__main__":
    app = Application()
    app.show()
