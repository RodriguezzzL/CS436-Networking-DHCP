import socket
from ipaddress import IPv4Network
from datetime import datetime, timedelta

class DHCPClient:
    def __init__(self, mac_address):
        self.mac_address = mac_address
        self.ip_address = None
        self.lease_expiration = None

class DHCPManager:
    def __init__(self, subnet="192.168.0.0/24", lease_duration=600):
        self.subnet = IPv4Network(subnet)
        self.lease_duration = timedelta(seconds=lease_duration)
        self.clients = {}

    def offer_ip(self, mac_address):
        for ip in self.subnet.hosts():
            if ip not in self.clients or self.clients[ip].lease_expiration < datetime.now():
                self.clients[ip] = DHCPClient(mac_address)
                self.clients[ip].ip_address = ip
                self.clients[ip].lease_expiration = datetime.now() + self.lease_duration
                return f"OFFER {mac_address} {ip} {self.clients[ip].lease_expiration.isoformat()}"
        return "DECLINE"
    
    def list_clients(self):
        client_info = []
        for client in self.clients.values():
            client_info.append({
                "MAC Address": client.mac_address,
                "IP Address": client.ip_address,
                "Lease Expiration": client.lease_expiration.isoformat()
            })
        return client_info

    def acknowledge_ip(self, mac_address):
        if mac_address in [client.mac_address for client in self.clients.values()]:
            client = next(client for client in self.clients.values() if client.mac_address == mac_address)
            if client.lease_expiration > datetime.now():
                return f"ACKNOWLEDGE {mac_address} {client.ip_address} {client.lease_expiration.isoformat()}"
        return "DECLINE"

    def release_ip(self, mac_address):
        keys_to_delete = [ip for ip, client in self.clients.items() if client.mac_address == mac_address]
        for ip in keys_to_delete:
             del self.clients[ip]

    def renew_ip(self, mac_address):
        if mac_address in [client.mac_address for client in self.clients.values()]:
            client = next(client for client in self.clients.values() if client.mac_address == mac_address)
            if client.lease_expiration > datetime.now():
                client.lease_expiration = datetime.now() + self.lease_duration
                return f"RENEWED {mac_address} {client.ip_address} {client.lease_expiration.isoformat()}"
            else:
                return self.offer_ip(mac_address)
        else:
            return self.offer_ip(mac_address)

# Start a UDP server
server = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
server.bind(("", 9000))
print("DHCP Server is running...")

dhcp_manager = DHCPManager()

while True:
    try:
        message, client_address = server.recvfrom(4096)
        decoded_message = message.decode()
        print("Server received: " + decoded_message)
        parsed_message = decoded_message.split(" ")
        mac_address = parsed_message[1]
        if parsed_message[0] == "DISCOVER":
            response = dhcp_manager.offer_ip(mac_address)
        elif parsed_message[0] == "REQUEST":
            response = dhcp_manager.acknowledge_ip(mac_address)
        elif parsed_message[0] == "RELEASE":
            dhcp_manager.release_ip(mac_address)
            response = "RELEASED"
        elif parsed_message[0] == "RENEW":
            response = dhcp_manager.renew_ip(mac_address)
        else:
            response = "INVALID REQUEST"
        print("Server sending: " + response)
        server.sendto(response.encode(), client_address)
    except KeyboardInterrupt:
        print("Server stopped.")
        break
    except Exception as e:
        print(e)
        pass

server.close()
