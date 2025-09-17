import { useState, useEffect } from 'react'
import { MapContainer, TileLayer, Polyline, Marker, Popup } from 'react-leaflet'
import api from './api'

// Simple RouteMap component using your provided code
function RouteMap({ route }) {
  if (!route || !route.geometry) return <p>No route available</p>

  // ORS geometry is GeoJSON LineString → convert to [lat, lng] pairs
  const coords = route.geometry.coordinates.map(([lng, lat]) => [lat, lng])

  return (
    <MapContainer center={coords[0]} zoom={6} style={{ height: "400px", width: "100%" }}>
      {/* Base map */}
      <TileLayer
        url="https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png"
        attribution="&copy; OpenStreetMap contributors"
      />

      {/* Route polyline */}
      <Polyline positions={coords} color="blue" weight={4} />

      {/* Start marker */}
      <Marker position={coords[0]}>
        <Popup>Pickup: {route.pickup_location}</Popup>
      </Marker>

      {/* End marker */}
      <Marker position={coords[coords.length - 1]}>
        <Popup>Dropoff: {route.dropoff_location}</Popup>
      </Marker>
    </MapContainer>
  )
}

// RouteMapView component that fetches data and displays the map
function RouteMapView({ tripId }) {
  const [routeData, setRouteData] = useState(null)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState(null)
  
  useEffect(() => {
    if (tripId) {
      loadRouteData()
    }
  }, [tripId])
  
  const loadRouteData = async () => {
    try {
      setLoading(true)
      const data = await api.get(`/api/trips/${tripId}/route/`)
      setRouteData(data)
      setError(null)
    } catch (error) {
      console.error('Error loading route data:', error)
      setError('Failed to load route data: ' + error.message)
    } finally {
      setLoading(false)
    }
  }
  
  if (loading) return <div className="loading">Loading route map...</div>
  if (error) return <div className="error">{error}</div>
  if (!routeData) return <div className="error">No route data available</div>
  
  return (
    <div>
      <h3 style={{color: '#333', marginBottom: '20px'}}>
        <i className="fas fa-map"></i> Route Map
      </h3>
      
      <div className="map-container">
        <RouteMap route={routeData} />
      </div>
      
      <div style={{
        marginTop: '20px', 
        display: 'grid', 
        gridTemplateColumns: 'repeat(auto-fit, minmax(200px, 1fr))', 
        gap: '15px'
      }}>
        <div className="route-info-card">
          <i className="fas fa-road"></i>
          <div>
            <strong>Distance</strong>
            <div>{routeData.summary?.distance_miles || 'N/A'} miles</div>
          </div>
        </div>
        
        <div className="route-info-card">
          <i className="fas fa-clock"></i>
          <div>
            <strong>Duration</strong>
            <div>{routeData.summary?.duration_hours || 'N/A'} hours</div>
          </div>
        </div>
        
        <div className="route-info-card">
          <i className="fas fa-map-marker-alt"></i>
          <div>
            <strong>Stops</strong>
            <div>{routeData.stops?.length || 0} planned</div>
          </div>
        </div>
        
        <div className="route-info-card">
          <i className="fas fa-route"></i>
          <div>
            <strong>Status</strong>
            <div>Active</div>
          </div>
        </div>
      </div>
      
      {routeData.stops && routeData.stops.length > 0 && (
        <div className="stops-section">
          <h4 style={{color: '#333', marginBottom: '15px', marginTop: '30px'}}>
            <i className="fas fa-list"></i> Planned Stops
          </h4>
          <div className="stops-timeline">
            {routeData.stops.map((stop, index) => (
              <div key={index} className="stop-timeline-item">
                <div className="stop-timeline-marker">
                  <i className={getStopIcon(stop.stop_type)}></i>
                </div>
                <div className="stop-timeline-content">
                  <div className="stop-header">
                    <strong>{stop.stop_type.replace('_', ' ').toUpperCase()}</strong>
                    <span className="stop-duration">{stop.duration}h</span>
                  </div>
                  <div className="stop-location">{stop.location}</div>
                  <div className="stop-times">
                    <small>
                      Arrival: {new Date(stop.arrival_time).toLocaleString()}
                      {stop.departure_time && (
                        <> | Departure: {new Date(stop.departure_time).toLocaleString()}</>
                      )}
                    </small>
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

// Helper function to get appropriate icon for stop type
function getStopIcon(stopType) {
  const icons = {
    pretrip: 'fas fa-clipboard-check',
    posttrip: 'fas fa-clipboard-check',
    fuel: 'fas fa-gas-pump',
    rest: 'fas fa-bed',
    pickup: 'fas fa-box',
    dropoff: 'fas fa-shipping-fast',
    loading: 'fas fa-truck-loading',
    offloading: 'fas fa-truck-ramp'
  }
  return icons[stopType] || 'fas fa-map-marker-alt'
}

export default RouteMapView
export { RouteMap }