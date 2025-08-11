"use client"

import { useState, useEffect } from 'react'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'
import { Button } from '@/components/ui/button'
import { Badge } from '@/components/ui/badge'
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs'
import { Skeleton } from '@/components/ui/skeleton'
import { Alert, AlertDescription, AlertTitle } from '@/components/ui/alert'
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from '@/components/ui/table'
import { format } from 'date-fns'

interface AttendanceRecord {
  id: number
  student_mac_address: string
  classroom_id: number
  entry_timestamp: string
  created_at: string
}

interface SystemStatus {
  backend: boolean
  database: boolean
  lastUpdate: string
}

export default function AttendanceDashboard() {
  const [attendanceData, setAttendanceData] = useState<AttendanceRecord[]>([])
  const [systemStatus, setSystemStatus] = useState<SystemStatus>({
    backend: false,
    database: false,
    lastUpdate: new Date().toISOString()
  })
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)

  const API_BASE_URL = 'http://localhost:5000'

  const fetchAttendanceData = async () => {
    try {
      setLoading(true)
      const response = await fetch(`${API_BASE_URL}/api/attendance/recent?limit=50`)
      if (!response.ok) throw new Error('Failed to fetch attendance data')
      
      const data = await response.json()
      setAttendanceData(data)
      setError(null)
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to fetch data')
    } finally {
      setLoading(false)
    }
  }

  const checkSystemStatus = async () => {
    try {
      const response = await fetch(`${API_BASE_URL}/api/health`)
      const backendStatus = response.ok
      
      // Simple database check by trying to fetch recent records
      const dbResponse = await fetch(`${API_BASE_URL}/api/attendance/recent?limit=1`)
      const databaseStatus = dbResponse.ok
      
      setSystemStatus({
        backend: backendStatus,
        database: databaseStatus,
        lastUpdate: new Date().toISOString()
      })
    } catch (err) {
      setSystemStatus({
        backend: false,
        database: false,
        lastUpdate: new Date().toISOString()
      })
    }
  }

  useEffect(() => {
    fetchAttendanceData()
    checkSystemStatus()
    
    // Set up polling every 30 seconds
    const interval = setInterval(() => {
      fetchAttendanceData()
      checkSystemStatus()
    }, 30000)
    
    return () => clearInterval(interval)
  }, [])

  const getClassroomName = (classroomId: number) => {
    const classrooms: { [key: number]: string } = {
      101: 'Room A101',
      102: 'Room A102',
      103: 'Room A103',
      201: 'Room B201',
      202: 'Room B202'
    }
    return classrooms[classroomId] || `Room ${classroomId}`
  }

  const getRecentStats = () => {
    const lastHour = attendanceData.filter(record => 
      new Date(record.entry_timestamp) > new Date(Date.now() - 3600000)
    ).length
    
    const uniqueStudents = new Set(attendanceData.map(record => record.student_mac_address)).size
    
    return { lastHour, uniqueStudents, total: attendanceData.length }
  }

  const stats = getRecentStats()

  return (
    <div className="min-h-screen bg-gray-50 p-4 md:p-8">
      <div className="max-w-7xl mx-auto">
        <div className="mb-8">
          <h1 className="text-4xl font-bold text-gray-900 mb-2">Attendance Dashboard</h1>
          <p className="text-gray-600">Real-time BLE-based attendance tracking system</p>
        </div>

        {/* System Status */}
        <Card className="mb-6">
          <CardHeader>
            <CardTitle>System Status</CardTitle>
            <CardDescription>Last updated: {format(new Date(systemStatus.lastUpdate), 'PPpp')}</CardDescription>
          </CardHeader>
          <CardContent>
            <div className="flex gap-4">
              <Badge variant={systemStatus.backend ? "default" : "destructive"}>
                Backend: {systemStatus.backend ? 'Online' : 'Offline'}
              </Badge>
              <Badge variant={systemStatus.database ? "default" : "destructive"}>
                Database: {systemStatus.database ? 'Connected' : 'Disconnected'}
              </Badge>
            </div>
          </CardContent>
        </Card>

        {/* Error Alert */}
        {error && (
          <Alert variant="destructive" className="mb-6">
            <AlertTitle>Error</AlertTitle>
            <AlertDescription>{error}</AlertDescription>
          </Alert>
        )}

        {/* Stats Cards */}
        <div className="grid grid-cols-1 md:grid-cols-3 gap-6 mb-6">
          <Card>
            <CardHeader>
              <CardTitle className="text-2xl">{stats.lastHour}</CardTitle>
              <CardDescription>Attendances (Last Hour)</CardDescription>
            </CardHeader>
          </Card>
          
          <Card>
            <CardHeader>
              <CardTitle className="text-2xl">{stats.uniqueStudents}</CardTitle>
              <CardDescription>Unique Students</CardDescription>
            </CardHeader>
          </Card>
          
          <Card>
            <CardHeader>
              <CardTitle className="text-2xl">{stats.total}</CardTitle>
              <CardDescription>Total Records</CardDescription>
            </CardHeader>
          </Card>
        </div>

        {/* Main Content */}
        <Tabs defaultValue="live" className="space-y-4">
          <TabsList>
            <TabsTrigger value="live">Live Attendance</TabsTrigger>
            <TabsTrigger value="analytics">Analytics</TabsTrigger>
            <TabsTrigger value="settings">Settings</TabsTrigger>
          </TabsList>

          <TabsContent value="live">
            <Card>
              <CardHeader>
                <div className="flex justify-between items-center">
                  <div>
                    <CardTitle>Recent Attendance</CardTitle>
                    <CardDescription>Latest student check-ins</CardDescription>
                  </div>
                  <Button onClick={fetchAttendanceData} disabled={loading}>
                    {loading ? 'Refreshing...' : 'Refresh'}
                  </Button>
                </div>
              </CardHeader>
              <CardContent>
                {loading ? (
                  <div className="space-y-3">
                    {[...Array(5)].map((_, i) => (
                      <div key={i} className="flex space-x-4">
                        <Skeleton className="h-12 w-12 rounded-full" />
                        <div className="space-y-2">
                          <Skeleton className="h-4 w-[250px]" />
                          <Skeleton className="h-4 w-[200px]" />
                        </div>
                      </div>
                    ))}
                  </div>
                ) : attendanceData.length === 0 ? (
                  <p className="text-center text-gray-500 py-8">No attendance records found</p>
                ) : (
                  <Table>
                    <TableHeader>
                      <TableRow>
                        <TableHead>Student MAC</TableHead>
                        <TableHead>Classroom</TableHead>
                        <TableHead>Check-in Time</TableHead>
                      </TableRow>
                    </TableHeader>
                    <TableBody>
                      {attendanceData.map((record) => (
                        <TableRow key={record.id}>
                          <TableCell className="font-mono text-sm">
                            {record.student_mac_address}
                          </TableCell>
                          <TableCell>{getClassroomName(record.classroom_id)}</TableCell>
                          <TableCell>
                            {format(new Date(record.entry_timestamp), 'PPpp')}
                          </TableCell>
                        </TableRow>
                      ))}
                    </TableBody>
                  </Table>
                )}
              </CardContent>
            </Card>
          </TabsContent>

          <TabsContent value="analytics">
            <Card>
              <CardHeader>
                <CardTitle>Analytics Overview</CardTitle>
                <CardDescription>Attendance patterns and insights</CardDescription>
              </CardHeader>
              <CardContent>
                <div className="text-center py-8">
                  <p className="text-gray-500">Analytics dashboard coming soon</p>
                  <p className="text-sm text-gray-400 mt-2">
                    Features: Daily attendance trends, classroom utilization, student patterns
                  </p>
                </div>
              </CardContent>
            </Card>
          </TabsContent>

          <TabsContent value="settings">
            <Card>
              <CardHeader>
                <CardTitle>System Configuration</CardTitle>
                <CardDescription>Manage system settings and connections</CardDescription>
              </CardHeader>
              <CardContent>
                <div className="space-y-4">
                  <div>
                    <h3 className="font-semibold mb-2">Backend Configuration</h3>
                    <p className="text-sm text-gray-600">API Base URL: {API_BASE_URL}</p>
                  </div>
                  <div>
                    <h3 className="font-semibold mb-2">ESP32 Configuration</h3>
                    <p className="text-sm text-gray-600">
                      Ensure ESP32 devices are configured with the correct server URL
                    </p>
                  </div>
                  <div>
                    <h3 className="font-semibold mb-2">Database Status</h3>
                    <p className="text-sm text-gray-600">
                      MySQL database: {systemStatus.database ? 'Connected' : 'Check connection'}
                    </p>
                  </div>
                </div>
              </CardContent>
            </Card>
          </TabsContent>
        </Tabs>
      </div>
    </div>
  )
}
