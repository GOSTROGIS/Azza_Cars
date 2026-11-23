import React from "react";
import { createRoot } from "react-dom/client";
import "@fontsource-variable/archivo/wdth.css";
import "@fontsource-variable/inter";
import "@fontsource/jetbrains-mono/400.css";
import "@design/tokens.css";
import "@design/components.css";
import "./app.css";
import App from "./App.jsx";

createRoot(document.getElementById("root")).render(<App />);
