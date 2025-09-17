import { useState } from 'react'
import RouteMap from '../RouteMap'
import DailyLogSheet from './DailyLogSheet'

function TripDetailView({ trip, onBack }) {
  const [activeTab, setActiveTab] = useState('overview')
  
  if (!trip) return null
  
  return (
    <div>
      <div style={{display: 'flex', alignItems: 'center', marginBottom: '20px', gap: '15px'}}>
        <button className="btn btn-secondary" onClick={onBack}>
          <i className="fas fa-arrow-left"></i> Back to Trips
        </button>
        <h2 style={{color: '#333', margin: 0}}>
          Trip Details: {trip.id?.substring(0, 8) || 'N/A'}
        </h2>
      </div>
      
      <div className="nav-tabs" >
        <button 
          className={`nav-tab2 ${activeTab === 'overview' ? 'active' : ''}`}
          onClick={() => setActiveTab('overview')}
        >
          <i className="fas fa-info-circle"></i> Overview
        </button>
        <button 
          className={`nav-tab2 ${activeTab === 'route' ? 'active' : ''}`}
          onClick={() => setActiveTab('route')}
        >
          <i className="fas fa-map"></i> Route & Map
        </button>
        <button 
          className={`nav-tab2 ${activeTab === 'logs' ? 'active' : ''}`}
          onClick={() => setActiveTab('logs')}
        >
          <i className="fas fa-clipboard-list"></i> Daily Logs
        </button>
      </div>
      <br />
      <div className="content" style={{padding: '20px', background: '#ebedf0ff'}}>
        {activeTab === 'overview' && (
          <TripOverview className="" trip={trip} />
        )}
        
        {activeTab === 'route' && (
          <RouteMap tripId={trip.id} />
        )}
        
        {activeTab === 'logs' && (
          <DailyLogSheet tripId={trip.id} />
        )}
      </div>
    </div>
  )
}

// Trip Overview Component
function TripOverview({ trip }) {
  return (
    <div>
      <h3 style={{color: '#333', marginBottom: '20px'}}>
        <i className="fas fa-truck"></i> Trip Overview
      </h3>
      
      <div className="form-grid">
        <div className="info-card">
          <strong>Trip ID:</strong> 
          <span>{trip.id}</span>
        </div>
        <div className="info-card">
          <strong>Driver:</strong> 
          <span>{trip.driver_name}</span>
        </div>
        <div className="info-card">
          <strong>Current Location:</strong> 
          <span>{trip.current_location}</span>
        </div>
        <div className="info-card">
          <strong>Pickup Location:</strong> 
          <span>{trip.pickup_location}</span>
        </div>
        <div className="info-card">
          <strong>Dropoff Location:</strong> 
          <span>{trip.dropoff_location}</span>
        </div>
        <div className="info-card">
          <strong>Cycle Hours Used:</strong> 
          <span>{trip.current_cycle_used}h</span>
        </div>
        {trip.drive_time && (
          <div className="info-card">
            <strong>Drive Time:</strong> 
            <span>{trip.drive_time}h</span>
          </div>
        )}
      </div>
      
      {trip.stops && trip.stops.length > 0 && (
        <div style={{marginTop: '30px'}}>
          <h4 style={{color: '#333', marginBottom: '15px'}}>
            <i className="fas fa-map-marker-alt"></i> Planned Stops
          </h4>
          <div className="stops-list">
            {trip.stops.map((stop, index) => (
              <div key={index} className="stop-item">
                <div style={{display: 'flex', justifyContent: 'space-between', alignItems: 'center'}}>
                  <div>
                    <strong>{stop.stop_type.replace('_', ' ').toUpperCase()}</strong>
                    <br />
                    <span>{stop.location}</span>
                  </div>
                  <div style={{textAlign: 'right', fontSize: '0.9em', color: '#666'}}>
                    <div>Duration: {stop.duration}h</div>
                    {stop.arrival_time && (
                      <div>Arrival: {new Date(stop.arrival_time).toLocaleString()}</div>
                    )}
                  </div>
                </div>
              </div>
            ))}
          </div>
        </div>
      )}
      
      {trip.daily_logs && trip.daily_logs.length > 0 && (
        <div style={{marginTop: '30px'}}>
          <h4 style={{color: '#333', marginBottom: '15px'}}>
            <i className="fas fa-calendar-alt"></i> Daily Log Summary
          </h4>
          <div style={{display: 'grid', gap: '10px'}}>
            {trip.daily_logs.map((log, index) => (
              <div key={index} className="log-summary-card">
                <div style={{display: 'flex', justifyContent: 'space-between', alignItems: 'center'}}>
                  <div>
                    <strong>Date: {new Date(log.date).toLocaleDateString()}</strong>
                    <br />
                    <small>Miles: {log.total_driving_miles}</small>
                  </div>
                  <div style={{textAlign: 'right', fontSize: '0.9em'}}>
                    <div>Driving: {(log.total_driving_time / 60).toFixed(1)}h</div>
                    <div>On Duty: {(log.total_on_duty_time / 60).toFixed(1)}h</div>
                  </div>
                </div>
              </div>
            ))}
          </div>
        </div>
      )}
    </div>
  )
}

export default TripDetailView