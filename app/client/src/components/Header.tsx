import type { POIResponse } from "../types";

interface HeaderProps {
  setResult: (result: POIResponse) => void;
}

export const Header: React.FC<HeaderProps> = ({ setResult }) => {

  return (
    <div className="h-18 bg-transparent">
      <div 
        className="max-w-5xl mx-auto h-full flex items-center text-white font-bold text-2xl cursor-pointer"
        onClick={() => setResult(null!)}  
      >
        Tour Planner
      </div>
    </div>
  )
}
