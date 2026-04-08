import can

class RealCANBus:
    def __init__(self, channel='gokart_test_bus'):
        self.latest_data = {
            "speed": 0, "rpm": 0, "battery": 100, "temp": 20, "gear": "N"
        }
        
        try:
            # Assuming your physical kart runs at a 500kbps baud rate
            self.bus = can.interface.Bus(channel='can0', bustype='socketcan', bitrate=500000)
            print(f"Connected to virtual bus: {channel}")
        except Exception as e:
            print(f"CRITICAL ERROR: Could not connect to virtual CAN bus. {e}")
            self.bus = None

    def read(self):
        # ---> DIAGNOSTIC PRINT 1 <---
        if not self.bus:
            print("DEBUG CAN: ERROR - The bus is None!")
            return self.latest_data

        msg_count = 0
        while True:
            msg = self.bus.recv(timeout=0.0)
            if msg is None:
                break
            
            msg_count += 1

            # Parsing ID 0x101: RPM (2 bytes), Speed (1 byte)
            if msg.arbitration_id == 0x101:
                self.latest_data["rpm"] = int.from_bytes(msg.data[0:2], byteorder='big')
                self.latest_data["speed"] = msg.data[2]
                
            # Parsing ID 0x102: Temp (1 byte), Battery (1 byte)
            elif msg.arbitration_id == 0x102:
                self.latest_data["temp"] = msg.data[0]
                self.latest_data["battery"] = msg.data[1]
                
            # Parsing ID 0x103: Gear (1 byte)
            elif msg.arbitration_id == 0x103:
                gear_map = {0: "N", 1: "1", 2: "2", 3: "3", 4: "4", 5: "5"}
                self.latest_data["gear"] = gear_map.get(msg.data[0], "E")

        # ---> DIAGNOSTIC PRINT 2 <---
        if msg_count > 0:
            print(f"DEBUG CAN: Successfully pulled {msg_count} messages off the bus!")

        return self.latest_data