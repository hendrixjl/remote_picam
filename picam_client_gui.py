import sys
import io
from PIL import Image, ImageTk
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
        val = int(self.val["text"])
        if (val < self.max_val):
            val += 1
            self.val["text"] = "{}".format(val)
        
    def decrement(self):
        val = int(self.val["text"])
        if (val > self.min_val):
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

class My4TupleCntrl(ttk.Frame):
    def __init__(self, parent, name, x1, y1, x2, y2, *args, **kwargs):
        ttk.Frame.__init__(self, parent, *args, **kwargs)
        big_frame = ttk.Frame(self, relief=tkinter.GROOVE, borderwidth=2)
        ttk.Label(big_frame, text="{}:x1".format(name)).pack(side=tkinter.LEFT)
        self.x1 = ttk.Entry(big_frame, width=5)
        self.x1.insert(0, str(x1))
        self.x1.pack(side=tkinter.LEFT, padx=5, pady=5)
        ttk.Label(big_frame, text="y1:").pack(side=tkinter.LEFT)
        self.y1 = ttk.Entry(big_frame, width=5)
        self.y1.insert(0, str(y1))
        self.y1.pack(side=tkinter.LEFT, padx=5, pady=5)
        ttk.Label(big_frame, text="x2".format(name)).pack(side=tkinter.LEFT)
        self.x2 = ttk.Entry(big_frame, width=5)
        self.x2.insert(0, str(x2))
        self.x2.pack(side=tkinter.LEFT, padx=5, pady=5)
        ttk.Label(big_frame, text="y2:").pack(side=tkinter.LEFT)
        self.y2 = ttk.Entry(big_frame, width=5)
        self.y2.insert(0, str(y2))
        self.y2.pack(side=tkinter.LEFT, padx=5, pady=5)
        big_frame.pack()
        
    def get_val(self):
        return float(self.x1.get()), float(self.y1.get()), float(self.x2.get()), float(self.y2.get())

    def set_val(self, res):
        fmt = "{:5.3f}"
        self.x1.delete(0, tkinter.END)
        self.x1.insert(0, fmt.format(res[0]))
        self.y1.delete(0, tkinter.END)
        self.y1.insert(0, fmt.format(res[1]))
        self.x2.delete(0, tkinter.END)
        self.x2.insert(0, fmt.format(res[2]))
        self.y2.delete(0, tkinter.END)
        self.y2.insert(0, fmt.format(res[3]))

class MyOptionCntrl(ttk.Frame):
    def __init__(self, parent, name, first, options, handler, *args, **kwargs):
        self.name = name
        ttk.Frame.__init__(self, parent, *args, **kwargs)
        big_frame = ttk.Frame(self, relief=tkinter.GROOVE, borderwidth=2)
        ttk.Label(big_frame, text=self.name).pack(side='left', padx=5, pady=5)
        self.var = tkinter.StringVar()
        max_chars = 0
        for o in options:
            if len(o) > max_chars:
                max_chars = len(o)
        
        self.opts = ttk.OptionMenu(big_frame, self.var, first, *options)
        self.opts.config(width=max_chars)
        self.opts.pack(side='left')
        big_frame.pack()
##        self.observer = self.var.trace('w', self.callback()) #handler.callback(self.name, self.var.get()))

    def get_val(self):
        return self.var.get()

    def set_val(self, val):
        print("MyOptionCntrl.set_val(). name={} val={}".format(self.name, val))
##        self.var.trace_vdelete('w', self.observer)
        self.var.set(val)
##        self.observer = self.var.trace('w', self.callback()) #handler.callback(self.name, self.var.get()))

##    def callback(self):
##        print("MyOptionCtrl.callback")

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
        self.service_callback = True
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
        choices_frame = ttk.Frame(exp_frame)
        exp_mode_options = ['off', 'auto', 'night', 'nightpreview', 'backlight',
                            'spotlight', 'sports', 'snow', 'beach', 'verylong',
                            'fixedfps', 'antishake', 'fireworks' ]
        self.exposure_mode = MyOptionCntrl(choices_frame, "exposure_mode", exp_mode_options[1], exp_mode_options, self)
        self.exposure_mode.pack(side=tkinter.TOP, fill=tkinter.X)
        awb_mode_options = ['off', 'auto', 'sunlight', 'cloudy', 'shade',
                            'tungsten', 'florescent', 'incandescent', 'flash', 'horizon']
        self.awb_mode = MyOptionCntrl(choices_frame, "awb_mode", awb_mode_options[1], awb_mode_options, self)
        self.awb_mode.pack(side=tkinter.TOP, fill=tkinter.X)
        choices_frame.pack(side=tkinter.LEFT)
        self.exposure_compensation = MyIntCntrl(exp_frame, "exp comp", 0, -25, 25)
        self.exposure_compensation.pack(side=tkinter.LEFT, padx=5, pady=5)
        exp_frame.pack(side=tkinter.TOP, fill=tkinter.BOTH)


        self.res_cntrl = MyResCntrl(self, 1600, 1200)
        self.res_cntrl.pack(side=tkinter.TOP)
        self.zoom_cntrl = My4TupleCntrl(self, "zoom", 0.0, 0.0, 1.0, 1.0)
        self.zoom_cntrl.pack(side=tkinter.TOP)

        bottom_frame = ttk.Frame(self)
        ttk.Button(bottom_frame, text='Get Parameters', command=self.fetch_parameters).pack(pady=5)
        ttk.Button(bottom_frame, text='Set Parameters', command=self.send_parameters).pack(pady=5)
        bottom_frame.pack(side=tkinter.TOP, fill=tkinter.BOTH)

        #self.photolabel = tkinter.Label(self)
        #self.photolabel.pack(side=tkinter.TOP)
        
        self.pack()
        self.fetch_parameters()
        self.service_callback = True
        

    def set_parameters(self, params):
        print("set_parameters. params={}".format(params))
        self.awb_mode.set_val(params['awb_mode'])
        self.exposure_mode.set_val(params['exposure_mode'])
        self.exposure_compensation.set(params['exposure_compensation'])
        self.res_cntrl.set_val(params['resolution'])
        self.zoom_cntrl.set_val(params['zoom'])

    def get_parameters(self):
        params = {}
        params['awb_mode'] = self.awb_mode.get_val()
        params['exposure_mode'] = self.exposure_mode.get_val()
        params['exposure_compensation'] = self.exposure_compensation.get()
        params['resolution'] = self.res_cntrl.get_val()
        params['zoom'] = self.zoom_cntrl.get_val()
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
#        self.photo = ImageTk.PhotoImage(image)
        #self.photolabel = tkinter.Label(self, image=photo)
        #self.photolabel.pack(side=tkinter.TOP)

    def fetch_parameters(self):
        params = picam_client.get_parameters(self.host.get(), int(self.port.get()))
        self.set_parameters(params)

    def callback(self, name, data):
        if self.service_callback:
            prm = {}
            prm[name] = data
            print("callback. prm={}".format(prm))
        
 #       new_params = picam_client.set_parameters(prm, self.host.get(), int(self.port.get()))
 #       self.set_parameters(new_params)
        

root = tkinter.Tk()
MyApp(root, sys.argv[1], sys.argv[2])
root.mainloop()


# brightness=0 contrast=0 sharpness=0 saturation=0 iso=0
# exposure_mode='auto' exposure_compensation=0
# flash_mode='off' awb_mode='auto' awb_gains='(43,32),(549, 256)'
# sensor_mode=0 image_denoise=True image_effect='none' meter_mode='average'
# rotation=0' resolution='(720, 480)' zoom='(0.0, 0.0, 1.0, 1.0)' zoom='(0.0, 0.0, 1.0, 1.0)'
