import sys
import io
from PIL import Image
import datetime
import tkinter
import ast
import picam_client

from tkinter import ttk

class MyIntCntrl(ttk.Frame):
    def __init__(self, parent, name, start_val, min_val, max_val, *args, **kwargs):
        ttk.Frame.__init__(self, parent, *args, **kwargs)
        self.min_val = min_val
        self.max_val = max_val
        big_frame = ttk.Frame(self, relief=tkinter.GROOVE, borderwidth=2)
        ttk.Label(big_frame, text=name).pack()
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
        if (f < self.max_val):
            val = int(self.val["text"])
            val += 1
            self.val["text"] = "{}".format(val)
        
    def decrement(self):
        if (f > self.min_val):
            val = int(self.val["text"])
            val -= 1
            self.val["text"] = "{}".format(val)

    def get(self):
        return int(self.val["text"])

    def set(self, val):
        self.val["text"] = val


class MyResCntrl(ttk.Frame):
    def __init__(self, parent, x, y, *args, **kwargs):
        ttk.Frame.__init__(self, parent, *args, **kwargs)
        big_frame = ttk.Frame(self, relief=tkinter.GROOVE, borderwidth=2)
        ttk.Label(big_frame, text="resolution x:").pack(side=tkinter.LEFT)
        self.x = ttk.Entry(big_frame, width=4)
        self.x.insert(0, str(x))
        self.x.pack(side=tkinter.LEFT, padx=5, pady=5)
        ttk.Label(big_frame, text="y:").pack(side=tkinter.LEFT)
        self.y = ttk.Entry(big_frame, width=4)
        self.y.insert(0, str(y))
        self.y.pack(side=tkinter.LEFT, padx=5, pady=5)
        big_frame.pack()
        
    def get_val(self):
        return int(self.x.get()), int(self.y.get())

    def set_val(self, res):
        self.x.delete(0, tkinter.END)
        self.x.insert(0, str(res[0]))
        self.y.delete(0, tkinter.END)
        self.y.insert(0, str(res[1]))

class MyOptionCntrl(ttk.Frame):
    def __init__(self, parent, name, first, options, *args, **kwargs):
        ttk.Frame.__init__(self, parent, *args, **kwargs)
        big_frame = ttk.Frame(self, relief=tkinter.GROOVE, borderwidth=2)
        ttk.Label(big_frame, text=name).pack(side='left', padx=5, pady=5)
        self.var = tkinter.StringVar()
        max_chars = 0
        for o in options:
            if len(o) > max_chars:
                max_chars = len(o)
        
        self.opts = ttk.OptionMenu(big_frame, self.var, first, *options)
        self.opts.config(width=max_chars)
        self.opts.pack(side='left')
        big_frame.pack()

    def get_val(self):
        return self.var.get()

    def set_val(self, val):
        self.var.set(val)

class MyApp(ttk.Frame):
    """The adders gui and functions."""
    def __init__(self, parent, host, port, *args, **kwargs):
        ttk.Frame.__init__(self, parent, *args, **kwargs)
        self.root = parent
        self.init_gui(host, port)
        
    def validate_port(self, P):
        if not P:
            return False
        try:
            f = int(P)
            return (f > 0) and (f <= 65535)
        except ValueError:
            return False
        

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
        self.port = ttk.Entry(addr_frame, width=5, validatecommand=(self.register(self.validate_port), '%P'))
        self.port.insert(0, port)
        self.port.pack(side=tkinter.LEFT, padx=5, pady=5)
        addr_frame.pack(side=tkinter.TOP, fill=tkinter.BOTH)

        exp_frame = ttk.Frame(self)
        exp_mode_options = ['off', 'auto', 'night', 'nightpreview', 'backlight',
                            'spotlight', 'sports', 'snow', 'beach', 'verylong',
                            'fixedfps', 'antishake', 'fireworks' ]
        self.exposure_mode = MyOptionCntrl(exp_frame, "exposure_mode", exp_mode_options[1], exp_mode_options)
        self.exposure_mode.pack(side=tkinter.LEFT, padx=5, pady=5)
        self.exposure_compensation = MyIntCntrl(exp_frame, "exp comp", 0, -25, 25)
        self.exposure_compensation.pack(side=tkinter.LEFT, padx=5, pady=5)
        exp_frame.pack(side=tkinter.TOP, fill=tkinter.BOTH)

        self.res_cntrl = MyResCntrl(self, 1600, 1200)
        self.res_cntrl.pack(side=tkinter.TOP)

        bottom_frame = ttk.Frame(self)
        ttk.Button(bottom_frame, text='Get Parameters', command=self.fetch_parameters).pack(pady=5)
        ttk.Button(bottom_frame, text='Set Parameters', command=self.send_parameters).pack(pady=5)
        bottom_frame.pack(side=tkinter.TOP, fill=tkinter.BOTH)
        
        self.pack()
        

    def set_parameters(self, params):
        print("params={}".format(params))
        self.exposure_mode.set_val(params['exposure_mode'])
        self.exposure_compensation.set(params['exposure_compensation'])
        self.res_cntrl.set_val(params['resolution'])

    def get_parameters(self):
        params = {}
        params['exposure_mode'] = self.exposure_mode.get_val()
        params['exposure_compensation'] = self.exposure_compensation.get()
        params['resolution'] = self.res_cntrl.get_val()
        return params

    def send_parameters(self):
        params = self.get_parameters()
        new_params = picam_client.set_parameters(params, self.host.get(), int(self.port.get()))
        print("{}".format(new_params))

    def get_picture(self):
        params = self.get_parameters()
        image_stream = picam_client.request_picture(params, self.host.get(), int(self.port.get()))
        image = Image.open(image_stream)
        print('Image is %dx%d' % image.size)
        image.verify()
        print('Image is verified')

    def fetch_parameters(self):
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
