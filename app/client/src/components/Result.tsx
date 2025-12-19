import type { POIResponse, ItineraryRoute } from "../types";
import { Map } from "./Map";
import { Timeline } from "./Timeline";
import { useState } from "react";


interface ResultProps {
  result: POIResponse;
}

export const Result: React.FC<ResultProps> = ({ 
  result
}) => {
  const [selectedDay, setSelectedDay] = useState<number | null>(null);
  const [selectedRoutes, setSelectedRoutes] = useState<ItineraryRoute[]>([]);

  const handleDaySelect = (day: number, routes: ItineraryRoute[]) => {
    setSelectedDay(day);
    setSelectedRoutes(routes);
  };

  return (
    <div className="max-w-5xl mx-auto flex justify-center mt-25 z-0 ">
      <Timeline onDaySelect={handleDaySelect} result={result} />
      <Map routes={selectedRoutes} selectedDay={selectedDay ?? undefined} />
    </div>
  )
}