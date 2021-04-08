import os
import time

import paho.mqtt.client as mqtt

from telegram.bot import Bot
from telegram.parsemode import ParseMode

# initializing the bot with API_KEY and CHAT_ID
if os.getenv('TELEGRAM_BOT_API_KEY') == None:
	print("Error: Please set the environment variable TELEGRAM_BOT_API_KEY and try again.")
	exit(1)
bot = Bot(os.getenv('TELEGRAM_BOT_API_KEY'))

if os.getenv('TELEGRAM_BOT_CHAT_ID') == None:
	print("Error: Please set the environment variable TELEGRAM_BOT_CHAT_ID and try again.")
	exit(1)
chat_id = os.getenv('TELEGRAM_BOT_CHAT_ID')

# based on example from https://pypi.org/project/paho-mqtt/
# The callback for when the client receives a CONNACK response from the server.


def on_connect(client, userdata, flags, rc):
	print("Connected with result code "+str(rc))
	if rc == 0:
		print("Connected successfully to broker")
		# bot.send_message(
		# 	chat_id,
		# 	text="Connecté au brocker MQTT...",
		# 	parse_mode=ParseMode.HTML,
		# )
	else:
		print("Connection failed")

	# Subscribing in on_connect() means that if we lose the connection and
	# reconnect then subscriptions will be renewed.

	# client.subscribe("teslamate/cars/1/version")
	client.subscribe("teslamate/cars/1/update_available")
	client.subscribe("teslamate/cars/1/doors_open")
	client.subscribe("teslamate/cars/1/usable_battery_level")
	client.subscribe("teslamate/cars/1/plugged_in")
	client.subscribe("teslamate/cars/1/time_to_full_charge")
	client.subscribe("teslamate/cars/1/locked")
	client.subscribe("teslamate/cars/1/state")
	# client.subscribe("teslamate/cars/1/shift_state")
	# client.subscribe("teslamate/cars/1/latitude")
	# client.subscribe("teslamate/cars/1/longitude")
	# client.subscribe("teslamate/cars/1/speed")
	# client.subscribe("teslamate/cars/1/heading")

# The callback for when a PUBLISH message is received from the server.


def on_message(client, userdata, msg):
	print(msg.topic+" "+str(msg.payload.decode()))

	if msg.topic == "teslamate/cars/1/state":
		print("Voiture 1 / Changement d'état : "+str(msg.payload.decode()))
		if str(msg.payload.decode()) == "online":
			car_state = "😃"
		elif str(msg.payload.decode()) == "charging":
			car_state = "🤤"
		elif str(msg.payload.decode()) == "asleep":
			car_state = "😴"
		elif str(msg.payload.decode()) == "suspended":
			car_state = "🥱"
		elif str(msg.payload.decode()) == "offline":
			car_state = "👻"
		elif str(msg.payload.decode()) == "driving":
			car_state = "🛣"
		else:
			car_state = str(msg.payload.decode())
		bot.send_message(
			chat_id,
			text="<b>"+"Voiture 1"+"</b>"+" Etat : "+car_state,
			parse_mode=ParseMode.HTML,
		)

	if msg.topic == "teslamate/cars/1/doors_open":
		print("Voiture 1 / Portière / changement d'état : "+str(msg.payload.decode()))
		door_state = "ouverte" if msg.payload.decode() == "true" else "fermée"
		bot.send_message(
			chat_id,
			text="<b>"+"Voiture 1"+"</b>"+" Porte "+door_state,
			parse_mode=ParseMode.HTML,
		)

	if msg.topic == "teslamate/cars/1/locked":
		print("Voiture 1 / Verrouillage / changement d'état : "+str(msg.payload.decode()))
		lock_state = "🔐 verrouilée" if msg.payload.decode() == "true" else "🔓 déverrouilée"
		bot.send_message(
			chat_id,
			text="<b>"+"Voiture 1"+"</b> "+lock_state,
			parse_mode=ParseMode.HTML,
		)

	if msg.topic == "teslamate/cars/1/update_available" and msg.payload.decode() == "true":
		print("Voiture 1 / Mise à jour dispo")
		bot.send_message(
			chat_id,
			# text="<b>"+"SW Update"+"</b>\n"+"A new SW update for your Tesla is available!\n\n<b>"+msg.topic+"</b>\n"+str(msg.payload.decode()),
			text="<b>"+"Voiture 1"+"</b>"+" Une mise à jour est disponible.",
			parse_mode=ParseMode.HTML,
		)

	if msg.topic == "teslamate/cars/1/usable_battery_level":
		print("Voiture 1 / Batterie status")
		bot.send_message(
			chat_id,
			text="<b>"+"Voiture 1"+"</b>"+" 🔋 Batterie à "+str(msg.payload.decode())+"%",
			parse_mode=ParseMode.HTML,
		)

	if msg.topic == "teslamate/cars/1/plugged_in":
		print("Voiture 1 / Charge status")
		charge_state = "🔌 En train de charger" if msg.payload.decode() == "true" else "🔋 Sur batterie"
		bot.send_message(
			chat_id,
			text="<b>"+"Voiture 1"+"</b> "+charge_state,
			parse_mode=ParseMode.HTML,
		)

	if msg.topic == "teslamate/cars/1/time_to_full_charge" and float(msg.payload.decode()) > 0.0 :
		print("Voiture 1 / Temps de recharge restant "+str(msg.payload.decode())+" en heure")
		temps_restant = float(msg.payload.decode()) * float(60)
		texte_temps = str(temps_restant)+" minutes pour être chargée." if temps_restant > 1 else str(temps_restant)+" minute pour être chargée."
		bot.send_message(
			chat_id,
			text="<b>"+"Voiture 1"+"</b>"+"⏳ Reste "+texte_temps,
			parse_mode=ParseMode.HTML,
		)

client = mqtt.Client()
client.on_connect = on_connect
client.on_message = on_message

client.connect(os.getenv('MQTT_BROKER_HOST', '127.0.0.1'),
			   int(os.getenv('MQTT_BROKER_PORT', 1883)), 60)

# Blocking call that processes network traffic, dispatches callbacks and
# handles reconnecting.
# Other loop*() functions are available that give a threaded interface and a
# manual interface.
# client.loop_forever()


client.loop_start()  # start the loop
try:
	while True:
		time.sleep(1)

except KeyboardInterrupt:

	print("exiting")


client.disconnect()

client.loop_stop()
