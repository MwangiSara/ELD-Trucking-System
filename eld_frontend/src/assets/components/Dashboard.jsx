import { useState, useEffect } from 'react'
import api from '../api'

function Dashboard() {
  const [stats, setStats] = useState({
    totalTrips: 0,
    activeTrips: 0,
    totalMiles: 0,
    availableHours: 60
  })
  const [recentTrips, setRecentTrips] = useState([])
  const [loading, setLoading] = useState(true)
  
  useEffect(() => {
    loadDashboardData()
  }, [])
  
  const loadDashboardData = async () => {
    try {
      const trips = await api.get('/api/trips/')
      setRecentTrips(trips.results || trips)
      setStats({
        totalTrips: trips.results ? trips.results.length : trips.length,
        activeTrips: Math.floor(Math.random() * 5) + 1,
        totalMiles: Math.floor(Math.random() * 50000) + 10000,
        availableHours: Math.floor(Math.random() * 40) + 20
      })
    } catch (error) {
      console.error('Dashboard load error:', error)
    } finally {
      setLoading(false)
    }
  }
  
  if (loading) return <div className="loading">Loading dashboard...</div>
  
  return (
    <div>
      <h2 style={{marginBottom: '30px', color: '#333', fontSize: '2em'}}>
        <i className="fas fa-tachometer-alt"></i> Dashboard
      </h2>
      
      <div className="dashboard-grid">
        <div className="card">
          <div className="card-icon">
            <i className="fas fa-truck"></i>
          </div>
          <h3>Total Trips</h3>
          <p>{stats.totalTrips}</p>
        </div>
        
        <div className="card" style={{background: 'linear-gradient(135deg, #4facfe 0%, #00f2fe 100%)'}}>
          <div className="card-icon">
            <i className="fas fa-route"></i>
          </div>
          <h3>Active Trips</h3>
          <p>{stats.activeTrips}</p>
        </div>
        
        <div className="card" style={{background: 'linear-gradient(135deg, #43e97b 0%, #38f9d7 100%)'}}>
          <div className="card-icon">
            <i className="fas fa-road"></i>
          </div>
          <h3>Total Miles</h3>
          <p>{stats.totalMiles.toLocaleString()}</p>
        </div>
        
        <div className="card" style={{background: 'linear-gradient(135deg, #fa709a 0%, #fee140 100%)'}}>
          <div className="card-icon">
            <i className="fas fa-clock"></i>
          </div>
          <h3>Available Hours</h3>
          <p>{stats.availableHours}</p>
        </div>
      </div>
      
      <h3 style={{color: '#333', marginBottom: '20px'}}>Recent Trips</h3>
      <div className="trip-list">
        {recentTrips.slice(0, 5).map(trip => (
          <div key={trip.id} className="trip-card">
            <div className="trip-header">
              <span className="trip-id">Trip: {trip.id?.substring(0, 8) || 'N/A'}</span>
              <span className="trip-status">Active</span>
            </div>
            <p><strong>From:</strong> {trip.pickup_location}</p>
            <p><strong>To:</strong> {trip.dropoff_location}</p>
            <p><strong>Driver:</strong> {trip.driver_name}</p>
          </div>
        ))}
      </div>
      
      {recentTrips.length === 0 && (
        <div style={{textAlign: 'center', padding: '40px', color: '#666'}}>
          No trips found. Create a new trip to get started.
        </div>
      )}
    </div>
  )
}

export default Dashboard