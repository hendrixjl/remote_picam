import socket
import sys
import io
import struct
from PIL import Image
import datetime
import tkinter

from tkinter import ttk

def get_line(connection):
    buff = ''
    while True:
        tbuff = connection.recv(1024).decode()
        buff += tbuff
        if '\n' in tbuff:
            return buff

        
def get_picture(socket):
    connection = socket.makefile('rb')
    # Read the length of the image as a 32-bit unsigned int. If the
    # length is zero, quit the loop
    image_len = struct.unpack('<L', connection.read(struct.calcsize('<L')))[0]
    if not image_len:
        return
    # Construct a stream to hold the image data and read the image
    # data from the connection
    image_stream = io.BytesIO()
    image_stream.write(connection.read(image_len))
    # Rewind the stream, open it as an image with PIL and do some
    # processing on it
    image_stream.seek(0)
    image = Image.open(image_stream)
    print('Image is %dx%d' % image.size)
    image.verify()
    print('Image is verified')
    image_stream.seek(0)
    return image_stream.read()

class MyApp(ttk.Frame):
    """The adders gui and functions."""
    def __init__(self, parent, host, port, *args, **kwargs):
        ttk.Frame.__init__(self, parent, *args, **kwargs)
        self.root = parent
        self.init_gui(host, port)
 
    def init_gui(self, host, port):
        """Builds GUI."""
        self.root.title('remote_picam')
        self.pack()

        top_frame = ttk.Frame(self).pack(side=tkinter.TOP, fill=tkinter.BOTH)
        ttk.Button(top_frame, text='Get Picture', command=self.get_picture).pack(pady=5)
        
        addr_frame = ttk.Frame(self).pack(side=tkinter.TOP, fill=tkinter.BOTH)
        ttk.Label(addr_frame, text='host:').pack(side=tkinter.LEFT, padx=5, pady=5)
        self.host = ttk.Entry(addr_frame, width=12)
        self.host.insert(0, host)
        self.host.pack(side=tkinter.LEFT, padx=5, pady=5)
        ttk.Label(addr_frame, text='port:').pack(side=tkinter.LEFT, padx=5, pady=5)
        self.port = ttk.Entry(addr_frame, width=5)
        self.port.insert(0, port)
        self.port.pack(side=tkinter.LEFT, padx=5, pady=5)

        exp_frame = ttk.Frame(self).pack(side=tkinter.TOP, fill=tkinter.BOTH)
        ttk.Label(exp_frame, text='exposure_mode').pack()
        exp_mode_options = ['off', 'auto', 'night', 'nightpreview', 'backlight',
                            'spotlight', 'sports', 'snow', 'beach', 'verylong',
                            'fixedfps', 'antishake', 'fireworks' ]
        self.exposure_mode = tkinter.StringVar()
        ttk.OptionMenu(exp_frame, self.exposure_mode, exp_mode_options[1], *exp_mode_options).pack(side='left', padx=5, pady=5)

        bottom_frame = ttk.Frame(self).pack(side=tkinter.TOP, fill=tkinter.BOTH)
        ttk.Button(top_frame, text='Get Parameters', command=self.get_parameters).pack(pady=5)
        

    def get_picture(self):
        message = "exposure_mode='{}'\n".format(self.exposure_mode.get())
        mysocket = socket.socket()
        mysocket.connect((self.host.get(), int(self.port.get())))
        mysocket.send(message.encode())
        pic = get_picture(mysocket)
        t = datetime.datetime.now()
        fname = "pi-{}-{}-{}-{}-{}-{}.jpg".format(t.year, t.month, t.day, t.hour, t.minute, t.second)
        with open(fname, 'wb') as out:
            out.write(pic)
        mysocket.close()
        print("wrote {}".format(fname))

    def get_parameters(self):
        message = "@\n"
        mysocket = socket.socket()
        mysocket.connect((self.host.get(), int(self.port.get())))
        mysocket.send(message.encode())
        print(get_line(mysocket))
        mysocket.close()

root = tkinter.Tk()
MyApp(root, sys.argv[1], sys.argv[2])
root.mainloop()


# brightness=0 contrast=0 sharpness=0 saturation=0 iso=0
# exposure_mode='auto' exposure_compensation=0
# flash_mode='off' awb_mode='auto' awb_gains='(43,32),(549, 256)'
# sensor_mode=0 image_denoise=True image_effect='none' meter_mode='average'
# rotation=0' resolution='(720, 480)' crop='(0.0, 0.0, 1.0, 1.0)' zoom='(0.0, 0.0, 1.0, 1.0)'
