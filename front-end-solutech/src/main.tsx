import { StrictMode } from "react";
import { createRoot } from "react-dom/client";
import "./index.css";
import App from "./App";

// Enregistrement du Service Worker pour le mode hors-ligne
if ('serviceWorker' in navigator) {
  window.addEventListener('load', () => {
    navigator.serviceWorker.register('/sw.js')
      .then((registration) => {
        console.log('[SW] Service Worker enregistré:', registration.scope);
      })
      .catch((error) => {
        console.log('[SW] Échec enregistrement SW:', error);
      });
  });
}

createRoot(document.getElementById("root")!).render(
  <StrictMode>
    <App />
  </StrictMode>
);
