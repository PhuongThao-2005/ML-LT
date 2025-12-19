import { MapContainer, TileLayer, Marker, Popup, useMap } from 'react-leaflet';
import 'leaflet/dist/leaflet.css';
import { useEffect, useState } from 'react';
import L from 'leaflet';
import type { ItineraryRoute } from '../types';

type LatLng = [number, number];

// Fix default marker icon issue with Leaflet in React
delete (L.Icon.Default.prototype as any)._getIconUrl;
L.Icon.Default.mergeOptions({
  iconRetinaUrl: 'https://cdnjs.cloudflare.com/ajax/libs/leaflet/1.7.1/images/marker-icon-2x.png',
  iconUrl: 'https://cdnjs.cloudflare.com/ajax/libs/leaflet/1.7.1/images/marker-icon.png',
  shadowUrl: 'https://cdnjs.cloudflare.com/ajax/libs/leaflet/1.7.1/images/marker-shadow.png',
});

const MapUpdater = ({ routes }: { routes: ItineraryRoute[] }) => {
  const map = useMap();

  useEffect(() => {
    if (routes.length > 0) {
      const validPositions = routes
        .filter(r => r.latitude && r.longitude)
        .map(r => [r.latitude!, r.longitude!] as LatLng);

      if (validPositions.length > 0) {
        if (validPositions.length === 1) {
          map.setView(validPositions[0], 13);
        } else {
          const bounds = L.latLngBounds(validPositions);
          map.fitBounds(bounds, { padding: [50, 50] });
        }
      }
    }
  }, [routes, map]);

  return null;
};

const POIMarker = ({ poi }: { poi: ItineraryRoute }) => {
  const map = useMap();

  if (!poi.latitude || !poi.longitude) return null;

  const position: LatLng = [poi.latitude, poi.longitude];

  const getMarkerColor = (type: string) => {
    switch (type) {
      case 'Start': return '🏨';
      case 'Visit': return '🎯';
      case 'Lunch': return '🍽️';
      case 'Dinner': return '🍴';
      case 'Return Hotel': return '🏠';
      default: return '📍';
    }
  };

  return (
    <Marker
      position={position}
      eventHandlers={{
        click: () => {
          map.flyTo(position, 15);
        },
      }}
    >
      <Popup>
        <div className="p-2">
          <div className="font-semibold text-lg mb-1">
            {getMarkerColor(poi.type)} {poi.name}
          </div>
          <div className="text-sm text-gray-600 mb-1">
            ⏰ {poi.arrival_time}
          </div>
          {poi.address && (
            <div className="text-sm text-gray-600 mb-1">
              📍 {poi.address}
            </div>
          )}
          {poi.rating && (
            <div className="text-sm">
              ⭐ {poi.rating} / 5.0
            </div>
          )}
        </div>
      </Popup>
    </Marker>
  );
}

interface MapProps {
  routes?: ItineraryRoute[];
  selectedDay?: number;
}

export const Map: React.FC<MapProps> = ({ routes = [] }) => {

  const [center, setCenter] = useState<LatLng>([10.762622, 106.660172]);

  useEffect(() => {
    if (!navigator.geolocation) {
      return;
    }

    navigator.geolocation.getCurrentPosition((position) => {
      setCenter([position.coords.latitude, position.coords.longitude]),
      () => {
        setCenter([10.762622, 106.660172]);
      },
      {
        enableHighAccuracy: true,
        timeout: 5000,
      };
    })
  }, [])
  
  return (
    <div className='w-full h-full z-0'>
      <MapContainer   
        center={center}
        zoom={12}
        style={{ height: '400px', width: '100%' }}
      >
        <TileLayer
          url="https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png"
          attribution='&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors'
        />
        <MapUpdater routes={routes} />
        {routes.map((poi) => (
          <POIMarker key={`${poi.poi_id}`} poi={poi} />
        ))}
      </MapContainer>
    </div>
  )
}