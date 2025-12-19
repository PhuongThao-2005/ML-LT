

export const Footer = () => {

  return (
    <div className="w-full h-20 bg-gray-200 flex justify-center items-center mt-20">
      <div className="text-gray-600">
        © {new Date().getFullYear()} Travel Planner. All rights reserved.
      </div>
    </div>
  )
}