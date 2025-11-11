import { useEffect, useState } from "react";
import UploadCard from "./components/UploadCard";
import TipsPanel from "./components/TipsPanel";

export default function App() {
  const [sessionId, setSessionId] = useState(null);

  return (
    <div className="min-h-screen bg-gradient-to-b from-gray-50 to-gray-100">
      <header className="max-w-4xl mx-auto px-6 py-8">
        <h1 className="text-3xl md:text-4xl font-bold tracking-tight">
          <span className="mr-2">⚡</span>AI Energy Coach
        </h1>
        <p className="text-gray-600 mt-2">
          Analyze your smart-meter data and get personalized, explainable savings tips.
        </p>
      </header>

      <main className="max-w-4xl mx-auto px-6">
        <div className="grid md:grid-cols-2 gap-6">
          <UploadCard onUploaded={setSessionId} />
          <TipsPanel sessionId={sessionId} />
        </div>
      </main>

      <footer className="max-w-4xl mx-auto px-6 py-10 text-xs text-gray-500">
        Prototype for research/demo purposes. No PII collected.
      </footer>
    </div>
  );
}
