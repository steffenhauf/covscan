import asyncio
import zlib
from datetime import datetime
from subprocess import check_call

import base45
import cbor2
import cv2
import picamera
import picamera.array
from gpiozero import LED, Button, DistanceSensor, TonalBuzzer
from gpiozero.tones import Tone
from pyzbar import pyzbar

YELLOW_LED = 18
RED_LED = 15
GREEN_LED = 14

MAX_PASS_TIME = 10

yellow_led = LED(YELLOW_LED)
red_led = LED(RED_LED)
green_led = LED(GREEN_LED)

# distance sensor
ECHO_PIN = 27
TRIG_PIN = 17
FREE_DISTANCE = 100  # cm
sensor = DistanceSensor(echo=ECHO_PIN, trigger=TRIG_PIN)

# buzzer to go with it
BUZZER_PIN = 2
buzzer = TonalBuzzer(BUZZER_PIN)
tone = Tone("A4")

# button to shut down the PI
BUTTON_PIN = 3
shutdown_btn = Button(BUTTON_PIN, hold_time=2)


accept_time = datetime.now()
valid_pass = False
reset_on_free = False
yellow_led.on()

RESOLUTION = "1296x972"
loop = asyncio.get_event_loop()


def shutdown():
    print("Shutting down")
    check_call(['sudo', 'poweroff'])


shutdown_btn.when_held = shutdown


def get_codes(nparr):
    barcodes = pyzbar.decode(nparr, symbols=[pyzbar.ZBarSymbol.QRCODE])
    return barcodes


async def cam_loop():
    global reset_on_free, valid_pass, accept_time
    with picamera.PiCamera(resolution=RESOLUTION, framerate=5) as camera:
        camera.contrast = 100
        with picamera.array.PiRGBArray(camera) as output:
            for i, frame in enumerate(
                    camera.capture_continuous(output, 'rgb')):
                await asyncio.sleep(0)
                nparr = frame.array
                nparr = await loop.run_in_executor(None, cv2.cvtColor,
                                                   nparr, cv2.COLOR_BGR2GRAY)
                await asyncio.sleep(0)
                barcodes = await loop.run_in_executor(None, get_codes, nparr)
                for barcode in barcodes:
                    await asyncio.sleep(0)
# https://github.com/hannob/vacdec/blob/main/vacdec
                    cert = barcode.data.decode("utf-8")
                    b45data = cert.replace("HC1:", "")
                    zlibdata = base45.b45decode(b45data)
                    cbordata = zlib.decompress(zlibdata)
                    decoded = cbor2.loads(cbordata)
                    v = cbor2.loads(decoded.value[2])
                    # check that its not expired
                    expire = v[4]
                    if datetime.now().timestamp() > expire:
                        valid_pass = False
                    else:
                        try:
                            payload = v[-260][1]
                            vstat = payload["v"]
                            for entry in vstat:
                                valid_pass |= entry["dn"] == entry["sd"]
                            if valid_pass:
                                accept_time = datetime.now()
                        except Exception as e:
                            print(e)
                            valid_pass = False
                if valid_pass:
                    green_led.on()
                    red_led.off()
                else:
                    green_led.off()
                    red_led.on()
                dt = (datetime.now() - accept_time).total_seconds()
                if dt > MAX_PASS_TIME:
                    valid_pass = False
                output.truncate(0)
                await asyncio.sleep(0)


async def buzzer_loop():
    global reset_on_free, valid_pass
    while True:
        distance = sensor.distance * 100
        if distance < FREE_DISTANCE:
            if not valid_pass:
                red_led.on()
                green_led.off()
                buzzer.play(tone)
            else:
                reset_on_free = True
        elif reset_on_free:
            valid_pass = False
            reset_on_free = False
            red_led.on()
            green_led.off()
            buzzer.stop()
        else:
            buzzer.stop()
        await asyncio.sleep(0)


if __name__ == "__main__":
    loop.create_task(buzzer_loop())
    loop.run_until_complete(cam_loop())
