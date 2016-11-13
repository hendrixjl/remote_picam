import picamera
import datetime
import socket
import io
import struct

def make_int_tuple(data):
    fields = data.strip('(').rstrip(')').split(',')
    return int(fields[0]), int(fields[1])

def make_float_tuple(data):
    fields = data.strip('(').rstrip(')').split(',')
    floats = [float(i) for i in fields]
    return tuple(floats)
    
def set_params(params, camera):
    if 'awb_gains' in params:
        fields = params['awb_gains'].split(',')
        red = make_int_tuple(fields[0])
        blue = make_int_tuple(fields[1])
        camera.awb_gains = ( red, blue )
    if 'brightness' in params:
        camera.brightness = int(params['brightness'])
    if 'sharpness' in params:
        camera.sharpness = int(params['sharpness'])
    if 'contrast' in params:
        camera.contrast = int(params['contrast'])
    if 'saturation' in params:
        camera.saturation = int(params['saturation'])
    if 'iso' in params:
        camera.iso = int(params['iso'])
    if 'exposure_compensation' in params:
        camera.exposure_compensation = int(params['exposure_compensation'])
    if 'sensor_mode' in params:
        camera.sensor_mode = int(params['sensor_mode'])
    if 'rotation' in params:
        camera.rotation = int(params['rotation'])
    if 'exposure_mode' in params:
        camera.exposure_mode = params['exposure_mode']
    if 'flash_mode' in params:
        camera.flash_mode = params['flash_mode']
    if 'awb_mode' in params:
        camera.awb_mode = params['awb_mode']
    if 'image_effect' in params:
        camera.image_effect = params['image_effect']
    if 'meter_mode' in params:
        camera.meter_mode = params['meter_mode']
    if 'image_denoise' in params:
        camera.image_denoise = 'True' in params['image_denoise']
    if 'resolution' in params:
        print('resolution param = {}'.format(params['resolution']))
        camera.resolution = make_int_tuple(params['resolution'])
    if 'crop' in params:
        camera.crop = make_float_tuple(params['crop'])
    if 'zoom' in params:
        camera.zoom = make_float_tuple(params['zoom'])

def get_params(camera):
    params = {}
    params['awb_gains'] = camera.awb_gains
    params['brightness'] = camera.brightness
    params['sharpness'] = camera.sharpness
    params['contrast'] = camera.contrast
    params['saturation'] = camera.saturation
    params['iso'] = camera.iso
    params['exposure_compensation'] = camera.exposure_compensation
    params['sensor_mode'] = camera.sensor_mode
    params['rotation'] = camera.rotation
    params['exposure_mode'] = camera.exposure_mode
    params['flash_mode'] = camera.flash_mode
    params['awb_mode'] = camera.awb_mode
    params['image_effect'] = camera.image_effect
    params['meter_mode'] = camera.meter_mode
    params['image_denoise'] = camera.image_denoise
    params['resolution'] = camera.resolution
    params['crop'] = camera.crop
    params['zoom'] = camera.zoom
    return params

def set_defaults(camera):
    camera.resolution = (1600, 1200)

def get_line(connection):
    buff = ''
    while True:
        tbuff = connection.recv(1024).decode()
        buff += tbuff
        if '\n' in tbuff:
            return buff

def get_key_value(text):
    fields = text.split('=')
    k = fields[0]
    if len(fields) > 1:
        v = fields[1].strip("'").rstrip("'")
    else:
        v = None
    return k,v

def extract_params(line):
    fields = line.split()
    values = {}
    for f in fields:
        k,v = get_key_value(f)
        values[k] = v
    return values

def take_shot(camera):
    stream = io.BytesIO()
    camera.capture(stream, 'jpeg')
    stream.seek(0)
    return stream.read()

camera = picamera.PiCamera()
set_defaults(camera)

# Start a socket listening for connections on 0.0.0.0:8000 (0.0.0.0 means
# all interfaces)
server_socket = socket.socket()
server_socket.bind(('0.0.0.0', 8000))
server_socket.listen(0)
index = 0
print("Running")
try:
    while True:
        connection = server_socket.accept()[0]
        buff = get_line(connection)
        print(buff)
        params = extract_params(buff)
        set_params(params, camera)
        buffer = take_shot(camera)
        connection.sendall(struct.pack('<L', len(buffer)))
        connection.sendall(buffer)
        print("sent picture")
        connection.close()
finally:
    server_socket.close()
