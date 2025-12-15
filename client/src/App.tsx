import { Header, Input } from "./components"


function App() {

  return (
    <div className="h-dvh">
      <div className="z-auto">
        <img 
          src="public/cover.jpg" 
          className="h-83 w-full object-cover object-[50%_83%] absolute -z-10 opacity-95"
        />
        <Header />
        <Input />
      </div>
    </div>
  )
}

export default App
