import { Header, Input, Result, Homepage, Footer } from "./components"
import { useState } from "react"
import { type POIResponse } from "./types";

function App() {
  const [result, setResult] = useState<POIResponse | null>(null);

  return (
    <div className="h-dvh">
      <div className="z-auto">
        <img 
          src="/cover.jpg" 
          className="h-83 w-full object-cover object-[50%_83%] absolute -z-10 opacity-95"
        />
        <Header setResult={setResult}/>
        <Input setResult={setResult} />
      </div>
      {result ? <Result result={result} /> : <Homepage />}
      <Footer />
    </div>
  )
}

export default App
