import { useState, useEffect } from 'react'

function DutyTimeGrid({ dutyType, events, totalMinutes }) {
  const [timeSlots, setTimeSlots] = useState(Array(24).fill(false))
  
  useEffect(() => {
    const slots = Array(24).fill(false)
    events.forEach(event => {
      if (event.duty_event_status === dutyType) {
        const startHour = new Date(event.start_time).getHours()
        const endHour = event.end_time ? new Date(event.end_time).getHours() : startHour + 1
        for (let i = startHour; i < endHour && i < 24; i++) {
          slots[i] = true
        }
      }
    })
    setTimeSlots(slots)
  }, [events, dutyType])
  
  const toggleTimeSlot = (index) => {
    const newSlots = [...timeSlots]
    newSlots[index] = !newSlots[index]
    setTimeSlots(newSlots)
  }
  
  const getSlotClass = (active) => {
    const baseClass = 'time-slot'
    if (!active) return baseClass
    
    switch (dutyType) {
      case 'off_duty': return `${baseClass} off-duty`
      case 'sleeper_berth': return `${baseClass} sleeper-berth`
      case 'driving': return `${baseClass} driving`
      case 'on_duty': return `${baseClass} on-duty`
      default: return baseClass
    }
  }
  
  return (
    <div className="time-grid">
      {timeSlots.map((active, index) => (
        <div
          key={index}
          className={getSlotClass(active)}
          onClick={() => toggleTimeSlot(index)}
          title={`Hour ${index}: ${active ? 'Active' : 'Inactive'}`}
        />
      ))}
    </div>
  )
}

export default DutyTimeGrid