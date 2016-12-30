#!/usr/bin/env python
# -*- coding: utf-8 -*-

import time
import usb
import threading

class usbHelper(object):
    def __init__(self, vid=0x11FA, pid=0x0206):
        '''
        constuctor
        '''
        self._vid = vid
        self._pid = pid
        self._is_connected = False
        self._handle = None

    def connect(self):
        '''
        connect usb device
        '''
        try:
            self.dev = usb.core.find(idVendor=self._vid, idProduct=self._pid)
            if self.dev:
                self.ep_in = self.dev[0][(0,0)][0].bEndpointAddress
                self.ep_out = self.dev[0][(0,0)][1].bEndpointAddress
                self.size = self.dev[0][(0,0)][1].wMaxPacketSize
            busses = usb.busses()
            for bus in busses:
                for device in bus.devices:
                    if device.idVendor == self._vid and device.idProduct == self._pid:
                        self._handle = device.open()
                        if self.dev.is_kernel_driver_active(0):
                            self._handle.detachKernelDriver(0)
                        self._handle.claimInterface(0)
            return True
        except Exception as e:
            self._is_connected = False
            return False   

    def disconnect(self):
        '''
        disconnect usb device
        '''
        if self._handle:
            self._handle.releaseInterface()

    def write(self, send_list, timeout=3000):
        '''
        write data to usb device,default timeout=3000ms=3s
        '''
        if self._handle:
            num = self._handle.interruptWrite(self.ep_out, send_list, timeout)
            return num
        return -1

    def on_connected_changed(self, func):
        '''
        set usb connected status change callback
        '''
        tConnected = threading.Thread(target=self._on_connected_changed, args=(func, ))
        tConnected.setDaemon(True)
        tConnected.start()

    def _on_connected_changed(self, func):
        '''
        set usb connected status change callback
        '''
        self._is_connected_temp = False
        while True:
            temp_dev = usb.core.find(idVendor=self._vid, idProduct=self._pid)
            self._is_connected = True if temp_dev else False
            if self._is_connected_temp != self._is_connected:
                func(self._is_connected)
            self._is_connected_temp = self._is_connected
            time.sleep(0.5)

    def on_data_received(self, func):
        '''
        set usb data recieved callback
        '''
        tDataReceived = threading.Thread(target=self._on_data_received, args=(func, ))
        tDataReceived.setDaemon(True)
        tDataReceived.start()
    
    def _on_data_received(self, func):
        '''
        set usb data recieved callback
        '''
        while True:
            if self._handle:
                try:
                    data = self._handle.interruptRead(self.ep_in, self.size, timeout=0)
                    if data:
                        func(data.tolist())
                except Exception as e:
                    self._handle = None
                    break

class testHelper(object):
    def __init__(self):
        self.myusb = usbHelper()
        self.myusb.on_connected_changed(self.myusb_on_connected_changed)

    def myusb_on_connected_changed(self, is_connected):
        if is_connected:
            print("Connected")
            self.myusb.connect()
            self.myusb.on_data_received(self.myusb_on_data_received)
        else:
            print("DisConnected")

    def myusb_on_data_received(self, data):
        print("".join([chr(i) for i in data[5:] if i != 0]))

if __name__ == '__main__':
    musb = testHelper()

    count = 0
    while count < 25:
        print("Count: %s"%count)
        time.sleep(1)
        count += 1
