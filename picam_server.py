import picamera
import datetime
import socket
import io
import struct
import ast

    
def set_params(params, camera):
##    if 'awb_gains' in params:
##        fields = params['awb_gains'].split(',')
##        red = make_int_tuple(fields[0])
##        blue = make_int_tuple(fields[1])
##        camera.awb_gains = ( red, blue )
    if 'brightness' in params:
        camera.brightness = params['brightness']
    if 'sharpness' in params:
        camera.sharpness = params['sharpness']
    if 'contrast' in params:
        camera.contrast = params['contrast']
    if 'saturation' in params:
        camera.saturation = params['saturation']
    if 'iso' in params:
        camera.iso = params['iso']
    if 'exposure_compensation' in params:
        camera.exposure_compensation = params['exposure_compensation']
    if 'sensor_mode' in params:
        camera.sensor_mode = params['sensor_mode']
    if 'rotation' in params:
        camera.rotation = params['rotation']
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
        camera.image_denoise = params['image_denoise']
    if 'resolution' in params:
        camera.resolution = params['resolution']
    if 'crop' in params:
        camera.crop = params['crop']
    if 'zoom' in params:
        camera.zoom = params['zoom']

def get_params(camera):
    params = {}
#    params['awb_gains'] = camera.awb_gains
    params['brightness'] = camera.brightness
    params['sharpness'] = camera.sharpness
    params['contrast'] = camera.contrast
    params['saturation'] = camera.saturation
    params['iso'] = int(camera.iso)
    params['exposure_compensation'] = camera.exposure_compensation
    params['sensor_mode'] = int(camera.sensor_mode)
    params['rotation'] = camera.rotation
    params['exposure_mode'] = camera.exposure_mode
    params['flash_mode'] = camera.flash_mode
    params['awb_mode'] = camera.awb_mode
    params['image_effect'] = camera.image_effect
    params['meter_mode'] = camera.meter_mode
    params['image_denoise'] = camera.image_denoise
    res = str(camera.resolution).split('x')
    x = int(res[0])
    y = int(res[1])
    params['resolution'] = (x, y)
    params['crop'] = camera.crop
    params['zoom'] = camera.zoom
    return params

def get_defaults():
    params = {}
    params['image_denoise'] = (1600, 1200)
    return params

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
    return ast.literal_eval(line)

def take_shot(camera):
    stream = io.BytesIO()
    camera.capture(stream, 'jpeg')
    stream.seek(0)
    return stream.read()

def save_settings(params):
    with open("settings.txt", 'w') as outfile:
        outfile.write("{}".format(params))

def load_settings():
    try:
        with open("settings.txt", 'r') as infile:
            line = infile.read()
            params = extract_params(line)
    except IOError:
        params = get_defaults()
    return params

def identify_camera(camera):
    try:
        camera.width = (3280, 2464)
    except IOError:
        camera.width = (2592, 1944)
        return 1
    return 2

def main():
    params = load_settings()
    camera = picamera.PiCamera()
    set_params(params, camera)

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
            if '@' in buff:
                params = get_params(camera)
                print(params)
                connection.sendall("{}\n".format(params))
                connection.close()
            elif '!' in buff:
                params = extract_params(buff[1:])
                set_params(params, camera)
                params = get_params(camera)
                print(params)
                connection.sendall("{}\n".format(params))
                connection.close()
                save_settings(params)
            else:
                params = extract_params(buff)
                set_params(params, camera)
                buffer = take_shot(camera)
                connection.sendall(struct.pack('<L', len(buffer)))
                connection.sendall(buffer)
                print("sent picture")
                connection.close()
    finally:
        server_socket.close()

if __name__ == "__main__":
    main()
    
