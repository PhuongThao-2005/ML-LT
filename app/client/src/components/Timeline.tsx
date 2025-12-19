import { useEffect, useState } from "react";
import { IoClose } from "react-icons/io5";
import type { ItineraryRoute, POIResponse } from "../types";

interface TimelineProps {
  onDaySelect?: (day: number, routes: ItineraryRoute[]) => void;
  result: POIResponse;
}

const Details = ({
  route,
  onClose,
  day
}: {
  route: ItineraryRoute[],
  onClose: () => void,
  day: number
}) => {
  const [expanded, setExpanded] = useState<boolean>(false);
  const [current, setCurrent] = useState<number | null>(null);

  const handleExpand = (item: ItineraryRoute) => {
    if (current === item.order) {
      setCurrent(null);
      setExpanded(!expanded);
    } else {
      setCurrent(item.order);
      setExpanded(true);
    }
  }

  const type = (itemType: string) => {
    switch (itemType) {
      case "Start":
        return "Điểm xuất phát";
      case "Lunch":
        return "Bữa trưa";
      case "Dinner":
        return "Bữa tối";
      case "Visit":
        return "Tham quan";
      case "End":
        return "Về khách sạn";
      default:
        return "Hoạt động";
    }
  }

  return (
    <>
      <div 
        className="fixed inset-0 bg-black/50 z-40"
        onClick={onClose}
      />
      
      <div className="fixed top-1/2 left-1/2 transform -translate-x-1/2 -translate-y-1/2 bg-white border shadow-lg p-6 rounded-lg z-50 max-w-2xl w-full max-h-[80vh] overflow-y-auto">
        <div className="flex justify-between items-center mb-4 border-b pb-3">
          <h2 className="text-xl font-semibold">Chi tiết Ngày {day}</h2>
          <button
            onClick={onClose}
            className="text-gray-500 hover:text-gray-700 transition cursor-pointer"
          >
            <IoClose size={24} />
          </button>
        </div>
        <div className="space-y-4">
          {route.map((item) => (
            <div>
              <button
                key={item.order}
                onClick={() => handleExpand(item)} 
                className="flex text-left gap-4 p-3 rounded-md hover:bg-gray-50 transition cursor-pointer w-full"
              >
                <div className="flex flex-row justify-center items-center gap-3">
                  <div className="text-sm text-gray-500">{item.arrival_time}</div>
                  <div className={`font-medium ${current === item.order ? 'text-blue-600' : ''}`}>{item.name}</div>
                </div>
              </button>
              {expanded && current === item.order && (
                <div className="w-full pl-14 mt-3 mb-2">
                  <div className="bg-linear-to-r from-blue-50 to-indigo-50 border-l-4 border-blue-500 rounded-r-lg p-4 space-y-3 shadow-sm">
                    <div className="flex items-center gap-2">
                      <span className="px-3 py-1 bg-blue-100 text-blue-700 text-sm font-medium rounded-full">
                        {type(item.type)}
                      </span>
                    </div>
                    
                    <div className="grid grid-cols-1 gap-2 text-sm">
                      <div className="flex items-center gap-2">
                        <span className="font-semibold text-gray-700 min-w-22.5">⏱️ Thời lượng:</span>
                        <span className="text-gray-600">{item.duration_min} phút</span>
                      </div>
                      
                      <div className="flex items-start gap-2">
                        <span className="font-semibold text-gray-700 min-w-22.5">📍 Địa chỉ:</span>
                        <span className="text-gray-600 flex-1 pl-1.5">{item.address}</span>
                      </div>
                      
                      <div className="flex items-center gap-2">
                        <span className="font-semibold text-gray-700 min-w-22.5">⭐ Đánh giá:</span>
                        <span className="text-yellow-600 font-medium pl-1.5">{item.rating} / 5.0</span>
                      </div>
                    </div>
                  </div>
                </div>
              )}
            </div>
          ))}
        </div>
      </div>
    </>
  )
}

export const Timeline: React.FC<TimelineProps> = ({ 
  onDaySelect, result 
}) => {
  const [activeDay, setActiveDay] = useState<number | null>(null);
  const [route, setRoute] = useState<ItineraryRoute[]>([]);
  const [showPopup, setShowPopup] = useState<boolean>(false);

  const handleClick = (day: number) => {
    setActiveDay(day);
    setShowPopup(true);
  }

  const handleClosePopup = () => {
    setShowPopup(false);
  }

  const handleMap = (day: number) => {
    const selectedDay = result.itinerary.find(item => item.day === day);
    if (selectedDay) {
      setRoute(selectedDay.route);
      onDaySelect?.(day, selectedDay.route);
      setActiveDay(day);
    }
  }

  useEffect(() => {
    handleMap(result.itinerary[0].day);
  }, [result])

  return (
    <div className="w-1/2 mr-4 relative">
      <div className="text-[20px] font-semibold mb-4">
        Lịch trình chi tiết
      </div>

      <div>
        {result.itinerary.map((item) => (
          <div key={item.day}>
            <button 
              className={`font-semibold text-lg border p-2 cursor-pointer w-full text-left rounded-md hover:bg-gray-100 transition flex items-center gap-2 mb-4 relative ${
                activeDay === item.day ? 'bg-blue-50 border-blue-300' : ''
              }`}
              onClick={() => handleMap(item.day)}
            >
              <div>
                Ngày {item.day}
              </div>
              <button
                className="flex items-center justify-center text-sm text-blue-600 hover:underline ml-2 cursor-pointer absolute right-4"
                onClick={() => handleClick(item.day)}
              >
                Xem chi tiết &rarr;
              </button>
            </button>
            
          </div>
        ))}
      </div>

      {showPopup && <Details route={route} onClose={handleClosePopup} day={activeDay!} />}
    </div>
  )
}