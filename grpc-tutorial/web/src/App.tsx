import React, { useEffect } from "react";
import "./App.css";

import { gRPCClients } from "./client";
import { InferRequest } from "./deepthought/deepthought_pb";

function App() {
  const [response, setResponse] = React.useState<number>(0);

  useEffect(() => {
    (async () => {
      // gRPC request
      const request = new InferRequest();
      request.setQuery("Life");
      const response = await gRPCClients.computeClient.infer(request, null);
      console.log(response);
      setResponse(response.getAnswer());
    })();
  }, []);

  return (
    <div className="App">
      <header className="App-header">
        <p>Show response from gRPC server: {response}</p>
      </header>
    </div>
  );
}

export default App;
