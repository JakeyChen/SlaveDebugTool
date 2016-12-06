#! /usr/bin/env python
# -*- coding: utf-8 -*-

import ttk
import tkFont
import Tkinter as tk
import datetime
import threading

import PyTkinter as pytk
from SerialFrm import SerialFrame
from UsbFrm import UsbFrame

g_font = ("Monaco", 16)

class MainFrame(object):
    '''
    main frame
    '''

    def __init__(self, master=None):
        '''
        constructor
        '''
        self.root = master
        self.create_frame()

        self.state = True
        # self.root.attributes("-fullscreen", self.state)
        self.root.bind("<F11>", self.toggle_fullscreen)

    def create_frame(self):
        self.frm_top = pytk.PyLabelFrame(self.root)
        self.frm_main = pytk.PyLabelFrame(self.root)
        self.frm_top.pack(fill="both", expand=0)
        self.frm_main.pack(fill="both", expand=1)

        self.create_frm_top()
        self.create_frm_main()

        self.init_serial_frm()

    def create_frm_top(self):
        '''
        '''
        self.frm_top_label = pytk.PyLabel(self.frm_top, 
                                          text="Current Mode is [ Serial ].",
                                          anchor="w",
                                          font=g_font)
        self.frm_top_btn_change = pytk.PyButton(self.frm_top,
                                                text="USB",
                                                activebackground="#030303",
                                                activeforeground="#E0EEEE",
                                                bg="#4D4D4D",
                                                fg="#FFFFFF",
                                                width=10,
                                                font=("Monaco", 12),
                                                command=self.change_mode)
        self.frm_top_btn_import = pytk.PyButton(self.frm_top,
                                                text="Import",
                                                activebackground="#030303",
                                                activeforeground="#E0EEEE",
                                                bg="#4D4D4D",
                                                fg="#FFFFFF",
                                                width=10,
                                                font=("Monaco", 12),
                                                command=self.import_text)

        self.frm_top_btn_change.pack(fill="both", expand=0, padx=5, pady=2, side=tk.LEFT)
        self.frm_top_label.pack(fill="both", expand=1, padx=4, pady=2, side=tk.LEFT)
        self.frm_top_btn_import.pack(fill="both", expand=0, padx=4, pady=2, side=tk.LEFT)

    def create_frm_main(self):
        '''
        '''
        self.serial_frm = SerialFrame(self.frm_main)
        self.usb_frm = UsbFrame(self.frm_main)
        
        self.serial_frm.frm.pack(fill="both", expand=1, padx=2, pady=2)
        self.usb_frm.frm.pack_forget()

    def show_current_time(self):
        '''
        show computer current date
        '''
        self.frm_status_bottom_label_date["text"] = str(datetime.datetime.now())[:-7]
        self.root.after(2**8, self.show_current_time)

    def change_mode(self):
        '''
        change function mode
        '''
        if self.frm_top_btn_change["text"] == "USB":
            self.serial_frm.frm.pack_forget()
            self.usb_frm.frm.pack(fill="both", expand=1, padx=2, pady=2)
            self.frm_top_btn_change["text"] = "Serial"
            self.frm_top_label["text"] = "Current Mode is [ USB ]."
        elif self.frm_top_btn_change["text"] == "Serial":
            self.serial_frm.frm.pack(fill="both", expand=1, padx=2, pady=2)
            self.usb_frm.frm.pack_forget()
            self.frm_top_btn_change["text"] = "USB"
            self.frm_top_label["text"] = "Current Function is [ Serial ]."

    def import_text(self):
        '''
        '''
        pass

    def toggle_fullscreen(self, event=None):
        '''
        toggle fullscreen
        '''
        self.state = not self.state
        self.root.attributes("-fullscreen", self.state)

    def init_serial_frm(self):
        '''
        init serial frm
        '''
        self.serial_frm.frm_left_btn["command"] = self.Toggle
        self.serial_frm.frm_right_send_btn["command"] = self.Send

    def Toggle(self):
        '''
        toggle dev
        '''
        pass

    def Send(self):
        '''
        send msg to dev
        '''
        pass

    def insert_show_text(self, msg, location="end", color="myblue", newline=True):
        '''
        test: test info show insert
        '''
        self.test_frm.frm_top_txt_show.insert(location, msg, color)
        if newline:
            self.test_frm.frm_top_txt_show.insert("end", "\n")
        self.test_frm.frm_top_txt_show.see("end")
        self.test_frm.frm_top_txt_show.update()

    def start_thread_timer(self, callback, timer=1):
        '''
        util: start thread timer
        '''
        temp_thread = threading.Timer(timer, callback)
        temp_thread.setDaemon(True)
        temp_thread.start()

    def start_thread_target(self, callback, name="thread"):
        '''
        util: start thread target
        '''
        temp_thread = threading.Thread(target=callback, name=name)
        temp_thread.setDaemon(True)
        temp_thread.start()

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

    app = MainFrame(root)
    root.mainloop()
