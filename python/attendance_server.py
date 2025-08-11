"""
Flask Server for Location-Based Attendance System
Receives attendance data from ESP32 BLE scanners and stores in MySQL database
"""

from flask import Flask, request, jsonify
import mysql.connector
from mysql.connector import Error
import datetime
import logging
import os
from typing import Dict, Any

# Configuration
MYSQL_CONFIG = {
    'host': os.getenv('MYSQL_HOST', 'localhost'),
    'database': os.getenv('MYSQL_DATABASE', 'attendance_system'),
    'user': os.getenv('MYSQL_USER', 'root'),
    'password': os.getenv('MYSQL_PASSWORD', 'password'),
    'port': int(os.getenv('MYSQL_PORT', 3306))
}

# Initialize Flask app
app = Flask(__name__)

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('attendance_server.log'),
        logging.StreamHandler()
    ]
)

logger = logging.getLogger(__name__)

class AttendanceDatabase:
    """Database handler for attendance records"""
    
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.connection = None
    
    def connect(self):
        """Establish database connection"""
        try:
            self.connection = mysql.connector.connect(**self.config)
            if self.connection.is_connected():
                logger.info("✅ Successfully connected to MySQL database")
                return True
        except Error as e:
            logger.error(f"❌ Error connecting to MySQL: {e}")
            return False
    
    def disconnect(self):
        """Close database connection"""
        if self.connection and self.connection.is_connected():
            self.connection.close()
            logger.info("🔌 MySQL connection closed")
    
    def insert_attendance_record(self, student_mac: str, classroom_id: int, timestamp: str) -> bool:
        """Insert attendance record into database"""
        try:
            if not self.connection or not self.connection.is_connected():
                if not self.connect():
                    return False
            
            cursor = self.connection.cursor()
            
            # Parameterized query to prevent SQL injection
            insert_query = """
                INSERT INTO attendance (student_mac_address, classroom_id, entry_timestamp)
                VALUES (%s, %s, %s)
            """
            
            # Convert timestamp string to datetime object
            try:
                timestamp_obj = datetime.datetime.strptime(timestamp, '%Y-%m-%d %H:%M:%S')
            except ValueError:
                logger.error(f"❌ Invalid timestamp format: {timestamp}")
                return False
            
            record_data = (student_mac, classroom_id, timestamp_obj)
            
            cursor.execute(insert_query, record_data)
            self.connection.commit()
            
            record_id = cursor.lastrowid
            cursor.close()
            
            logger.info(f"✅ Attendance record inserted successfully (ID: {record_id})")
            logger.info(f"   Student MAC: {student_mac}")
            logger.info(f"   Classroom: {classroom_id}")
            logger.info(f"   Timestamp: {timestamp}")
            
            return True
            
        except Error as e:
            logger.error(f"❌ Database error: {e}")
            if self.connection:
                self.connection.rollback()
            return False
        except Exception as e:
            logger.error(f"❌ Unexpected error: {e}")
            return False
    
    def get_recent_attendance(self, limit: int = 10) -> list:
        """Get recent attendance records for testing/debugging"""
        try:
            if not self.connection or not self.connection.is_connected():
                if not self.connect():
                    return []
            
            cursor = self.connection.cursor(dictionary=True)
            
            query = """
                SELECT id, student_mac_address, classroom_id, entry_timestamp
                FROM attendance
                ORDER BY entry_timestamp DESC
                LIMIT %s
            """
            
            cursor.execute(query, (limit,))
            records = cursor.fetchall()
            cursor.close()
            
            # Convert datetime objects to strings for JSON serialization
            for record in records:
                if 'entry_timestamp' in record:
                    record['entry_timestamp'] = record['entry_timestamp'].strftime('%Y-%m-%d %H:%M:%S')
            
            return records
            
        except Error as e:
            logger.error(f"❌ Error fetching records: {e}")
            return []

# Initialize database handler
db = AttendanceDatabase(MYSQL_CONFIG)

@app.route('/api/attendance', methods=['POST'])
def record_attendance():
    """API endpoint to record attendance"""
    try:
        # Get JSON data from request
        data = request.get_json()
        
        if not data:
            logger.warning("❌ No JSON data received")
            return jsonify({
                'success': False,
                'message': 'No JSON data provided'
            }), 400
        
        # Validate required fields
        required_fields = ['student_mac_address', 'classroom_id', 'timestamp']
        missing_fields = [field for field in required_fields if field not in data]
        
        if missing_fields:
            logger.warning(f"❌ Missing required fields: {missing_fields}")
            return jsonify({
                'success': False,
                'message': f'Missing required fields: {", ".join(missing_fields)}'
            }), 400
        
        # Extract data
        student_mac = data['student_mac_address'].strip()
        classroom_id = int(data['classroom_id'])
        timestamp = data['timestamp'].strip()
        
        # Validate data
        if not student_mac:
            return jsonify({
                'success': False,
                'message': 'Student MAC address cannot be empty'
            }), 400
        
        if classroom_id <= 0:
            return jsonify({
                'success': False,
                'message': 'Classroom ID must be a positive integer'
            }), 400
        
        logger.info(f"📝 Processing attendance record:")
        logger.info(f"   Student MAC: {student_mac}")
        logger.info(f"   Classroom: {classroom_id}")
        logger.info(f"   Timestamp: {timestamp}")
        
        # Insert record into database
        success = db.insert_attendance_record(student_mac, classroom_id, timestamp)
        
        if success:
            return jsonify({
                'success': True,
                'message': 'Attendance recorded successfully',
                'data': {
                    'student_mac_address': student_mac,
                    'classroom_id': classroom_id,
                    'timestamp': timestamp
                }
            }), 200
        else:
            return jsonify({
                'success': False,
                'message': 'Failed to record attendance in database'
            }), 500
            
    except ValueError as e:
        logger.error(f"❌ Data validation error: {e}")
        return jsonify({
            'success': False,
            'message': f'Invalid data format: {str(e)}'
        }), 400
    except Exception as e:
        logger.error(f"❌ Unexpected error in record_attendance: {e}")
        return jsonify({
            'success': False,
            'message': 'Internal server error'
        }), 500

@app.route('/api/attendance/recent', methods=['GET'])
def get_recent_attendance():
    """API endpoint to get recent attendance records"""
    try:
        limit = request.args.get('limit', 10, type=int)
        if limit > 100:  # Prevent excessive queries
            limit = 100
        
        records = db.get_recent_attendance(limit)
        
        return jsonify({
            'success': True,
            'message': f'Retrieved {len(records)} recent attendance records',
            'data': records
        }), 200
        
    except Exception as e:
        logger.error(f"❌ Error in get_recent_attendance: {e}")
        return jsonify({
            'success': False,
            'message': 'Failed to retrieve attendance records'
        }), 500

@app.route('/api/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    try:
        # Test database connection
        db_status = "connected" if db.connect() else "disconnected"
        
        return jsonify({
            'success': True,
            'message': 'Server is running',
            'database_status': db_status,
            'timestamp': datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        }), 200
        
    except Exception as e:
        logger.error(f"❌ Health check error: {e}")
        return jsonify({
            'success': False,
            'message': 'Server health check failed'
        }), 500

@app.errorhandler(404)
def not_found(error):
    """Handle 404 errors"""
    return jsonify({
        'success': False,
        'message': 'Endpoint not found'
    }), 404

@app.errorhandler(500)
def internal_error(error):
    """Handle 500 errors"""
    logger.error(f"❌ Internal server error: {error}")
    return jsonify({
        'success': False,
        'message': 'Internal server error'
    }), 500

def initialize_server():
    """Initialize server and test database connection"""
    logger.info("🚀 Starting Location-Based Attendance Server")
    logger.info(f"📊 Database: {MYSQL_CONFIG['host']}:{MYSQL_CONFIG['port']}/{MYSQL_CONFIG['database']}")
    
    # Test database connection
    if db.connect():
        logger.info("✅ Database connection test successful")
        db.disconnect()
    else:
        logger.warning("⚠️  Database connection test failed - server will still start")
    
    logger.info("🌐 Server endpoints:")
    logger.info("   POST /api/attendance - Record attendance")
    logger.info("   GET  /api/attendance/recent - Get recent records")
    logger.info("   GET  /api/health - Health check")
    logger.info("-" * 50)

if __name__ == '__main__':
    initialize_server()
    
    # Run Flask server
    app.run(
        host='0.0.0.0',  # Listen on all interfaces
        port=5000,
        debug=False,  # Set to True for development
        threaded=True
    )
