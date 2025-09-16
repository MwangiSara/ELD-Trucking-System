import { useState, useEffect } from 'react'
import api from '../api'

function ViewTrips({ onSelectTrip }) {
  const [trips, setTrips] = useState([])
  const [loading, setLoading] = useState(true)
  
  useEffect(() => {
    loadTrips()
  }, [])
  
  const loadTrips = async () => {
    try {
      const data = await api.get('/api/trips/')
      setTrips(data.results || data)
    } catch (error) {
      console.error('Error loading trips:', error)
    } finally {
      setLoading(false)
    }
  }
  
  if (loading) return <div className="loading">Loading trips...</div>
  
  return (
    <div>
      <h2 style={{marginBottom: '30px', color: '#333', fontSize: '2em'}}>
        <i className="fas fa-list"></i> All Trips
      </h2>
      
      <div className="trip-list">
        {trips.map(trip => (
          <div key={trip.id} className="trip-card" onClick={() => onSelectTrip(trip)}>
            <div className="trip-header">
              <span className="trip-id">Trip: {trip.id?.substring(0, 8) || 'N/A'}</span>
              <span className="trip-status">
                {trip.drive_time ? 'Completed' : 'In Progress'}
              </span>
            </div>
            <p><strong>Current:</strong> {trip.current_location}</p>
            <p><strong>From:</strong> {trip.pickup_location}</p>
            <p><strong>To:</strong> {trip.dropoff_location}</p>
            <p><strong>Driver:</strong> {trip.driver_name}</p>
            <p><strong>Cycle Hours:</strong> {trip.current_cycle_used}h</p>
            {trip.stops && (
              <p><strong>Stops:</strong> {trip.stops.length}</p>
            )}
          </div>
        ))}
      </div>
      
      {trips.length === 0 && (
        <div style={{textAlign: 'center', padding: '40px', color: '#666'}}>
          No trips found. Create a new trip to get started.
        </div>
      )}
    </div>
  )
}

export default ViewTrips