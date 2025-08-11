```markdown
# Detailed Plan for the Location-Based Attendance System

This plan outlines the creation of three core components:
• An ESP32-based BLE scanner written in Python  
• A Flask backend server for processing attendance data  
• A MySQL database schema for recording entries

---

## Component 1: ESP32 BLE Scanner (File: /python/esp32_ble_scanner.py)

• **Dependencies & Setup:**  
  – Use MicroPython libraries: `bluetooth`, `urequests`, and `utime` for non-blocking operations.  
  – Define configurable parameters such as the target service UUID (`12345678-1234-5678-1234-56789abcdef0`) and a classroom ID.

• **Implementation Steps:**  
  1. Import necessary modules (e.g., `bluetooth`, `urequests`, `utime`).  
  2. Initialize BLE scanning and start a continuous, non-blocking scan loop.  
  3. Filter scanned beacons by matching the target service UUID.  
  4. Extract the MAC address from the advertisement data (representing the student ID).  
  5. Generate the current timestamp using a real-time clock call.  
  6. Construct a JSON payload containing `student_mac_address`, `classroom_id`, and `timestamp`.  
  7. Send the payload via an HTTP POST request to the Flask server endpoint (`/api/attendance`).  
  8. Implement try-except blocks to capture and log BLE scanning errors and HTTP request failures.  
  9. Introduce a configurable delay between scans to balance resource usage.

---

## Component 2: Flask Server (File: /python/attendance_server.py)

• **Dependencies & Setup:**  
  – Use Python libraries: `flask`, `mysql.connector` (or an equivalent like `PyMySQL`), and `datetime`.  
  – Load MySQL credentials and connection settings from environment variables or a dedicated config file.

• **Implementation Steps:**  
  1. Import necessary libraries (`Flask`, `request`, and `mysql.connector`).  
  2. Initialize the Flask app and configure logging for better error visibility.  
  3. Create an API endpoint `/api/attendance` that accepts POST requests.  
  4. In the endpoint, parse incoming JSON and validate that `student_mac_address`, `classroom_id`, and `timestamp` are present.  
  5. Connect to the MySQL database using secure credentials.  
  6. Use parameterized SQL queries to safely insert the attendance record into the `attendance` table.  
  7. Wrap database operations in try-except blocks to handle connection or query failures.  
  8. Return a clear JSON response indicating success ("Attendance recorded successfully") or a descriptive error message.

---

## Component 3: Database Schema (File: /python/create_attendance_table.sql)

• **SQL Table Design:**  
  – Create a table named `attendance` with these columns:  
    • `id`: INT auto-incrementing primary key  
    • `student_mac_address`: VARCHAR(255) NOT NULL  
    • `classroom_id`: INT NOT NULL  
    • `entry_timestamp`: DATETIME NOT NULL  

• **SQL Command Example:**  
```sql
CREATE TABLE attendance (
  id INT AUTO_INCREMENT PRIMARY KEY,
  student_mac_address VARCHAR(255) NOT NULL,
  classroom_id INT NOT NULL,
  entry_timestamp DATETIME NOT NULL
) ENGINE=InnoDB;
```
• Add an index on `student_mac_address` if needed for performance.

---

## README.md Updates

• **Documentation Enhancements:**  
  – Update the README to include an overview of the attendance system and instructions for setup.  
  – Detail installation steps for Python dependencies (e.g., `pip install flask mysql-connector-python`).  
  – Explain how to flash the ESP32 script and run the Flask server (command: `python attendance_server.py`).  
  – Include steps to initialize the MySQL database using `create_attendance_table.sql`.  
  – Provide troubleshooting tips and usage examples (e.g., sample curl commands).

---

## Integration and Testing

• **Testing Procedures:**  
  – Use a simulated BLE beacon environment to validate the ESP32 script’s detection logic.  
  – Manually test the Flask API endpoint using a curl command such as:
```bash
curl -X POST http://localhost:5000/api/attendance \
-H "Content-Type: application/json" \
-d '{"student_mac_address": "AA:BB:CC:DD:EE:FF", "classroom_id": 101, "timestamp": "2023-10-01 09:00:00"}'
```
  – Verify that successful responses are returned and the MySQL database reflects new attendance entries.  
  – Ensure that all error cases (e.g., missing fields, connection failures) are gracefully handled and logged.

---

## Error Handling & Best Practices

• Use robust try-except blocks in both the ESP32 and Flask scripts to capture and log unexpected errors.  
• Employ parameterized queries in the Flask server to mitigate SQL injection vulnerabilities.  
• Keep sensitive credentials out of source code by using environment variables or dedicated configuration files.  
• Maintain detailed logging for monitoring and debugging purposes.  
• Structure code into clear, reusable functions with appropriate inline documentation.

---

## Summary

• Three core components are created: an ESP32 BLE scanner, a Flask backend server, and a MySQL table setup.  
• The ESP32 script continuously scans for BLE beacons, filters by a specific UUID, extracts MAC addresses, and sends POST requests.  
• The Flask server validates input, uses secure parameterized queries, and handles database insertions with error handling.  
• The SQL file creates the `attendance` table as required.  
• README updates guide installation, configuration, and testing processes.  
• Comprehensive error handling and best practices are integrated in all components.  
• Sample curl commands are provided for endpoint verification.
