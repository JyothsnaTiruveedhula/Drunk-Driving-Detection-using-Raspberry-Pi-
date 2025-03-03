import RPi.GPIO as GPIO
import time

# Set up GPIO pins
GPIO.setmode(GPIO.BOARD)
GPIO.setup(7, GPIO.OUT)
GPIO.setup(11, GPIO.OUT)
GPIO.setup(13, GPIO.OUT)
GPIO.setup(15, GPIO.OUT)

# Set up alcohol sensor
ALC_PIN = 21
GPIO.setup(ALC_PIN, GPIO.IN)

# Main loop
while True:
    if GPIO.input(ALC_PIN) == GPIO.HIGH:
        # If alcohol is detected, turn on the robot
        GPIO.output(7, GPIO.HIGH)
        GPIO.output(11, GPIO.LOW)
        GPIO.output(13, GPIO.LOW)
        GPIO.output(15, GPIO.HIGH)
        time.sleep(2)
    else:
        # If no alcohol is detected, turn off the robot
        GPIO.output(7, GPIO.LOW)
        GPIO.output(11, GPIO.LOW)
        GPIO.output(13, GPIO.LOW)
        GPIO.output(15, GPIO.LOW)
        time.sleep(2)

# Clean up GPIO pins
GPIO.cleanup()
import Adafruit_CharLCD as LCD
import RPi.GPIO as GPIO
import time
from datetime import datetime
import os
import serial
import re
##from smbus import SMBus
##bus = SMBus(1)
port = serial.Serial("/dev/ttyAMA0", baudrate=9600, timeout=0.5)
ok = "OK"
admin_num = ""
DMV_num = ""
number = ""
rcv = None
admin_config = False
DMV_config = False
##def get_alcohol_level():
## reading = bus.read_byte_data(0x48,0x00)
## reading2 = float(reading * 0.43)
## print "analog reading = ", str(reading) , str(reading2) , '%'
## return reading2
##
def send_cmd(cmd,response=None,t=0.5):
port = serial.Serial("/dev/ttyAMA0", baudrate=9600, timeout=t)
cmd = cmd + "\r\n"
port.write(cmd)
rcv = port.readall().strip()
print "rcv = ", rcv
if response:
print rcv.endswith(response)
return rcv.endswith(response)
else:
return rcv
def send_sms(text,num):
lcd.clear()
lcd.message('Sending sms to\n'+num)
print "sending sms to ",num
send_cmd("AT+CMGF=1",ok)
if send_cmd("AT+CMGS=\""+num+'\"','>'):
if send_cmd(text+"\x1a",ok,5):
print "sms sent"
lcd.clear()
lcd.message('SMS sent')
time.sleep(1)
else:
print "cant send sms....check your balance"
def get_data():
rcv = ""
print "data available"
rcv = port.readall().strip()
print "rcv=" , rcv
check_data(rcv)
port.flushInput()
def check_data(data):
global admin_num
global admin_config
global DMV_num
global DMVf_config
if data.find("+CLIP") > 0:
index1 = data.find('\"') + 1
index2 = data.find(',') - 1
number = data[index1:index2]
print "receiving call from ",number
lcd.clear()
lcd.message('receiving call\n'+number)
if not admin_config:
admin_num = number
admin_config = True
print "admin number saved..",admin_num
time.sleep(1)
send_cmd("ATH",ok)
print "call cut"
send_sms("This number is configure as ADMIN..",admin_num)
elif not DMV_config and number != admin_num:
DMV_num = number
DMV_config = True
print "DMV number saved..",DMV_num
time.sleep(1)
send_cmd("ATH",ok)
print "call cut"
send_sms("This number is configure as DMV..",DMV_num)
elif admin_config and DMV_config:
print "configuration already done"
time.sleep(1)
send_cmd("ATH",ok)
print "call cut"
else:
lcd.clear()
lcd.message('Nummber already\nexist')
print "%s already configure.."%admin_num
time.sleep(1)
send_cmd("ATH",ok)
print "call cut"
if data.find("+CMT") > 0:
index1 = data.find('\"') + 1
index2 = data.find(',') - 1
sms_number = data[index1:index2]
index3 = data.rfind('"') + 1
sms = data[index3:]
print "number: ",sms_number
print "sms: ", sms
def gps_track():
lcd.clear()
lcd.message('Tracking')
time.sleep(2)
gps_data = send_cmd("AT+CGPSINF=2")
print "gps_data =", gps_data
if gps_data.find("+CGPSINF:") >= 0:
index1 = gps_data.find(',N')
_lat = gps_data[0:index1]
print _lat
index2 = _lat.rfind(',') +1
_lat = str(_lat[index2 : ])
index1 = gps_data.find(',E')
_lon = gps_data[0:index1]
print _lat
index2 = _lon.rfind(',') +1
_lon = str(_lon[index2 : ])
print "lat = " , float(_lat)
print "lon = " , float(_lon)
return _lat,_lon
##os.system("tvservice -o")
restart = 23
led = 8
button = 25
##gas = 23
buzzer = 7
motor1 = 6
motor2 = 13
# Raspberry Pi pin configuration:
##lcd_rs = 26 # Note this might need to be changed to 21 for older revision Pi's.
##lcd_en = 19
##lcd_d4 = 21
##lcd_d5 = 20
##lcd_d6 = 16
##lcd_d7 = 12
lcd_rs = 26 # Note this might need to be changed to 21 for older revision Pi's.
lcd_en = 19
lcd_d4 = 21
lcd_d5 = 20
lcd_d6 = 16
lcd_d7 = 12
##lcd_backlight = 8
# Define LCD column and row size for 16x2 LCD.
lcd_columns = 16
lcd_rows = 2
lcd = LCD.Adafruit_CharLCD(lcd_rs, lcd_en, lcd_d4, lcd_d5, lcd_d6, lcd_d7,
lcd_columns, lcd_rows)
GPIO.setup(restart,GPIO.IN)
GPIO.setup(button,GPIO.IN, pull_up_down=GPIO.PUD_DOWN)
##GPIO.setup(gas,GPIO.IN, pull_up_down=GPIO.PUD_UP)
GPIO.setup(led,GPIO.OUT)
GPIO.setup(buzzer,GPIO.OUT)
GPIO.setup(motor1,GPIO.OUT)
GPIO.setup(motor2,GPIO.OUT)
reset = True
while reset == True:
## alcohol = get_alcohol_level()
sms_sent = False
ok = "OK"
admin_num = ""
DMV_num = ""
number = ""
rcv = None
admin_config = False
DMV_config = False
p = GPIO.PWM(motor1,50)
p.start(0)
GPIO.output(led, False)
GPIO.output(buzzer, False)
GPIO.output(motor2, False)
main = True
lcd.clear()
lcd.show_cursor(False)
print "Alcohol detection system"
lcd.message(' Alcohol ')
lcd.set_cursor(0,1)
lcd.message('Detection system')
time.sleep(4)
## t1 = datetime.now()
## while GPIO.input(restart) == False:
## t2 = datetime.now()
## delta = t2 - t1
## time_elapse = delta.total_seconds()
## if time_elapse > 10:
## reset = False
## main = False
## break
if main:
print "connecting GSM"
lcd.clear()
lcd.message('connecting GSM')
time.sleep(5)
while True:
if send_cmd("AT",ok):
send_cmd("ATE0",ok)
send_cmd("AT+CNMI=2,2,0,0",ok)
send_cmd("AT+CGPSPWR=1",ok
send_cmd("AT+CLIP=1",ok)
print "GSM connected"
lcd.clear()
lcd.message('GSM connected')
time.sleep(1)
break
else:
print "GSM not connected"
lcd.clear()
lcd.message('GSM not \nconnected')
main = False
time.sleep(3)
lcd.clear()
lcd.message('connect GSM and\nrestart system')
while GPIO.input(restart) == True:
None
break
port.flushInput()
port.flushOutput()
if main:
print "Waiting for admin"
while not admin_config:
lcd.clear()
lcd.message('Waiting for\nADMIN')
time.sleep(0.5)
if port.inWaiting() > 0:
get_data()
lcd.clear()
lcd.message('ADMIN number is\ncofigured')
time.sleep(2)
print "Waiting for DMV"
while not DMV_config:
lcd.clear()
lcd.message('Waiting for\nDMV')
time.sleep(0.5)
if port.inWaiting() > 0:
get_data()
lcd.clear()
lcd.message('DMV number is\ncofigured')
time.sleep(2)
lcd.clear()
lcd.message('Press switch...')
print "press switch"
full_on = False
half_on = False
while main == True:
sm = 1
if not GPIO.input(button):
lcd.clear()
lcd.message('Please Wait....')
print "Please Wait...."
time.sleep(1)
while True:
alcohol = get_alcohol_level()
time.sleep(1)
lcd.clear()
lcd.message('Alcohol : ')
lcd.message(str(alcohol) + '% ')
if alcohol < 50 and alcohol > 20:
sms_sent = False
print "Alcohol Level Under Limit"
lcd.set_cursor(0,1)
lcd.message('Engin speed 50% ')
GPIO.output(motor2, False)
if full_on == True:
print "Engin Stop"
for dc in range(100,50,-5):
p.ChangeDutyCycle(dc)
time.sleep(0.1)
elif half_on == False:
print "Engin Running"
for dc in range(0,50,5):
p.ChangeDutyCycle(dc)
time.sleep(0.1)
half_on = True
full_on = False
GPIO.output(led, False)
GPIO.output(buzzer, False)
if alcohol < 20:
sms_sent = False
print "Alcohol Level Under Limit"
lcd.set_cursor(0,1)
lcd.message('Engin speed 100%')
GPIO.output(motor2, False)
if half_on == True:
print "Engin Running"
for dc in range(55,100,5):
p.ChangeDutyCycle(dc)
time.sleep(0.1)
half_on = False
full_on = True
elif full_on == False:
print "Engin Running"
for dc in range(0,100,5):
p.ChangeDutyCycle(dc)
time.sleep(0.1)
half_on = False
full_on = True
GPIO.output(led, False)
GPIO.output(buzzer, False)
if alcohol > 50:
lcd.set_cursor(0,1)
lcd.message(' Engin stop ')
print "Alcohol Level Over Limit"
GPIO.output(led, True)
GPIO.output(buzzer, True)
GPIO.output(motor2, False)
if half_on == True:
print "Engin Stop"
for dc in range(50,-1,-5):
p.ChangeDutyCycle(dc)
time.sleep(0.1)
full_on = False
half_on = False
elif full_on == True:
print "Engin Stop"
for dc in range(100,-1,-5):
p.ChangeDutyCycle(dc)
time.sleep(0.1)
full_on = False
half_on = False
time.sleep(2)
GPIO.output(led, False)
GPIO.output(buzzer, False)
if sms_sent == False:
port.flushInput()
port.flushOutput()
lat,lon = gps_track()
if lat > 0 and lon > 0:
lcd.clear()
lcd.message('lat: ' + str(lat))
lcd.set_cursor(0,1)
lcd.message('lon: ' + str(lon))
time.sleep(1.5)
map_site = "Alcohol Detected!!\n" + "http://maps.google.com/maps?f=q&q=" + str(lat) + "," + 
str(lon) + "&z=16"
print map_site
send_sms(map_site,admin_num)
send_sms(map_site,DMV_num)
sms_sent = True
else:
lcd.clear()
lcd.message("gps not working")
time.sleep(1.5)
print "gps not working"
map_site = "Alcohol Detected!!\n" + "gps not working"
send_sms(map_site,admin_num)
send_sms(map_site,DMV_num)
sms_sent = True
lcd.clear()
lcd.message('Press switch...')
print "press switch"
break
if not GPIO.input(button):
sms_sent = False
lcd.clear()
lcd.message(' Engin stop ')
GPIO.output(motor2, False)
if half_on == True:
print "Engin Stop"
for dc in range(50,-1,-5):
p.ChangeDutyCycle(dc)
time.sleep(0.1)
full_on = False
half_on = False
elif full_on == True:
print "Engin Stop"
for dc in range(100,-1,-5):
p.ChangeDutyCycle(dc)
time.sleep(0.1)
full_on = False
half_on = False
GPIO.output(led, False)
GPIO.output(buzzer, False)
time.sleep(1)
sm = 0
lcd.clear()
lcd.message('Press switch...')
print "press switch"
break
if GPIO.input(restart) == False:
main = False
break
time.sleep(1)
time.sleep(1)
if GPIO.input(restart) == False:
break
##os.system("tvservice -p; fbset -depth 8; fbset -depth 16")
print "end"
lcd.clear()
lcd.message('Program Terminate')
time.sleep(2)
lcd.clear()
GPIO.cleanup()