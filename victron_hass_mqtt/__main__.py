import argparse
import ssl
import threading

import paho.mqtt.client as mqtt
from vedirect import Vedirect
from victron_hass_mqtt.h import Device, Sensor

sensor_mapping = {}

client = None
ve = None
global_name = None
global_windowing = None

def setup_devices():
    global client, global_name, global_windowing
    device = Device(f"victron-{global_name.lower()}", global_name, "1.0", "SmartSolar 7510", "Victron")
    sensor_mapping["H19"] = Sensor(
        client,
        "Yield Total",
        topic_parent_level="Solar",
        parent_device=device,
        unit_of_measurement="kWh",
        device_class="energy",
        state_class="total_increasing",
        multiplier=0.01,
        mov_avg=global_windowing
    )
    sensor_mapping["H20"] = Sensor(
        client,
        "Yield Today",
        topic_parent_level="Solar",
        parent_device=device,
        unit_of_measurement="kWh",
        device_class="energy",
        state_class="total_increasing",
        multiplier=0.01,
        mov_avg=global_windowing
    )
    sensor_mapping["V"] = Sensor(
        client,
        "Battery Voltage",
        topic_parent_level="Solar",
        parent_device=device,
        unit_of_measurement="V",
        device_class="voltage",
        state_class="measurement",
        multiplier=0.001,
        mov_avg=global_windowing
    )
    sensor_mapping["VPV"] = Sensor(
        client,
        "Panel Voltage",
        topic_parent_level="Solar",
        parent_device=device,
        unit_of_measurement="V",
        device_class="voltage",
        state_class="measurement",
        multiplier=0.001,
        mov_avg=global_windowing
    )
    sensor_mapping["I"] = Sensor(
        client,
        "Battery Current",
        topic_parent_level="Solar",
        parent_device=device,
        unit_of_measurement="A",
        device_class="current",
        state_class="measurement",
        multiplier=0.001,
        mov_avg=global_windowing
    )
    sensor_mapping["IL"] = Sensor(
        client,
        "Load Current",
        topic_parent_level="Solar",
        parent_device=device,
        unit_of_measurement="A",
        device_class="current",
        state_class="measurement",
        multiplier=0.001,
        mov_avg=global_windowing
    )
    sensor_mapping["PPV"] = Sensor(
        client,
        "Panel Power",
        topic_parent_level="Solar",
        parent_device=device,
        unit_of_measurement="W",
        device_class="power",
        state_class="measurement",
        mov_avg=global_windowing
    )


def mqtt_send_callback(packet):
    for key, value in packet.items():
        if key != 'SER#' and key in sensor_mapping.keys():  # topic cannot contain MQTT wildcards
            sensor_mapping[key].send(value)


def on_connect(*args, **kwargs):
    global ve
    threading.Thread(target=setup_devices).start()
    threading.Thread(target=ve.read_data_callback, args=[mqtt_send_callback]).start()


def on_message(*args, **kwargs):
    pass  # print(f"message: {args}{kwargs}")


def on_publish(*args, **kwargs):
    pass #print(f"publish: {args}{kwargs}")


def main():
    global client, ve, global_name, global_windowing
    parser = argparse.ArgumentParser(description='Process VE.Direct protocol')
    parser.add_argument('--tty', help='Serial port', required=True)
    parser.add_argument('--name', help='MQTT Identifier', required=True)
    parser.add_argument('--timeout', help='Serial port read timeout', type=int, default='60')
    parser.add_argument('--window_size', help='Sliding window moving average', type=int, default='60')
    parser.add_argument('--broker', help='MQTT broker address', type=str, default='test.mosquitto.org')
    parser.add_argument('--port', help='MQTT broker port', type=int, default='1883')
    parser.add_argument('--username', help='MQTT broker port', default=None)
    parser.add_argument('--password', help='MQTT password', default=None)
    parser.add_argument('--tls', help='Use tls', action='store_true', default=False)
    parser.add_argument('--ca_path', help='TLS CA cert path (required if using TLS)',
                        default="/etc/ssl/certs/ca-certificates.crt")
    args = parser.parse_args()
    global_name = args.name
    global_windowing = args.window_size
    ve = Vedirect(args.tty, args.timeout)

    client = mqtt.Client()
    client.on_connect = on_connect
    client.on_message = on_message
    client.on_publish = on_publish
    if args.username and args.password:
        client.username_pw_set(args.username, args.password)
    if args.tls:
        client.tls_set(args.ca_path, tls_version=ssl.PROTOCOL_TLSv1_2)
    client.connect(args.broker, args.port, 60)
    print(f"Successfully started!")
    client.loop_forever()

if __name__ == '__main__':
    main()