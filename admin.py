#!/usr/bin/env python3
import uuid
import socket
from datetime import datetime as dt

class ConnectionInfo:
    def __init__(self, mac, ip, timestamp):
        self.mac = mac
        self.ip = ip
        self.timestamp = timestamp

    def __str__(self):
        return f"MAC: {self.mac}, IP: {self.ip}, Timestamp: {self.timestamp}"

    def get_message_string(self):
        return f"{self.mac} {self.ip} {self.timestamp}"

def parse_received_message(message):
    decoded_message = message.decode()
    print("Received from server: " + decoded_message)
    parsed_message = decoded_message.split(" ")
    return parsed_message

def handle_response(parsed_message):
    if parsed_message[0] == "OFFER":
        send_request(parsed_message[1], parsed_message[2], parsed_message[3])
    elif parsed_message[0] == "ACKNOWLEDGE":
        connection_info.ip = parsed_message[2]
        connection_info.timestamp = parsed_message[3]
        menu()
    elif parsed_message[0] == "DECLINE":
        print("No address offered. Allocation declined.")
    else:
        print("Received an odd message:")
        for item in parsed_message:
            print(item)

def send_request(mac, ip, timestamp):
    message = f"REQUEST {mac} {ip} {timestamp}"
    send_message(message)

def send_message(dhcp_message):
    print("Sending to server: " + dhcp_message)
    client_socket.sendto(dhcp_message.encode(), (SERVER_IP, SERVER_PORT))

def release_ip():
    message = f"RELEASE {connection_info.get_message_string()}"
    send_message(message)
    menu()

def renew_ip():
    send_message(f"RENEW {connection_info.get_message_string()}")
    message, _ = client_socket.recvfrom(4096)
    handle_response(parse_received_message(message))

def request_list():
    send_message("LIST")
    message, _ = client_socket.recvfrom(4096)
    print(message.decode())
    menu()

def menu():
    print("IP allocation management options:")
    print("0: LIST (Admin Only)")
    print("1: RELEASE IP")
    print("2: RENEW IP")
    print("3: Exit")

    valid_option = False
    while not valid_option:
        option = input("Select: ")
        if option == "0":
            valid_option = True
            request_list()
        elif option == "1":
            valid_option = True
            release_ip()
        elif option == "2":
            valid_option = True
            renew_ip()
        elif option == "3":
            valid_option = True
            quit()
            return
        else:
            print("Invalid selection. Please choose from the listed options.")

# Extract local MAC address
mac_address = ":".join(["{:02x}".format((uuid.getnode() >> ele) & 0xFF) for ele in range(0, 8 * 6, 8)][::-1]).upper()
connection_info = ConnectionInfo(mac_address, None, None)

# Server IP and port number
SERVER_IP = "10.0.0.100"
SERVER_PORT = 9000

client_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

# Sending DISCOVER message
message = "DISCOVER " + mac_address
client_socket.sendto(message.encode(), (SERVER_IP, SERVER_PORT))

# Listening for response
while True:
    try:
        message, _ = client_socket.recvfrom(4096)
        parsed_message = parse_received_message(message)
        handle_response(parsed_message)
    except Exception as e:
        print(e)
