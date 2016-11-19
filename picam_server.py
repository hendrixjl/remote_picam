import picamera
import datetime
import socket
import io
import struct
import ast

    
def set_params(aparams, acamera):
##    if 'awb_gains' in aparams:
##        fields = aparams['awb_gains'].split(',')
##        red = make_int_tuple(fields[0])
##        blue = make_int_tuple(fields[1])
##        acamera.awb_gains = ( red, blue )
    if 'brightness' in aparams:
        acamera.brightness = aparams['brightness']
    if 'sharpness' in params:
        acamera.sharpness = aparams['sharpness']
    if 'contrast' in aparams:
        acamera.contrast = aparams['contrast']
    if 'saturation' in aparams:
        acamera.saturation = aparams['saturation']
    if 'iso' in aparams:
        acamera.iso = aparams['iso']
    if 'exposure_compensation' in aparams:
        acamera.exposure_compensation = aparams['exposure_compensation']
    if 'sensor_mode' in aparams:
        acamera.sensor_mode = aparams['sensor_mode']
    if 'rotation' in aparams:
        acamera.rotation = aparams['rotation']
    if 'exposure_mode' in aparams:
        acamera.exposure_mode = aparams['exposure_mode']
    if 'flash_mode' in aparams:
        acamera.flash_mode = aparams['flash_mode']
    if 'awb_mode' in aparams:
        acamera.awb_mode = aparams['awb_mode']
    if 'image_effect' in aparams:
        acamera.image_effect = aparams['image_effect']
    if 'meter_mode' in aparams:
        acamera.meter_mode = aparams['meter_mode']
    if 'image_denoise' in aparams:
        acamera.image_denoise = aparams['image_denoise']
    if 'resolution' in aparams:
        acamera.resolution = aparams['resolution']
    if 'crop' in aparams:
        acamera.crop = aparams['crop']
    if 'zoom' in aparams:
        acamera.zoom = aparams['zoom']

def get_params(acamera):
    p = {}
#    p['awb_gains'] = acamera.awb_gains
    p['brightness'] = acamera.brightness
    p['sharpness'] = acamera.sharpness
    p['contrast'] = acamera.contrast
    p['saturation'] = acamera.saturation
    p['iso'] = int(acamera.iso)
    p['exposure_compensation'] = acamera.exposure_compensation
    p['sensor_mode'] = int(acamera.sensor_mode)
    p['rotation'] = acamera.rotation
    p['exposure_mode'] = acamera.exposure_mode
    p['flash_mode'] = acamera.flash_mode
    p['awb_mode'] = acamera.awb_mode
    p['image_effect'] = acamera.image_effect
    p['meter_mode'] = acamera.meter_mode
    p['image_denoise'] = acamera.image_denoise
    res = str(acamera.resolution).split('x')
    x = int(res[0])
    y = int(res[1])
    p['resolution'] = (x, y)
    p['crop'] = acamera.crop
    p['zoom'] = acamera.zoom
    return p

def get_line(conn):
    buff = ''
    while True:
        tbuff = conn.recv(1024).decode()
        buff += tbuff
        if '\n' in tbuff:
            return buff

def get_key_value(t):
    fields = t.split('=')
    k = fields[0]
    if len(fields) > 1:
        v = fields[1].strip("'").rstrip("'")
    else:
        v = None
    return k,v

def extract_params(l):
    return ast.literal_eval(l)

def take_shot(acamera):
    stream = io.BytesIO()
    acamera.capture(stream, 'jpeg')
    stream.seek(0)
    return stream.read()

def save_settings(p):
    with open("settings.txt", 'w') as outfile:
        outfile.write("{}".format(p))

def load_settings(acamera):
    identify_camera(acamera)
    try:
        with open("settings.txt", 'r') as infile:
            line = infile.read()
            p = extract_params(line)
    except IOError:
        p = get_params(acamera)
    return p

def identify_camera(acamera):
    try:
        acamera.resolution = (3280, 2464)
    except picamera.exc.PiCameraValueError:
        acamera.resolution = (2592, 1944)
        return 1
    return 2

def main():
    camera = picamera.PiCamera()
    params = load_settings(camera)
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
    
