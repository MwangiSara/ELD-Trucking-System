import React, { useEffect, useState } from "react";

function TripDetailView({ trip, onBack }) {
  const [logs, setLogs] = useState([]);
  const [events, setEvents] = useState([]);

  useEffect(() => {
    if (!trip) return;

    // fetch daily logs
    const fetchLogs = async () => {
      try {
        const res = await fetch(
          `http://localhost:8000/api/trips/${trip.id}/logs/`
        );
        const data = await res.json();
        setLogs(data.results || data);

        // if logs exist, fetch duty events of first log
        if (data.length > 0) {
          const firstLog = data[0];
          const resEvents = await fetch(
            `http://localhost:8000/api/logs/${firstLog.id}/events/`
          );
          const eventsData = await resEvents.json();
          setEvents(eventsData);
        }
      } catch (error) {
        console.error("Error fetching trip details:", error);
      }
    };

    fetchLogs();
  }, [trip]);

  if (!trip) {
    return <p>Select a trip to view details.</p>;
  }

  return (
    <div className="trip-detail">
      <button onClick={onBack}>← Back to Trips</button>
      <h2>Trip Details</h2>
      <p>
        {trip.current_location} → {trip.pickup_location} →{" "}
        {trip.dropoff_location}
      </p>

      <h3>Daily Logs</h3>
      <ul>
        {logs.map((log) => (
          <li key={log.id}>
            {log.date} | Driving: {log.total_driving_time} hrs | Miles:{" "}
            {log.total_driving_miles}
          </li>
        ))}
      </ul>

      <h3>Duty Events (First Log)</h3>
      <ul>
        {events.map((event, i) => (
          <li key={i}>
            {event.duty_event_status} | {event.start_time} → {event.end_time} |{" "}
            {event.location}
          </li>
        ))}
      </ul>
    </div>
  );
}

export default TripDetailView;
