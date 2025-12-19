import { useEffect, useState } from "react";
import { GrPlan } from "react-icons/gr";
import { TbHistory } from "react-icons/tb";
import { mutatePlan, fetchHistory } from "../libs/api";
import type { POIResponse } from "../types";

interface InputProps {
  setResult: (result: POIResponse | null) => void;
}

export const Input: React.FC<InputProps> = ({ 
  setResult
}) => {
  const fullText = "Tôi muốn đi Đà Lạt 5 ngày với 4 thành viên và chi phí 10 triệu VNĐ...";
  const [placeholder, setPlaceholder] = useState("");
  const [index, setIndex] = useState(0);

  const [query, setQuery] = useState("");
  const [history, setHistory] = useState<{ id: number; name: string; query: string }[]>([]);

  const [loading, setLoading] = useState(false);

  const handleSaveHistory = async () => {
    if (query.length === 0) return;
    setLoading(true);
    const data = await mutatePlan(query);
    setLoading(false);
    setResult(data);

    if (!query.trim() || !data) return;
    const newHistoryItem = { id: data.tour_id, name: data.city, query };
    const newHistory = [newHistoryItem, ...history.filter(item => item.name !== query).slice(0, 5)];
    setHistory(newHistory);
    localStorage.setItem("history", JSON.stringify(newHistory));
  }

  const handleHistoryClick = async (id: number, query: string) => {
    setLoading(true);
    const history = await fetchHistory(id);
    setResult(history);
    setQuery(query);
    setLoading(false);
  }

  useEffect(() => {
    const savedHistory = localStorage.getItem("history");
    if (savedHistory) {
      const parsed = JSON.parse(savedHistory);
      if (parsed.length > 0 && typeof parsed[0] === 'string') {
        setHistory([]);
        localStorage.removeItem("history");
      } else {
        setHistory(parsed);
      }
    }
  }, [])

  useEffect(() => {
    if (index < fullText.length) {
      const timeout = setTimeout(() => {
        setPlaceholder(fullText.slice(0, index + 1));
        setIndex(index + 1);
      }, 20);
      return () => clearTimeout(timeout);
    } else {
      const timeout = setTimeout(() => {
        setPlaceholder("");
        setIndex(0);
      }, 2000);
      return () => clearTimeout(timeout);
    }
  }, [index]);

  return (
    <div className="h-65 bg-transparent">
      <div className="max-w-5xl mx-auto h-full flex flex-col justify-center relative">
        <div className="font-bold text-white text-5xl mt-24">
          Bạn muốn đi đâu?  
        </div>
        <div className="w-full bg-[#ffb700] mt-6 p-1 rounded-md shadow-md absolute -bottom-5.5 grid grid-cols-[8fr_2fr] items-center gap-1">
          <input 
            className="h-11 px-3 bg-white rounded-sm outline-none focus:outline-none"
            placeholder={placeholder}
            value={query}
            onChange={(e) => setQuery(e.target.value)}
          />
          <button 
            onClick={handleSaveHistory}
            className="h-11 px-2 bg-[#006ce4] rounded-sm flex items-center gap-2 text-white font-semibold hover:bg-(--main) transition justify-center cursor-pointer"
          >
            <GrPlan className="text-white"/>
            Lên kế hoạch
          </button>
        </div>
        <div className="absolute -bottom-14 ml-3 flex flex-row items-center">
          {history.length > 0 && (
            history.map((item, index) => (
              <button
                key={index}
                onClick={() => handleHistoryClick(item.id, item.query)}
                className="text-sm mr-2 transition text-black px-2 border rounded-xl border-gray-400 cursor-pointer flex justify-center items-center gap-1"
              >
                <TbHistory />
                {item.name}
              </button>
            ))
          )}
        </div>
      </div>
      {loading && (
        <div className="fixed inset-0 bg-black/30 flex justify-center items-center z-50">
          <div className="bg-white p-6 rounded-lg shadow-lg flex flex-col items-center">
            <div className="ease-linear rounded-full border-8 border-t-8 border-gray-200 border-t-blue-500 h-16 w-16 mb-4 animate-spin"></div>
            <div className="font-semibold text-gray-700">Đang lên kế hoạch...</div>
          </div>
        </div>
      )}
    </div>
  )
}