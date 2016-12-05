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
                for com in list_ports.comports():
                    strCom = com[0] + ": " + com[1][:-7].decode("gbk").encode("utf-8")
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

    def Toggle(self):
        '''
        打开/关闭 设备
        '''
        

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
