"""
ESP32 BLE Scanner for Location-Based Attendance System
Continuously scans for BLE beacons and sends attendance data to Flask server
"""

import bluetooth
import urequests
import utime
import ujson
from machine import RTC

# Configuration
TARGET_SERVICE_UUID = "12345678-1234-5678-1234-56789abcdef0"
CLASSROOM_ID = 101  # Configure this for each classroom
SERVER_URL = "http://192.168.1.100:5000/api/attendance"  # Update with your server IP
SCAN_INTERVAL = 5  # seconds between scans

class BLEAttendanceScanner:
    def __init__(self, classroom_id, server_url, target_uuid):
        self.classroom_id = classroom_id
        self.server_url = server_url
        self.target_uuid = target_uuid
        self.ble = bluetooth.BLE()
        self.ble.active(True)
        self.rtc = RTC()
        
    def scan_for_beacons(self):
        """Scan for BLE beacons and filter by service UUID"""
        try:
            print("Starting BLE scan...")
            # Start scanning for 3 seconds
            self.ble.gap_scan(3000, 30000, 30000)
            
            # Wait for scan to complete
            utime.sleep(3)
            
            # Get scan results
            scan_results = self.ble.gap_scan_stop()
            
            detected_beacons = []
            for result in scan_results:
                addr_type, addr, adv_type, rssi, adv_data = result
                
                # Convert MAC address to string format
                mac_address = ":".join(["{:02x}".format(b) for b in addr])
                
                # Check if beacon matches our target service UUID
                if self.is_target_beacon(adv_data):
                    detected_beacons.append({
                        'mac_address': mac_address,
                        'rssi': rssi,
                        'timestamp': self.get_current_timestamp()
                    })
                    print(f"Detected target beacon: {mac_address} (RSSI: {rssi})")
            
            return detected_beacons
            
        except Exception as e:
            print(f"BLE scan error: {e}")
            return []
    
    def is_target_beacon(self, adv_data):
        """Check if advertisement data contains target service UUID"""
        try:
            # Parse advertisement data to find service UUID
            # This is a simplified check - in practice, you'd parse the full AD structure
            target_uuid_bytes = self.target_uuid.replace("-", "").lower()
            adv_hex = "".join(["{:02x}".format(b) for b in adv_data])
            
            return target_uuid_bytes in adv_hex.lower()
            
        except Exception as e:
            print(f"Error checking beacon: {e}")
            return False
    
    def get_current_timestamp(self):
        """Get current timestamp in MySQL datetime format"""
        try:
            current_time = self.rtc.datetime()
            # Format: YYYY-MM-DD HH:MM:SS
            timestamp = "{:04d}-{:02d}-{:02d} {:02d}:{:02d}:{:02d}".format(
                current_time[0], current_time[1], current_time[2],
                current_time[4], current_time[5], current_time[6]
            )
            return timestamp
        except Exception as e:
            print(f"Error getting timestamp: {e}")
            return "1970-01-01 00:00:00"
    
    def send_attendance_data(self, beacon_data):
        """Send attendance data to Flask server"""
        try:
            payload = {
                "student_mac_address": beacon_data['mac_address'],
                "classroom_id": self.classroom_id,
                "timestamp": beacon_data['timestamp']
            }
            
            headers = {'Content-Type': 'application/json'}
            
            print(f"Sending attendance data: {payload}")
            
            response = urequests.post(
                self.server_url,
                data=ujson.dumps(payload),
                headers=headers
            )
            
            if response.status_code == 200:
                print(f"✅ Attendance recorded successfully for {beacon_data['mac_address']}")
                response_data = ujson.loads(response.text)
                print(f"Server response: {response_data}")
            else:
                print(f"❌ Server error: {response.status_code} - {response.text}")
                
            response.close()
            
        except Exception as e:
            print(f"❌ Error sending attendance data: {e}")
    
    def run_continuous_scan(self):
        """Main loop - continuously scan for beacons and send data"""
        print(f"🚀 Starting BLE Attendance Scanner for Classroom {self.classroom_id}")
        print(f"📡 Target UUID: {self.target_uuid}")
        print(f"🌐 Server URL: {self.server_url}")
        print(f"⏱️  Scan interval: {SCAN_INTERVAL} seconds")
        print("-" * 50)
        
        while True:
            try:
                # Scan for beacons
                detected_beacons = self.scan_for_beacons()
                
                # Send data for each detected beacon
                for beacon in detected_beacons:
                    self.send_attendance_data(beacon)
                
                if not detected_beacons:
                    print("No target beacons detected in this scan")
                
                print(f"💤 Waiting {SCAN_INTERVAL} seconds before next scan...")
                utime.sleep(SCAN_INTERVAL)
                
            except KeyboardInterrupt:
                print("\n🛑 Scanner stopped by user")
                break
            except Exception as e:
                print(f"❌ Unexpected error in main loop: {e}")
                print(f"🔄 Retrying in {SCAN_INTERVAL} seconds...")
                utime.sleep(SCAN_INTERVAL)

def main():
    """Initialize and start the BLE scanner"""
    try:
        # Create scanner instance
        scanner = BLEAttendanceScanner(
            classroom_id=CLASSROOM_ID,
            server_url=SERVER_URL,
            target_uuid=TARGET_SERVICE_UUID
        )
        
        # Start continuous scanning
        scanner.run_continuous_scan()
        
    except Exception as e:
        print(f"❌ Failed to start scanner: {e}")

if __name__ == "__main__":
    main()
