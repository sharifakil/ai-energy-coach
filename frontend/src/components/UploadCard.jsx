import { useState } from "react";
const API = import.meta.env.VITE_API_URL || "http://localhost:8000";

export default function UploadCard({ onUploaded }) {
  const [usage, setUsage] = useState(null);
  const [tariffs, setTariffs] = useState(null);
  const [carbon, setCarbon] = useState(null);
  const [loading, setLoading] = useState(false);
  const [msg, setMsg] = useState("");

  // pretty-print FastAPI error payloads
  function extractErrorMessage(text, json) {
    const detail = json?.detail;
    if (typeof detail === "string") return detail;
    if (Array.isArray(detail)) return detail.map(d => d.msg || d.detail || JSON.stringify(d)).join("; ");
    if (json?.error) return json.error;
    return text || "Upload failed";
  }

  const submit = async () => {
    if (!usage && !tariffs && !carbon) {
      return alert("Please upload at least one CSV (usage).");
    }

    const fd = new FormData();
    // ⬇️ All files go under the SAME key: 'files'
    if (usage)   fd.append("files", usage);
    if (tariffs) fd.append("files", tariffs);
    if (carbon)  fd.append("files", carbon);

    try {
      setLoading(true);
      setMsg("Uploading and analyzing…");
      const res = await fetch(`${API}/upload`, { method: "POST", body: fd });

      // read as text first so we can show nice errors
      const text = await res.text();
      let data = null;
      try { data = JSON.parse(text); } catch { /* keep text */ }

      if (!res.ok) {
        const friendly = extractErrorMessage(text, data);
        throw new Error(friendly);
      }

      const sessionId = data?.session_id;
      if (!sessionId) throw new Error("No session_id returned from server.");
      onUploaded(sessionId);
      setMsg("Analysis complete ✅");
    } catch (e) {
      setMsg(`Error: ${e.message || String(e)}`);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="p-5 rounded-2xl bg-white border shadow-sm">
      <h3 className="font-semibold mb-3 text-lg">Upload your energy data</h3>

      <div className="space-y-3 text-sm">
        <div>
          <label className="block text-gray-700 mb-1 font-medium">Usage CSV (timestamp,kwh)</label>
          <input type="file" accept=".csv" onChange={e=>setUsage(e.target.files[0])} />
        </div>
        <div>
          <label className="block text-gray-700 mb-1 font-medium">Tariffs CSV (timestamp,price_per_kwh)</label>
          <input type="file" accept=".csv" onChange={e=>setTariffs(e.target.files[0])} />
        </div>
        <div>
          <label className="block text-gray-700 mb-1 font-medium">Carbon CSV (timestamp,g_per_kwh)</label>
          <input type="file" accept=".csv" onChange={e=>setCarbon(e.target.files[0])} />
        </div>
      </div>

      <button
        onClick={submit}
        disabled={loading}
        className="mt-4 w-full md:w-auto px-4 py-2 rounded-xl bg-black text-white hover:bg-gray-800 disabled:opacity-60"
      >
        {loading ? "Analyzing…" : "Analyze"}
      </button>

      {msg && <p className="text-xs text-gray-600 mt-2">{msg}</p>}

      <p className="text-[11px] text-gray-400 mt-3">
        You can drop files in any order. We auto-detect by headers.
        <br />
        Required headers → usage: <code>timestamp,kwh</code> · tariffs: <code>timestamp,price_per_kwh</code> · carbon: <code>timestamp,g_per_kwh</code>.
      </p>
    </div>
  );
}
