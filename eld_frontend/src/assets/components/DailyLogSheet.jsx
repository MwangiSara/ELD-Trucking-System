import { useState, useEffect } from 'react'
import api from '../api'
import DutyTimeGrid from './DutyTimeGrid'

function DailyLogSheet({ tripId }) {
  const [logs, setLogs] = useState([])
  const [selectedLog, setSelectedLog] = useState(null)
  const [loading, setLoading] = useState(true)
  const [dutyEvents, setDutyEvents] = useState([])
  const [showAddEvent, setShowAddEvent] = useState(false)
  const [newEvent, setNewEvent] = useState({
    duty_event_status: 'off_duty',
    start_time: '',
    end_time: '',
    location: '',
    remarks: '',
    truck_moved: false
  })
  
  useEffect(() => {
    if (tripId) {
      loadDailyLogs()
    }
  }, [tripId])
  
  const loadDailyLogs = async () => {
    try {
      const data = await api.get(`/api/trips/${tripId}/logs/`)
      setLogs(data)
      if (data.length > 0) {
        setSelectedLog(data[0])
        loadDutyEvents(data[0].id)
      }
    } catch (error) {
      console.error('Error loading daily logs:', error)
    } finally {
      setLoading(false)
    }
  }
  
  const loadDutyEvents = async (logId) => {
    try {
      const events = await api.get(`/api/logs/${logId}/events/`)
      setDutyEvents(events)
    } catch (error) {
      console.error('Error loading duty events:', error)
    }
  }
  
  const handleLogSelect = (log) => {
    setSelectedLog(log)
    loadDutyEvents(log.id)
  }
  
  const handleAddEvent = async (e) => {
    e.preventDefault()
    try {
      const eventData = {
        ...newEvent,
        daily_log: selectedLog.id
      }
      await api.post(`/api/logs/${selectedLog.id}/events/`, eventData)
      
      // Reset form
      setNewEvent({
        duty_event_status: 'off_duty',
        start_time: '',
        end_time: '',
        location: '',
        remarks: '',
        truck_moved: false
      })
      setShowAddEvent(false)
      
      // Reload events
      loadDutyEvents(selectedLog.id)
    } catch (error) {
      console.error('Error adding duty event:', error)
      alert('Failed to add duty event: ' + error.message)
    }
  }
  
  const formatTime = (hours) => {
    const h = Math.floor(hours)
    const m = Math.round((hours - h) * 60)
    return `${h}:${m.toString().padStart(2, '0')}`
  }
  
  const formatDateTime = (dateString) => {
    return new Date(dateString).toLocaleString()
  }
  
  if (loading) return <div className="loading">Loading daily logs...</div>
  if (logs.length === 0) return <div className="error">No daily logs found for this trip</div>
  
  return (
    <div>
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '30px' }}>
        <h2 style={{ color: '#333', fontSize: '2em', margin: 0 }}>
          <i className="fas fa-clipboard-list"></i> Daily Log Sheets
        </h2>
        <button 
          className="btn"
          onClick={() => setShowAddEvent(!showAddEvent)}
        >
          <i className="fas fa-plus"></i> Add Duty Event
        </button>
      </div>
      
      <div style={{marginBottom: '20px'}}>
        <label>Select Log Date: </label>
        <select 
          onChange={(e) => handleLogSelect(logs[e.target.value])}
          style={{marginLeft: '10px', padding: '8px', borderRadius: '5px', border: '1px solid #ddd'}}
        >
          {logs.map((log, index) => (
            <option key={log.id} value={index}>
              {new Date(log.date).toLocaleDateString()} - {log.driver_name}
            </option>
          ))}
        </select>
      </div>
      
      {showAddEvent && (
        <div className="add-event-form">
          <h4>Add New Duty Event</h4>
          <form onSubmit={handleAddEvent}>
            <div className="form-grid">
              <div className="form-group">
                <label>Duty Status</label>
                <select
                  value={newEvent.duty_event_status}
                  onChange={(e) => setNewEvent({...newEvent, duty_event_status: e.target.value})}
                  required
                >
                  <option value="off_duty">Off Duty</option>
                  <option value="sleeper_berth">Sleeper Berth</option>
                  <option value="driving">Driving</option>
                  <option value="on_duty">On Duty</option>
                </select>
              </div>
              
              <div className="form-group">
                <label>Start Time</label>
                <input
                  type="datetime-local"
                  value={newEvent.start_time}
                  onChange={(e) => setNewEvent({...newEvent, start_time: e.target.value})}
                  required
                />
              </div>
              
              <div className="form-group">
                <label>End Time</label>
                <input
                  type="datetime-local"
                  value={newEvent.end_time}
                  onChange={(e) => setNewEvent({...newEvent, end_time: e.target.value})}
                />
              </div>
              
              <div className="form-group">
                <label>Location</label>
                <input
                  type="text"
                  value={newEvent.location}
                  onChange={(e) => setNewEvent({...newEvent, location: e.target.value})}
                  placeholder="e.g., Denver, CO"
                  required
                />
              </div>
              
              <div className="form-group">
                <label>Remarks</label>
                <input
                  type="text"
                  value={newEvent.remarks}
                  onChange={(e) => setNewEvent({...newEvent, remarks: e.target.value})}
                  placeholder="Optional remarks"
                />
              </div>
              
              <div className="form-group">
                <label>
                  <input
                    type="checkbox"
                    checked={newEvent.truck_moved}
                    onChange={(e) => setNewEvent({...newEvent, truck_moved: e.target.checked})}
                    style={{ marginRight: '8px' }}
                  />
                  Truck Moved
                </label>
              </div>
            </div>
            
            <div>
              <button type="submit" className="btn">Add Event</button>
              <button 
                type="button" 
                className="btn btn-secondary" 
                onClick={() => setShowAddEvent(false)}
              >
                Cancel
              </button>
            </div>
          </form>
        </div>
      )}
      
      {selectedLog && (
        <div className="log-sheet">
          <div className="log-header">
            <div>
              <div className="log-field">
                <label>Date:</label>
                <input type="text" value={new Date(selectedLog.date).toLocaleDateString()} readOnly />
              </div>
              <div className="log-field">
                <label>Driver:</label>
                <input type="text" value={selectedLog.driver_name} readOnly />
              </div>
              <div className="log-field">
                <label>Vehicle:</label>
                <input type="text" value={selectedLog.vehicle_number} readOnly />
              </div>
              <div className="log-field">
                <label>Trailer:</label>
                <input type="text" value={selectedLog.trailer_number} readOnly />
              </div>
            </div>
            <div>
              <div className="log-field">
                <label>Total Miles:</label>
                <input type="text" value={selectedLog.total_driving_miles} readOnly />
              </div>
              <div className="log-field">
                <label>Shipper:</label>
                <input type="text" value={selectedLog.shipper_name || 'N/A'} readOnly />
              </div>
              <div className="log-field">
                <label>Load #:</label>
                <input type="text" value={selectedLog.load_number || 'N/A'} readOnly />
              </div>
              <div className="log-field">
                <label>Commodity:</label>
                <input type="text" value={selectedLog.shipper_commodity || 'N/A'} readOnly />
              </div>
            </div>
          </div>
          
          <div className="time-labels">
            <div></div>
            {Array.from({length: 24}, (_, i) => (
              <div key={i}>{i}</div>
            ))}
          </div>
          
          <div className="duty-grid">
            <div className="duty-label">1. Off Duty</div>
            <DutyTimeGrid 
              dutyType="off_duty" 
              events={dutyEvents}
              totalMinutes={selectedLog.total_off_duty_time}
            />
          </div>
          
          <div className="duty-grid">
            <div className="duty-label">2. Sleeper Berth</div>
            <DutyTimeGrid 
              dutyType="sleeper_berth" 
              events={dutyEvents}
              totalMinutes={selectedLog.total_sleeper_berth_time}
            />
          </div>
          
          <div className="duty-grid">
            <div className="duty-label">3. Driving</div>
            <DutyTimeGrid 
              dutyType="driving" 
              events={dutyEvents}
              totalMinutes={selectedLog.total_driving_time}
            />
          </div>
          
          <div className="duty-grid">
            <div className="duty-label">4. On Duty</div>
            <DutyTimeGrid 
              dutyType="on_duty" 
              events={dutyEvents}
              totalMinutes={selectedLog.total_on_duty_time}
            />
          </div>
          
          <div className="legend">
            <div className="legend-item">
              <div className="legend-color" style={{backgroundColor: '#ffeb3b'}}></div>
              <span>Off Duty</span>
            </div>
            <div className="legend-item">
              <div className="legend-color" style={{backgroundColor: '#2196f3'}}></div>
              <span>Sleeper Berth</span>
            </div>
            <div className="legend-item">
              <div className="legend-color" style={{backgroundColor: '#4caf50'}}></div>
              <span>Driving</span>
            </div>
            <div className="legend-item">
              <div className="legend-color" style={{backgroundColor: '#ff5722'}}></div>
              <span>On Duty</span>
            </div>
          </div>
          
          <div style={{display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(150px, 1fr))', gap: '15px', margin: '20px 0'}}>
            <div>
              <strong>Total Off Duty:</strong> {formatTime(selectedLog.total_off_duty_time / 60)}
            </div>
            <div>
              <strong>Total Sleeper:</strong> {formatTime(selectedLog.total_sleeper_berth_time / 60)}
            </div>
            <div>
              <strong>Total Driving:</strong> {formatTime(selectedLog.total_driving_time / 60)}
            </div>
            <div>
              <strong>Total On Duty:</strong> {formatTime(selectedLog.total_on_duty_time / 60)}
            </div>
          </div>
          
          {dutyEvents && dutyEvents.length > 0 && (
            <div className="duty-events-section">
              <h4>Duty Events</h4>
              <div className="duty-events-list">
                {dutyEvents.map((event, index) => (
                  <div key={index} className="duty-event-item">
                    <div className="event-header">
                      <strong>{event.duty_event_status.replace('_', ' ').toUpperCase()}</strong>
                      <span className={`event-status ${event.truck_moved ? 'moved' : 'stationary'}`}>
                        {event.truck_moved ? 'Vehicle Moved' : 'Stationary'}
                      </span>
                    </div>
                    <div className="event-details">
                      <div>Start: {formatDateTime(event.start_time)}</div>
                      {event.end_time && <div>End: {formatDateTime(event.end_time)}</div>}
                      <div>Location: {event.location}</div>
                      {event.remarks && <div>Remarks: {event.remarks}</div>}
                    </div>
                  </div>
                ))}
              </div>
            </div>
          )}
          
          <div className="remarks-section">
            <h4>Driver Remarks</h4>
            <textarea 
              placeholder="Enter any remarks, violations, or special circumstances..."
              defaultValue={dutyEvents.map(event => `${event.duty_event_status}: ${event.remarks || event.location}`).join('\n')}
            />
          </div>
        </div>
      )}
    </div>
  )
}

export default DailyLogSheet