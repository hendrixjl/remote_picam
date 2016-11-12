import socket
import sys
import io
import struct
from PIL import Image
import datetime

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


host = sys.argv[1]
port = int(sys.argv[2])
message = sys.argv[3] + '\n'
socket = socket.socket()
socket.connect((host, port))
socket.send(message.encode())
pic = get_picture(socket)
t = datetime.datetime.now()
fname = "pi-{}-{}-{}-{}-{}-{}.jpg".format(t.year, t.month, t.day, t.hour, t.minute, t.second)
with open(fname, 'wb') as out:
    out.write(pic)
socket.close()
print("wrote {}".format(fname))


# brightness=0 contrast=0 sharpness=0 saturation=0 iso=0
# exposure_mode='auto' exposure_compensation=0
# flash_mode='off' awb_mode='auto' awb_gains='(43,32),(549, 256)'
# sensor_mode=0 image_denoise=True image_effect='none' meter_mode='average'
# rotation=0' resolution='(720, 480)' crop='(0.0, 0.0, 1.0, 1.0)' zoom='(0.0, 0.0, 1.0, 1.0)'
