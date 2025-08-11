# Location-Based Attendance System

A comprehensive BLE (Bluetooth Low Energy) based attendance tracking system that automatically detects student presence in classrooms using beacon technology.

## 🎯 System Overview

This system consists of three main components:
1. **ESP32 BLE Scanner** - Detects BLE beacons (student tags) in classrooms
2. **Flask Backend Server** - Processes attendance data and manages database
3. **MySQL Database** - Stores attendance records with timestamps

## 🏗️ Architecture

```
[Student BLE Beacons] → [ESP32 Scanner] → [Flask Server] → [MySQL Database]
```

- **BLE Beacons**: Carried by students, broadcast unique identifiers
- **ESP32 Scanners**: Installed in each classroom, scan for nearby beacons
- **Flask Server**: Central processing unit that validates and stores data
- **MySQL Database**: Persistent storage for all attendance records

## 📁 Project Structure

### Python Backend Components
- `python/esp32_ble_scanner.py`: ESP32 MicroPython script for BLE scanning
- `python/attendance_server.py`: Flask server for data processing
- `python/create_attendance_table.sql`: MySQL database schema
- `python/requirements.txt`: Python dependencies

### Next.js Frontend (Original)
- `src/components/ui/`: Reusable UI components
- `src/hooks/`: Custom React hooks
- `src/lib/utils.ts`: Utility functions
- `src/app/`: Application root with global styles

## 🚀 Quick Start

### Prerequisites
- **Hardware**: ESP32 microcontroller, BLE beacons
- **Software**: Python 3.8+, MySQL 8.0+, MicroPython (for ESP32)
- **Network**: WiFi connection for ESP32 and server communication

### 1. Database Setup

```bash
# Install MySQL and create database
mysql -u root -p
CREATE DATABASE attendance_system;
USE attendance_system;

# Run the schema file
source python/create_attendance_table.sql;
```

### 2. Flask Server Setup

```bash
# Navigate to python directory
cd python

# Install Python dependencies
pip install -r requirements.txt

# Set environment variables (create .env file)
export MYSQL_HOST=localhost
export MYSQL_DATABASE=attendance_system
export MYSQL_USER=root
export MYSQL_PASSWORD=your_password
export MYSQL_PORT=3306

# Start the Flask server
python attendance_server.py
```

The server will start on `http://localhost:5000`

### 3. ESP32 Configuration

```bash
# Flash MicroPython to ESP32
esptool.py --chip esp32 --port /dev/ttyUSB0 erase_flash
esptool.py --chip esp32 --port /dev/ttyUSB0 write_flash -z 0x1000 micropython.bin

# Upload the scanner script
ampy --port /dev/ttyUSB0 put python/esp32_ble_scanner.py main.py

# Configure WiFi and server settings in the script:
# - Update SERVER_URL with your Flask server IP
# - Set CLASSROOM_ID for each room
# - Configure TARGET_SERVICE_UUID for your beacons
```

## 🔧 Configuration

### ESP32 Scanner Settings
Edit `python/esp32_ble_scanner.py`:
```python
TARGET_SERVICE_UUID = "12345678-1234-5678-1234-56789abcdef0"  # Your beacon UUID
CLASSROOM_ID = 101  # Unique ID for each classroom
SERVER_URL = "http://192.168.1.100:5000/api/attendance"  # Flask server URL
SCAN_INTERVAL = 5  # Seconds between scans
```

### Flask Server Settings
Edit environment variables or `python/attendance_server.py`:
```python
MYSQL_CONFIG = {
    'host': 'localhost',
    'database': 'attendance_system',
    'user': 'root',
    'password': 'your_password',
    'port': 3306
}
```

## 📡 API Endpoints

### POST /api/attendance
Record new attendance entry
```bash
curl -X POST http://localhost:5000/api/attendance \
  -H "Content-Type: application/json" \
  -d '{
    "student_mac_address": "AA:BB:CC:DD:EE:FF",
    "classroom_id": 101,
    "timestamp": "2024-01-15 09:00:00"
  }'
```

### GET /api/attendance/recent
Get recent attendance records
```bash
curl http://localhost:5000/api/attendance/recent?limit=10
```

### GET /api/health
Server health check
```bash
curl http://localhost:5000/api/health
```

## 🧪 Testing

### Test Flask Server
```bash
# Start the server
python python/attendance_server.py

# Test attendance recording
curl -X POST http://localhost:5000/api/attendance \
  -H "Content-Type: application/json" \
  -d '{
    "student_mac_address": "AA:BB:CC:DD:EE:01",
    "classroom_id": 101,
    "timestamp": "2024-01-15 09:00:00"
  }'

# Check recent records
curl http://localhost:5000/api/attendance/recent

# Health check
curl http://localhost:5000/api/health
```

### Test Database
```sql
-- Check attendance records
SELECT * FROM attendance ORDER BY entry_timestamp DESC LIMIT 10;

-- Get attendance by classroom
SELECT * FROM attendance WHERE classroom_id = 101;

-- Daily attendance summary
SELECT * FROM daily_attendance_counts;
```

## 📊 Database Schema

### Main Table: `attendance`
- `id`: Auto-incrementing primary key
- `student_mac_address`: BLE beacon MAC address (VARCHAR 255)
- `classroom_id`: Classroom identifier (INT)
- `entry_timestamp`: When student was detected (DATETIME)
- `created_at`: Record creation time (TIMESTAMP)

### Views Available:
- `attendance_summary`: Formatted attendance data
- `daily_attendance_counts`: Daily statistics by classroom

## 🔒 Security Features

- **SQL Injection Protection**: Parameterized queries
- **Input Validation**: Server-side data validation
- **Error Handling**: Comprehensive error logging
- **Environment Variables**: Secure credential management

## 📝 Logging

The system provides detailed logging:
- **ESP32**: Console output for debugging
- **Flask Server**: File and console logging (`attendance_server.log`)
- **Database**: Query logging and error tracking

## 🛠️ Troubleshooting

### Common Issues

**ESP32 Connection Problems:**
- Check WiFi credentials and network connectivity
- Verify server URL and port accessibility
- Ensure MicroPython is properly flashed

**Database Connection Errors:**
- Verify MySQL service is running
- Check database credentials and permissions
- Ensure database and tables exist

**BLE Detection Issues:**
- Confirm beacon UUID matches configuration
- Check beacon battery levels and transmission power
- Verify ESP32 BLE functionality

### Debug Commands
```bash
# Check MySQL connection
mysql -u root -p -e "SELECT 1"

# Test server connectivity
ping your_server_ip

# Check ESP32 logs
screen /dev/ttyUSB0 115200
```

## 🚀 Deployment

### Production Deployment
1. Use a production WSGI server (Gunicorn, uWSGI)
2. Set up reverse proxy (Nginx)
3. Configure SSL certificates
4. Set up database backups
5. Implement monitoring and alerting

```bash
# Example production setup
pip install gunicorn
gunicorn -w 4 -b 0.0.0.0:5000 attendance_server:app
```

## 📈 Future Enhancements

- **Web Dashboard**: Real-time attendance monitoring
- **Mobile App**: Student and teacher interfaces
- **Analytics**: Attendance patterns and reporting
- **Integration**: LMS and student information systems
- **Scalability**: Multi-campus support

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests if applicable
5. Submit a pull request

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 🆘 Support

For support and questions:
- Create an issue in the repository
- Check the troubleshooting section
- Review the API documentation

---

## Original Next.js Setup (Still Available)

This is a [Next.js](https://nextjs.org) project bootstrapped with [`create-next-app`](https://nextjs.org/docs/app/api-reference/cli/create-next-app).

### Getting Started

First, run the development server:

```bash
npm run dev
# or
yarn dev
# or
pnpm dev
# or
bun dev
```

Open [http://localhost:3000](http://localhost:3000) with your browser to see the result.

### Core Dependencies
- **UI + Styling**: @radix-ui/**, tailwindcss, class-variance-authority
- **Icons and Themes**: lucide-react, next-themes
- **Forms**: react-hook-form, @hookform/resolvers
- **Specialized**: recharts, embla-carousel-react, vaul, cmdk, sonner

### Learn More

To learn more about Next.js, take a look at the following resources:

- [Next.js Documentation](https://nextjs.org/docs) - learn about Next.js features and API.
- [Learn Next.js](https://nextjs.org/learn) - an interactive Next.js tutorial.

You can check out [the Next.js GitHub repository](https://github.com/vercel/next.js) - your feedback and contributions are welcome!
