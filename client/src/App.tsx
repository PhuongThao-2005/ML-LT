import { Header, Input, Result, Homepage, Footer } from "./components"
import { use, useState } from "react"

function App() {
  const [result, setResult] = useState<any[]>([])

  return (
    <div className="h-dvh">
      <div className="z-auto">
        <img 
          src="/cover.jpg" 
          className="h-83 w-full object-cover object-[50%_83%] absolute -z-10 opacity-95"
        />
        <Header />
        <Input setResult={setResult} />
      </div>
      <Homepage />
      <Footer />
    </div>
  )
}

export default App
