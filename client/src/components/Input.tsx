import { useEffect, useState } from "react";
import { GrPlan } from "react-icons/gr";

export const Input = () => {
  const fullText = "Tôi muốn đi Đà Lạt 5 ngày với 4 thành viên và chi phí 10 triệu VNĐ...";
  const [placeholder, setPlaceholder] = useState("");
  const [index, setIndex] = useState(0);

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
      <div className="max-w-5xl mx-auto h-full flex flex-col justify-center px-4 relative">
        <div className="font-bold text-white text-5xl mt-24">
          Bạn muốn đi đâu?  
        </div>
        <div className="bg-[#ffb700] mt-6 p-1 rounded-md shadow-xl w-full absolute -bottom-5 grid grid-cols-[8fr_2fr] items-center gap-1">
          <input 
            className="h-11 px-3 bg-white rounded-sm outline-none focus:outline-none"
            placeholder={placeholder}
          />
          <button className="h-11 px-2 bg-[#006ce4] rounded-sm flex items-center gap-2 text-white font-semibold hover:bg-(--main) transition justify-center cursor-pointer">
            <GrPlan className="text-white"/>
            Lên kế hoạch
          </button>
        </div>
      </div>
    </div>
  )
}