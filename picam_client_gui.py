import sys
import io
from PIL import Image
import datetime
import tkinter
import ast
import picam_client

from tkinter import ttk

class MyIntCntrl(ttk.Frame):
    def __init__(self, parent, start_val, *args, **kwargs):
        ttk.Frame.__init__(self, parent, *args, **kwargs)
        big_frame = ttk.Frame(self, relief=tkinter.GROOVE, borderwidth=2)
        ttk.Label(big_frame, text="exp comp").pack()
        val_frame = ttk.Frame(big_frame)
        self.val = ttk.Label(val_frame, text="{}".format(start_val), width=3, relief=tkinter.SUNKEN, borderwidth=2)
        self.val.pack()
        val_frame.pack(side=tkinter.LEFT)
        cntrl_frame = ttk.Frame(big_frame)
        ttk.Button(cntrl_frame, text='+', width=3, command=self.increment).pack()
        ttk.Button(cntrl_frame, text='-', width=3, command=self.decrement).pack()
        cntrl_frame.pack()
        big_frame.pack()
        
    def increment(self):
        val = int(self.val["text"])
        val += 1
        self.val["text"] = "{}".format(val)
        
    def decrement(self):
        val = int(self.val["text"])
        val -= 1
        self.val["text"] = "{}".format(val)

    def get(self):
        return int(self.val["text"])

    def set(self, val):
        self.val["text"] = val

class MyApp(ttk.Frame):
    """The adders gui and functions."""
    def __init__(self, parent, host, port, *args, **kwargs):
        ttk.Frame.__init__(self, parent, *args, **kwargs)
        self.root = parent
        self.init_gui(host, port)
 
    def init_gui(self, host, port):
        """Builds GUI."""
        self.root.title('remote_picam')

        top_frame = ttk.Frame(self)
        ttk.Button(top_frame, text='Get Picture', command=self.get_picture).pack(pady=5)
        top_frame.pack(side=tkinter.TOP, fill=tkinter.BOTH)
        
        addr_frame = ttk.Frame(self)
        ttk.Label(addr_frame, text='host:').pack(side=tkinter.LEFT, padx=5, pady=5)
        self.host = ttk.Entry(addr_frame, width=12)
        self.host.insert(0, host)
        self.host.pack(side=tkinter.LEFT, padx=5, pady=5)
        ttk.Label(addr_frame, text='port:').pack(side=tkinter.LEFT, padx=5, pady=5)
        self.port = ttk.Entry(addr_frame, width=5)
        self.port.insert(0, port)
        self.port.pack(side=tkinter.LEFT, padx=5, pady=5)
        addr_frame.pack(side=tkinter.TOP, fill=tkinter.BOTH)

        exp_frame = ttk.Frame(self)
        ttk.Label(exp_frame, text='exposure_mode').pack(side='left', padx=5, pady=5)
        exp_mode_options = ['off', 'auto', 'night', 'nightpreview', 'backlight',
                            'spotlight', 'sports', 'snow', 'beach', 'verylong',
                            'fixedfps', 'antishake', 'fireworks' ]
        self.exposure_mode = tkinter.StringVar()
        self.exp_mode_opts = ttk.OptionMenu(exp_frame, self.exposure_mode, exp_mode_options[1], *exp_mode_options).pack(side='left')
        self.exposure_compensation = MyIntCntrl(exp_frame, 0)
        self.exposure_compensation.pack(side=tkinter.LEFT, padx=5, pady=5)
        exp_frame.pack(side=tkinter.TOP, fill=tkinter.BOTH)

        bottom_frame = ttk.Frame(self)
        ttk.Button(bottom_frame, text='Get Parameters', command=self.get_parameters).pack(pady=5)
        bottom_frame.pack(side=tkinter.TOP, fill=tkinter.BOTH)
        
        self.pack()
        

    def set_parameters(self, params):
        print("params={}".format(params))
        self.exposure_mode.set(params['exposure_mode'])
        self.exposure_compensation.set(params['exposure_compensation'])

    def get_picture(self):
        params = {}
        params['exposure_mode'] = self.exposure_mode.get()
        params['exposure_compensation'] = self.exposure_compensation.get()
        image_stream = picam_client.request_picture(params, self.host.get(), int(self.port.get()))
        image = Image.open(image_stream)
        print('Image is %dx%d' % image.size)
        image.verify()
        print('Image is verified')

    def get_parameters(self):
        params = picam_client.get_parameters(self.host.get(), int(self.port.get()))
        self.set_parameters(params)
        
        

root = tkinter.Tk()
MyApp(root, sys.argv[1], sys.argv[2])
root.mainloop()


# brightness=0 contrast=0 sharpness=0 saturation=0 iso=0
# exposure_mode='auto' exposure_compensation=0
# flash_mode='off' awb_mode='auto' awb_gains='(43,32),(549, 256)'
# sensor_mode=0 image_denoise=True image_effect='none' meter_mode='average'
# rotation=0' resolution='(720, 480)' crop='(0.0, 0.0, 1.0, 1.0)' zoom='(0.0, 0.0, 1.0, 1.0)'
