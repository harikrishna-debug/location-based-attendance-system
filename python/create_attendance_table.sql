-- Location-Based Attendance System Database Schema
-- MySQL Database Setup for storing BLE beacon attendance records

-- Create database (optional - run if database doesn't exist)
-- CREATE DATABASE IF NOT EXISTS attendance_system;
-- USE attendance_system;

-- Create attendance table
CREATE TABLE IF NOT EXISTS attendance (
    id INT AUTO_INCREMENT PRIMARY KEY,
    student_mac_address VARCHAR(255) NOT NULL,
    classroom_id INT NOT NULL,
    entry_timestamp DATETIME NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    INDEX idx_student_mac (student_mac_address),
    INDEX idx_classroom_id (classroom_id),
    INDEX idx_entry_timestamp (entry_timestamp),
    INDEX idx_created_at (created_at)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- Create a view for easy attendance reporting
CREATE OR REPLACE VIEW attendance_summary AS
SELECT 
    student_mac_address,
    classroom_id,
    entry_timestamp,
    DATE(entry_timestamp) as attendance_date,
    TIME(entry_timestamp) as attendance_time,
    created_at
FROM attendance
ORDER BY entry_timestamp DESC;

-- Create a view for daily attendance counts by classroom
CREATE OR REPLACE VIEW daily_attendance_counts AS
SELECT 
    classroom_id,
    DATE(entry_timestamp) as attendance_date,
    COUNT(DISTINCT student_mac_address) as unique_students,
    COUNT(*) as total_entries
FROM attendance
GROUP BY classroom_id, DATE(entry_timestamp)
ORDER BY attendance_date DESC, classroom_id;

-- Insert sample data for testing (optional)
-- INSERT INTO attendance (student_mac_address, classroom_id, entry_timestamp) VALUES
-- ('AA:BB:CC:DD:EE:01', 101, '2024-01-15 09:00:00'),
-- ('AA:BB:CC:DD:EE:02', 101, '2024-01-15 09:01:00'),
-- ('AA:BB:CC:DD:EE:03', 102, '2024-01-15 09:02:00'),
-- ('AA:BB:CC:DD:EE:04', 101, '2024-01-15 09:03:00'),
-- ('AA:BB:CC:DD:EE:05', 102, '2024-01-15 09:04:00');

-- Show table structure
DESCRIBE attendance;

-- Show indexes
SHOW INDEX FROM attendance;

-- Display sample queries for testing
-- SELECT 'Sample Queries for Testing:' as info;
-- SELECT '1. Get all attendance records:' as query;
-- SELECT * FROM attendance ORDER BY entry_timestamp DESC LIMIT 10;

-- SELECT '2. Get attendance by classroom:' as query;
-- SELECT * FROM attendance WHERE classroom_id = 101 ORDER BY entry_timestamp DESC;

-- SELECT '3. Get attendance for specific date:' as query;
-- SELECT * FROM attendance WHERE DATE(entry_timestamp) = CURDATE() ORDER BY entry_timestamp DESC;

-- SELECT '4. Get unique students per classroom today:' as query;
-- SELECT classroom_id, COUNT(DISTINCT student_mac_address) as unique_students 
-- FROM attendance 
-- WHERE DATE(entry_timestamp) = CURDATE() 
-- GROUP BY classroom_id;

-- SELECT '5. Get attendance summary view:' as query;
-- SELECT * FROM attendance_summary LIMIT 10;

-- SELECT '6. Get daily attendance counts:' as query;
-- SELECT * FROM daily_attendance_counts LIMIT 10;
