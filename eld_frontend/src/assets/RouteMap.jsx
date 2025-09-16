import { MapContainer, TileLayer, Polyline, Marker, Popup } from "react-leaflet";

function RouteMap({ route }) {
  if (!route || !route.geometry) return <p>No route available</p>;

  // ORS geometry is GeoJSON LineString → convert to [lat, lng] pairs
  const coords = route.geometry.coordinates.map(([lng, lat]) => [lat, lng]);

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
  );
}

export default RouteMap;
