#! /usr/bin/env python
# -*- coding: utf-8 -*-

import ttk
import time
import tkFont
import logging
import datetime
import platform
import threading
import Tkinter as tk

from UI.MainFrm import MainFrame
from Utils.SerialHelper import SerialHelper

# 根据系统 引用不同的库
if platform.system() == "Windows":
    import pywinusb.hid as hid
    from Utils.WinUsbHelper import hidHelper
    from  serial.tools import list_ports
else:
    import usb.core
    from Utils.UsbHelper import usbHelper
    import glob, os, re

logging.basicConfig(level=logging.DEBUG,
                    format='%(asctime)s %(filename)s[line:%(lineno)d] %(levelname)s %(message)s',
                    datefmt='%a, %d %b %Y %H:%M:%S')

class MainSlaveTool(MainFrame):
    '''
    main func class
    '''

    def __init__(self, master=None):
        '''
        constuctor
        '''
        super(MainSlaveTool, self).__init__(master)
        self.root = master

        self.vid = None
        self.pid = None
        self.usb_listbox = list()
        self.serial_listbox = list()
        self.find_all_devices()

        self.serial_receive_count = 0
        self.serial_recieve_data = ""

    # start ---- 轮循设备是否连接 ---- 
    def find_all_devices(self):
        '''
        线程检测连接设备的状态
        '''
        self.find_all_usb_devices()
        self.find_all_serial_devices()
        self.start_thread_timer(self.find_all_devices, 1)

    def find_all_usb_devices(self):
        '''
        检查USB设备
        '''
        try:
            self.temp_usb_list = list()
            if platform.system() == "Windows":
                usb_dev = hid.find_all_hid_devices()
                for dev in usb_dev:
                    vid = hex(dev.vendor_id)[2:].rjust(4, "0")
                    pid = hex(dev.product_id)[2:].rjust(4, "0")
                    dev_info = "VID:{0} PID:{1}".format(vid, pid)
                    self.temp_usb_list.append(dev_info)
            else:
                usb_dev = usb.core.find(find_all=True)
                for dev in usb_dev:
                    vid = hex(dev.idVendor)[2:].rjust(4, "0")
                    pid = hex(dev.idProduct)[2:].rjust(4, "0")
                    dev_info = "VID:{0} PID:{1}".format(vid, pid)
                    self.temp_usb_list.append(dev_info)
            for item in self.temp_usb_list:
                if item not in self.usb_listbox:
                    self.usb_frm.frm_left_listbox.insert("end", item)
            for item in self.usb_listbox:
                if item not in self.temp_usb_list:
                    size = self.usb_frm.frm_left_listbox.size()
                    index = list(self.usb_frm.frm_left_listbox.get(0, size)).index(item)
                    self.usb_frm.frm_left_listbox.delete(index)

            # 检测到usb设备被拔出时，关闭usb设备
            if self.pid and self.vid:
                _vid = self.fill_zero(hex(self.vid)[2:])
                _pid = self.fill_zero(hex(self.pid)[2:])
                dev_info = "VID:{0} PID:{1}".format(_vid, _pid)
                if dev_info not in self.temp_usb_list:
                    self.Toggle()
                    self.vid = None
                    self.pid = None
            self.usb_listbox = self.temp_usb_list
        except Exception as e:
            logging.error(e)

    def find_all_serial_devices(self):
        '''
        检查串口设备
        '''
        try:
            if platform.system() == "Windows":
                self.temp_serial = list()
                for com in list(list_ports.comports()):
                    strCom = com[0].encode("utf-8") + ": " + com[1][:-7].encode("utf-8")
                    self.temp_serial.append(strCom)
                for item in self.temp_serial:
                    if item not in self.serial_listbox:
                        self.serial_frm.frm_left_listbox.insert("end", item)
                for item in self.serial_listbox:
                    if item not in self.temp_serial:
                        size = self.serial_frm.frm_left_listbox.size()
                        index = list(self.serial_frm.frm_left_listbox.get(0, size)).index(item)
                        self.serial_frm.frm_left_listbox.delete(index)

                self.serial_listbox = self.temp_serial

            elif platform.system() == "Linux":
                self.temp_serial = list()
                self.temp_serial = self.find_usb_tty()
                for item in self.temp_serial:
                    if item not in self.serial_listbox:
                        self.serial_frm.frm_left_listbox.insert("end", item)
                for item in self.serial_listbox:
                    if item not in self.temp_serial:
                        index = list(self.serial_frm.frm_left_listbox.get(0, self.serial_frm.frm_left_listbox.size())).index(item)
                        self.serial_frm.frm_left_listbox.delete(index)
                self.serial_listbox = self.temp_serial
        except Exception as e:
            logging.error(e)
    # end ---- 轮循设备是否连接 ---- 

    def Toggle(self, event=None):
        '''
        打开/关闭 设备
        '''
        if self.frm_top_btn_change["text"] == "USB":  # Serial
            self.serial_toggle()

    def Send(self):
        '''
        发送数据
        '''
        if self.frm_top_btn_change["text"] == "USB":  # Serial
            self.serial_send()

    # start ---- Serial ---- 
    def serial_toggle(self):
        '''
        打开/关闭串口设备
        '''
        if self.serial_frm.frm_left_btn["text"] == "Open":
            try:
                serial_index = self.serial_frm.frm_left_listbox.curselection()
                if serial_index:
                    self.currentStrCom = self.serial_frm.frm_left_listbox.get(serial_index).encode("utf-8")
                else:
                    self.currentStrCom = self.serial_frm.frm_left_listbox.get(self.serial_frm.frm_left_listbox.size() - 1).encode("utf-8")

                if platform.system() == "Windows":
                    self.port = self.currentStrCom.split(":")[0]
                elif platform.system() == "Linux":
                    self.port = self.currentStrCom
                self.baudrate = self.serial_frm.frm_left_combobox_baudrate.get()
                self.parity = self.serial_frm.frm_left_combobox_parity.get()
                self.databit = self.serial_frm.frm_left_combobox_databit.get()
                self.stopbit = self.serial_frm.frm_left_combobox_stopbit.get()
                self.ser = SerialHelper(Port=self.port,
                                        BaudRate=self.baudrate,
                                        ByteSize=self.databit,
                                        Parity=self.parity,
                                        Stopbits=self.stopbit)
                self.ser.on_connected_changed(self.serial_on_connected_changed)
            except Exception as e:
                logging.error(e)
                try:
                    self.frm_status_label["text"] = "Open [{0}] Failed!".format(self.currentStrCom)
                    self.frm_status_label["fg"] = "#DC143C"
                except Exception as ex:
                    logging.error(ex)

        elif self.serial_frm.frm_left_btn["text"] == "Close":
            self.ser.disconnect()
            self.serial_frm.frm_left_btn["text"] = "Open"
            self.serial_frm.frm_left_btn["bg"] = "#008B8B"
            self.serial_frm.frm_status_label["text"] = "Close Serial Successful!"
            self.serial_frm.frm_status_label["fg"] = "#8DEEEE"

    def SerialClear(self):
        '''
        clear serial receive text
        '''
        self.serial_receive_count = 0
        self.serial_frm.frm_right_receive.delete("0.0", "end")

    def get_threshold_value(self, *args):
        '''
        get threshold value
        '''
        try:
            self.ser.threshold_value = int(self.serial_frm.threshold_str.get())
        except:
            pass

    def serial_send(self):
        '''
        串口数据发送 CR 13; NL(LF) 10
        '''
        send_data = self.serial_frm.frm_right_send.get("0.0", "end").strip()
        if self.serial_frm.new_line_cbtn_var.get() == 1:  # 是否添加换行符
            send_data = send_data + "\n"

        if self.serial_frm.send_hex_cbtn_var.get() == 1:  # 是否使用16进制发送
            send_data = send_data.replace(" ", "").replace("\n", "10")
            self.ser.write(send_data, True)
        else:
            self.ser.write(send_data)

    def serial_on_connected_changed(self, is_connected):
        if is_connected:
            self.ser.connect()
            if self.ser._is_connected:
                self.serial_frm.frm_status_label["text"] = "Open [{0}] Successful!".format(self.currentStrCom)
                self.serial_frm.frm_status_label["fg"] = "#66CD00"
                self.serial_frm.frm_left_btn["text"] = "Close"
                self.serial_frm.frm_left_btn["bg"] = "#F08080"
                self.ser.on_data_received(self.serial_on_data_received)
            else:
                self.serial_frm.frm_status_label["text"] = "Open [{0}] Failed!".format(self.currentStrCom)
                self.serial_frm.frm_status_label["fg"] = "#DC143C"
        else:
            self.ser.disconnect()
            self.serial_frm.frm_left_btn["text"] = "Open"
            self.serial_frm.frm_left_btn["bg"] = "#008B8B"
            self.serial_frm.frm_status_label["text"] = "Close Serial Successful!"
            self.serial_frm.frm_status_label["fg"] = "#8DEEEE"

    def serial_on_data_received(self, data):
        '''
        '''
        self.serial_recieve_data += data
        if self.ser.threshold_value <= len(self.serial_recieve_data):
            if self.serial_frm.receive_hex_cbtn_var.get() == 1:
                self.serial_frm.frm_right_receive.insert("end", "[" + str(datetime.datetime.now()) + " - "
                                              + str(self.serial_receive_count) + "]:\n", "green")
                data_str = " ".join([hex(ord(x))[2:].upper().rjust(2, "0") for x in self.serial_recieve_data])
                self.serial_frm.frm_right_receive.insert("end", data_str + "\n")
                self.serial_frm.frm_right_receive.see("end")
            else:
                self.serial_frm.frm_right_receive.insert("end", "[" + str(datetime.datetime.now()) + " - "
                                              + str(self.serial_receive_count) + "]:\n", "green")
                self.serial_frm.frm_right_receive.insert("end", self.serial_recieve_data + "\n")
                self.serial_frm.frm_right_receive.see("end")
            self.serial_receive_count += 1
            self.serial_recieve_data = ""

    def find_usb_tty(self, vendor_id=None, product_id=None):
        '''
        查找Linux下的串口设备
        '''
        tty_devs = list()
        for dn in glob.glob('/sys/bus/usb/devices/*') :
            try:
                vid = int(open(os.path.join(dn, "idVendor" )).read().strip(), 16)
                pid = int(open(os.path.join(dn, "idProduct")).read().strip(), 16)
                if  ((vendor_id is None) or (vid == vendor_id)) and ((product_id is None) or (pid == product_id)) :
                    dns = glob.glob(os.path.join(dn, os.path.basename(dn) + "*"))
                    for sdn in dns :
                        for fn in glob.glob(os.path.join(sdn, "*")) :
                            if  re.search(r"\/ttyUSB[0-9]+$", fn) :
                                tty_devs.append(os.path.join("/dev", os.path.basename(fn)))
            except Exception as ex:
                pass
        return tty_devs
    # end ---- Serial ---- 

if __name__ == '__main__':
    '''
    main loop
    '''
    root = tk.Tk()
    root.columnconfigure(0, weight=1)
    root.rowconfigure(0, weight=1)
    root.geometry()

    monacofont = tkFont.Font(family="Monaco", size=16)
    root.option_add("*TCombobox*Listbox*background", "#292929")
    root.option_add("*TCombobox*Listbox*foreground", "#FFFFFF")
    root.option_add("*TCombobox*Listbox*font", monacofont)

    root.configure(bg="#292929")
    combostyle = ttk.Style()
    combostyle.theme_use('default')
    combostyle.configure("TCombobox",
                         selectbackground="#292929",
                         fieldbackground="#292929",
                         background="#292929",
                         foreground="#FFFFFF")

    app = MainSlaveTool(root)
    root.mainloop()
