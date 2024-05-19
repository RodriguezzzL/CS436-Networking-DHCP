import uuid
import socket

class ConnectionHandler:
    def __init__(self, mac_address, ip=None, timestamp=None):
        self.mac = mac_address
        self.ip = ip
        self.timestamp = timestamp

    def __str__(self):
        return f"MAC: {self.mac}, IP: {self.ip}, Timestamp: {self.timestamp}"

    def format_message(self):
        return f"{self.mac} {self.ip} {self.timestamp}"

def decode_msg(message):
    decoded_message = message.decode().strip()
    print("Received Message: ", decoded_message)
    return decoded_message.split()

def handle_response(parsed_message):
    response_type = parsed_message[0]
    if response_type == "OFFER":
        send_allocation_request(parsed_message[1], parsed_message[2], parsed_message[3])
    elif response_type == "ACKNOWLEDGE":
        connection.ip = parsed_message[2]
        connection.timestamp = parsed_message[3]
        show_menu()
    elif response_type == "DECLINE":
        print("Server declined IP request.")
    else:
        print("Invalid response received:", " ".join(parsed_message))

def send_allocation_request(mac_address, ip_address, timestamp):
    msg = f"REQUEST {mac_address} {ip_address} {timestamp}"
    send_to_server(msg)

def send_to_server(msg):
    print("Sending Message: ", msg)
    client_socket.sendto(msg.encode(), (server_ip, server_port))

def release_ip():
    msg = f"RELEASE {connection.format_message()}"
    send_to_server(msg)
    show_menu()

def renew_ip():
    send_to_server(f"RENEW {connection.format_message()}")
    server_response, _ = client_socket.recvfrom(4096)
    handle_response(decode_msg(server_response))

def show_menu():
    print("IP Management Menu:")
    print("1: Release IP")
    print("2: Renew IP Allocation")
    print("3: Exit")

    while True:
        choice = input("Select an option: ")
        if choice == "1":
            release_ip()
            break
        elif choice == "2":
            renew_ip()
            break
        elif choice == "3":
            quit()
            return
        else:
            print("Invalid option. Please select from the listed options.")

# Generate MAC address
local_mac = ":".join(["{:02x}".format((uuid.getnode() >> ele) & 0xFF) for ele in range(0, 8 * 6, 8)][::-1]).upper()
connection = ConnectionHandler(local_mac)

# Server Configuration
server_ip = "10.0.0.100"
server_port = 9000

client_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

# Send DISCOVER message
discovery_msg = f"DISCOVER {local_mac}"
client_socket.sendto(discovery_msg.encode(), (server_ip, server_port))

# Listen for Response
while True:
    server_response, _ = client_socket.recvfrom(4096)
    parsed_response = decode_msg(server_response)
    handle_response(parsed_response)
