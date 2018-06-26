import machine, ssd1306, bme280, usched
import urequests

i2cDisplay = machine.I2C(scl=machine.Pin(4), sda=machine.Pin(5))
i2cSensor = machine.I2C(scl=machine.Pin(13), sda=machine.Pin(15))

oled = ssd1306.SSD1306_I2C(128, 64, i2cDisplay)
bme = bme280.BME280(i2c=i2cSensor)
adc = machine.ADC(machine.Pin(39))
adc.atten(adc.ATTN_11DB)

#bluePin = machine.PWM(machine.Pin(14))
bluePin = machine.Pin(14, machine.Pin.OUT)

price = 0

def get_price():
	global price
	while True:
		try:
			r = urequests.get("https://min-api.cryptocompare.com/data/price?fsym=BTC&tsyms=EUR")
			price = r.json()['EUR']
			r.close()
		except Exception as e:
			price = -1
		yield 30

def main_thread():
	global price
	while True:
		light = adc.read()
		oled.fill(0)
		t,p,h=bme.read_compensated_data()
		p = p // 256
		pi = p // 100
		pd = p - pi * 100
		hi = h // 1024
		hd = h * 100 // 1024 - hi * 100

		oled.text("Teplota: {}C".format(t / 100), 0, 0)
		oled.text("Tlak: {}.{:02d}hPa".format(pi, pd), 0, 13)
		oled.text("Vlhkost: {}.{:02d}%".format(hi, hd), 0, 26)
		oled.text("Svetlo: {}".format(light), 0, 39)
		oled.text("Bitcoin:{}EUR".format(price),0,52)
		oled.show()
		
		#bluePin.init() if int(light) > 3500 else bluePin.deinit()
		bluePin.value(1) if int(light) > 3500 else bluePin.value(0)
		yield 1


def connect():
	import network
	global oled

	oled.text("Wifi connecting", 0, 0)
	oled.show()
	ssid = "wifi_name"
	password =  "wifi_pass"

	station = network.WLAN(network.STA_IF)

	if station.isconnected() == True:
		print("Already connected")
		oled.text("Already connected", 0, 13)
		oled.show()
		return

	station.active(True)
	station.connect(ssid, password)

	while station.isconnected() == False:
		pass

	print("Successful")
	oled.text("Successful", 0, 13)
	oled.show()
	print(station.ifconfig())

#bluePin.freq(60)
#bluePin.deinit()
connect()
objSched = usched.Sched()
objSched.add_thread(get_price())
objSched.add_thread(main_thread())
objSched.run()
