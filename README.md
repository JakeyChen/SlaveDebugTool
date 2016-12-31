# SlaveDebugTool

* [Python GUI Programming (Tkinter)](https://www.tutorialspoint.com/python/python_gui_programming.htm)

* [Github pyserial](https://github.com/pyserial/pyserial/tree/master/examples)

* [Github pyusb](https://github.com/walac/pyusb/blob/master/docs/tutorial.rst)

* [Github pywinusb](https://github.com/rene-aguirre/pywinusb/tree/master/examples)


## win8下的效果图：

### 需要安装的库：

>pip install pyserial

>pip install pywinusb 

![](http://git.oschina.net/jakey.chen/SlaveDebugTool/tree/master/Images/win8_usb.png)

![](http://git.oschina.net/jakey.chen/SlaveDebugTool/tree/master/Images/win8_serial.png)


## ubuntu下的效果图(Ubuntu 16.04 GNOME)：

### 需要安装的库：

>sudo pip install pyserial

>sudo pip install pyusb 

>sudo apt-get install python-tk

![](http://git.oschina.net/jakey.chen/SlaveDebugTool/tree/master/Images/ubuntu_usb.png)

![](http://git.oschina.net/jakey.chen/SlaveDebugTool/blob/master/Images/ubuntu_serial.png?dir=0&filepath=Images%2Fubuntu_serial.png&oid=113f2396afb612f2921b7bff026ba2074a698b7a&sha=fe36a0c3b2b42c72369ac0a1e6849fb38ccb66c2)


# 使用技巧 (Serial)

在左侧列表框，可以显示出当前连接的Serial设备。

可以通过双击打开设备（或者点击下面的Open打开设备）

状态栏会有相应的提示信息

在发送对应的位置填写对应的字符串即可，比如要发送'abc'，直接填 'abc'即可

要按照16进制发送的话 勾选Hex 然后填写：0A 0B 0C 即可

接收框会实时显示收到的数据，第一位为计数位，可以知道一共收到了几条数据

点击Clear可以清楚计数和接收的数据


# 使用技巧 (USB)

在左侧列表框，可以显示出当前连接的USB设备。

可以通过双击打开设备（或者点击下面的Open打开设备）

状态栏会有相应的提示信息

与USB设备的通讯为64个字节

16x4 在对应的位置填写对应的【十六进制】对应的数字即可，比如要发送10，应填 0A

接收框会实时显示收到的数据，第一位为计数位，可以知道一共收到了几条数据

点击Clear可以清楚计数和接收的数据
