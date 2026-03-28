import { useState } from 'react'
import { Link } from "react-router-dom";
import './App.css'

function App() {
  const [data, setData] = useState(null);

  const callApi = async () => {
    const res = await fetch("http://localhost:8000/");
    const json = await res.json();
    setData(json);
  };

  return (
    <>
      <div>
        <button onClick={callApi}>API実行</button>
        <pre style={{ textAlign: "left" }}>
          {JSON.stringify(data, null, 2)}
        </pre>
      </div>

      <div className="ticks"></div>
      <section id="spacer"></section>

      <div className="App">
        <h1>{"遷移テスト"}</h1>
        <Link to='/test'>
          ボタン
        </Link>
      </div>
    </>
  )
}

export default App
