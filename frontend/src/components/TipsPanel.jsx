import { useEffect, useState } from "react";
const API = import.meta.env.VITE_API_URL || "http://localhost:8000";

export default function TipsPanel({ sessionId }) {
  const [tips, setTips] = useState(null);
  const [loading, setLoading] = useState(false);

  useEffect(() => {
    if (!sessionId) return setTips(null);
    setLoading(true);
    fetch(`${API}/recommendations?session_id=${sessionId}`)
      .then(r => r.json())
      .then(d => setTips(d.recommendations || []))
      .catch(() => setTips([]))
      .finally(() => setLoading(false));
  }, [sessionId]);

  return (
    <div className="p-5 rounded-2xl bg-white border shadow-sm min-h-[200px]">
      <h3 className="font-semibold mb-3 text-lg">AI Coach Recommendations</h3>
      {!sessionId && <p className="text-sm text-gray-500">Upload data to see tips.</p>}
      {loading && <p className="text-sm text-gray-500">Generating suggestions…</p>}
      {sessionId && !loading && tips?.length === 0 && (
        <p className="text-sm text-gray-500">No tips available for this sample.</p>
      )}
      {tips?.length > 0 && (
        <ul className="space-y-3">
          {tips.map((t, i) => (
            <li key={i} className="p-3 rounded-xl border bg-gray-50">
              <div className="font-medium">{t.title}</div>
              <div className="text-sm text-gray-700">{t.detail}</div>
              <div className="text-xs mt-1">
                {t.est_savings_per_month_gbp != null && <span>£{t.est_savings_per_month_gbp}/mo </span>}
                {t.est_co2_saving_kg_per_month != null && <span>· {t.est_co2_saving_kg_per_month} kg CO₂/mo</span>}
              </div>
            </li>
          ))}
        </ul>
      )}
    </div>
  );
}
