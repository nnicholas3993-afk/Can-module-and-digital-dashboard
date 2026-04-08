import can
import time
import math

def run_fake_ecu():
    # Connect to the exact same virtual channel
    bus = can.Bus(channel='232.164.1.1', interface='udp_multicast')
    print("Fake ECU is running and broadcasting data...")

    t = 0.0
    while True:
        t += 0.033

        # Simulate the math dynamics
        rpm = int(3000 + 2000 * math.sin(t * 1.7))
        speed = int(rpm * 0.02 + 20 * math.sin(t * 0.8))
        battery = int(75 + 25 * math.sin(t * 0.3))
        temp = int(70 + 30 * abs(math.sin(t * 0.5)))
        
        gear_val = 0 # "N"
        if speed > 80: gear_val = 5
        elif speed > 60: gear_val = 4
        elif speed > 40: gear_val = 3
        elif speed > 20: gear_val = 2
        elif speed > 5: gear_val = 1

        # Clamp values to valid byte ranges
        rpm = max(0, min(8000, rpm))
        speed = max(0, min(255, speed))
        battery = max(0, min(100, battery))
        temp = max(0, min(255, temp))

        # --- Message 1: RPM (Bytes 0-1) and Speed (Byte 2) ---
        rpm_bytes = rpm.to_bytes(2, byteorder='big')
        msg1 = can.Message(
            arbitration_id=0x101,
            data=[rpm_bytes[0], rpm_bytes[1], speed, 0, 0, 0, 0, 0],
            is_extended_id=False
        )

        # --- Message 2: Temp (Byte 0) and Battery (Byte 1) ---
        msg2 = can.Message(
            arbitration_id=0x102,
            data=[temp, battery, 0, 0, 0, 0, 0, 0],
            is_extended_id=False
        )

        # --- Message 3: Gear (Byte 0) ---
        msg3 = can.Message(
            arbitration_id=0x103,
            data=[gear_val, 0, 0, 0, 0, 0, 0, 0],
            is_extended_id=False
        )

        # Send to the virtual bus
        bus.send(msg1)
        bus.send(msg2)
        bus.send(msg3)

        # Wait ~33ms before sending the next batch
        time.sleep(0.033)

if __name__ == "__main__":
    run_fake_ecu()