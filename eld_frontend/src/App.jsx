import { useState, useEffect } from 'react'
import Dashboard from './assets/components/Dashboard'
import AddTrip from './assets/components/AddTrip'
import ViewTrips from './assets/components/ViewTrips'
import TripDetailView from './assets/components/TripDetailView'
import './App.css'

function App() {
  const [activeTab, setActiveTab] = useState('dashboard')
  const [selectedTrip, setSelectedTrip] = useState(null)
  
  const handleTripAdded = (newTrip) => {
    setActiveTab('trips')
  }
  
  const handleSelectTrip = (trip) => {
    setSelectedTrip(trip)
    setActiveTab('trip-detail')
  }
  
  const handleBackToTrips = () => {
    setSelectedTrip(null)
    setActiveTab('trips')
  }
  
  return (
    <div className="app">
      <div className="header">
        <h1><i className="fas fa-truck-moving"></i> ELD Trucking System</h1>
        <div className="nav-tabs">
          <button 
            className={`nav-tab ${activeTab === 'dashboard' ? 'active' : ''}`}
            onClick={() => setActiveTab('dashboard')}
          >
            <i className="fas fa-tachometer-alt"></i> Dashboard
          </button>
          <button 
            className={`nav-tab ${activeTab === 'add-trip' ? 'active' : ''}`}
            onClick={() => setActiveTab('add-trip')}
          >
            <i className="fas fa-plus"></i> Add Trip
          </button>
          <button 
            className={`nav-tab ${activeTab === 'trips' ? 'active' : ''}`}
            onClick={() => setActiveTab('trips')}
          >
            <i className="fas fa-list"></i> View Trips
          </button>
        </div>
      </div>
      
      <div className="content">
        {activeTab === 'dashboard' && <Dashboard />}
        {activeTab === 'add-trip' && <AddTrip onTripAdded={handleTripAdded} />}
        {activeTab === 'trips' && <ViewTrips onSelectTrip={handleSelectTrip} />}
        {activeTab === 'trip-detail' && (
          <TripDetailView trip={selectedTrip} onBack={handleBackToTrips} />
        )}
      </div>
    </div>
  )
}

export default App