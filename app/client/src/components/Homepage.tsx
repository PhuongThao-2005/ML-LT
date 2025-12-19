import { Map } from "./Map"

const place = [
  {
    name: "Đà Lạt",
    image: "./dalat.jpg"
  },
  {
    name: "Hội An",
    image: "./hoian.jpg"
  },
  { 
    name: "Hà Nội",
    image: "./hanoi.jpg"
  }
]

export const Homepage = () => {
  

  return (
    <div className="max-w-5xl mx-auto mt-22">
      <div>
        <div className="font-semibold text-2xl mb-3">
          Các địa điểm nổi bật
        </div>
        <div className="grid grid-cols-3 gap-3"> 
          {place.map((item) => (
            <div key={item.name} className="rounded-lg overflow-hidden shadow-md">
              <img 
                src={item.image} 
                alt={item.name} 
                className="w-full h-48 object-cover"
                onContextMenu={(e) => e.preventDefault()}
                onDragStart={(e) => e.preventDefault()}
              />
              <div className="p-2 font-semibold text-lg">{item.name}</div>
            </div>
          ))}
        </div>
      </div>

      <div className="mt-10">
        <div className="font-semibold text-2xl mb-1">
          Khám phá hành trình của bạn
        </div>
          <div className="font-light text-md mb-5">
            Chỉ với 1 câu lệnh, hệ thống sẽ giúp bạn lên kế hoạch chi tiết cho chuyến đi của mình
          </div>
          <div className="grid grid-cols-2 gap-2">
            <img 
              src='./example.png' 
              className=""
              onContextMenu={(e) => e.preventDefault()}
              onDragStart={(e) => e.preventDefault()}
            />
            <Map />
          </div>
      </div>
    </div>
  )
}