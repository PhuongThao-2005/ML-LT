export interface ItineraryRoute {
  type: string;
  name: string;
  arrival_time: string;
  travel_before_min: number;
  order: number;
  poi_id: string;
  duration_min: number;
  longitude?: number;
  latitude?: number;
  address?: string;
  rating?: number;
}

export interface ItineraryItem {
  day: number;
  route: ItineraryRoute[];
}

export interface POIResponse {
  tour_id: number;
  city: string;
  days: number;
  itinerary: ItineraryItem[];
  start_point?: string;
}