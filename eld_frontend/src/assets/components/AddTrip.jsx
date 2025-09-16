import { useState } from 'react'
import api from '../api'

function AddTrip({ onTripAdded }) {
  const [formData, setFormData] = useState({
    current_location: '',
    pickup_location: '',
    dropoff_location: '',
    current_cycle_used: 0
  })
  const [loading, setLoading] = useState(false)
  const [message, setMessage] = useState('')
  
  const handleSubmit = async (e) => {
    e.preventDefault()
    setLoading(true)
    setMessage('')
    
    try {
      const newTrip = await api.post('/api/trips/', formData)
      setMessage('Trip created successfully!')
      setFormData({
        current_location: '',
        pickup_location: '',
        dropoff_location: '',
        current_cycle_used: 0
      })
      if (onTripAdded) onTripAdded(newTrip)
    } catch (error) {
      setMessage('Error creating trip: ' + error.message)
    } finally {
      setLoading(false)
    }
  }
  
  const handleChange = (e) => {
    setFormData({
      ...formData,
      [e.target.name]: e.target.value
    })
  }
  
  return (
    <div>
      <h2 style={{marginBottom: '30px', color: '#333', fontSize: '2em'}}>
        <i className="fas fa-plus-circle"></i> Add New Trip
      </h2>
      
      {message && (
        <div className={message.includes('Error') ? 'error' : 'success'}>
          {message}
        </div>
      )}
      
      <form onSubmit={handleSubmit}>
        <div className="form-grid">
          <div className="form-group">
            <label>Current Location</label>
            <input
              type="text"
              name="current_location"
              value={formData.current_location}
              onChange={handleChange}
              required
              placeholder="e.g., Denver, CO"
            />
          </div>
          
          <div className="form-group">
            <label>Pickup Location</label>
            <input
              type="text"
              name="pickup_location"
              value={formData.pickup_location}
              onChange={handleChange}
              required
              placeholder="e.g., Chicago, IL"
            />
          </div>
          
          <div className="form-group">
            <label>Dropoff Location</label>
            <input
              type="text"
              name="dropoff_location"
              value={formData.dropoff_location}
              onChange={handleChange}
              required
              placeholder="e.g., Atlanta, GA"
            />
          </div>
          
          <div className="form-group">
            <label>Current Cycle Hours Used</label>
            <input
              type="number"
              name="current_cycle_used"
              value={formData.current_cycle_used}
              onChange={handleChange}
              min="0"
              max="70"
              step="0.1"
              required
            />
          </div>
        </div>
        
        <button type="submit" className="btn" disabled={loading}>
          {loading ? 'Creating Trip...' : 'Create Trip'}
        </button>
      </form>
    </div>
  )
}

export default AddTrip