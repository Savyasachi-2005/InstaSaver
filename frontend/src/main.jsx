import React from "react";
import ReactDOM from "react-dom/client";
import { BrowserRouter } from "react-router-dom";
import { Toaster } from "react-hot-toast";

import App from "./App";
import "./index.css";

ReactDOM.createRoot(document.getElementById("root")).render(
  <React.StrictMode>
    <BrowserRouter>
      <App />
      <Toaster
        position="top-right"
        toastOptions={{
          style: {
            background: "#11192d",
            color: "#d7e4ff",
            border: "1px solid rgba(143, 179, 255, 0.25)",
          },
        }}
      />
    </BrowserRouter>
  </React.StrictMode>
);
