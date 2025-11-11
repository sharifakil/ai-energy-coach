import { useState } from "react";
const API = import.meta.env.VITE_API_URL || "http://localhost:8000";

export default function UploadCard({ onUploaded }) {
  const [usage, setUsage] = useState(null);
  const [tariffs, setTariffs] = useState(null);
  const [carbon, setCarbon] = useState(null);
  const [loading, setLoading] = useState(false);
  const [msg, setMsg] = useState("");

  const submit = async () => {
    if (!usage) return alert("Please upload at least a smart-meter CSV");
    const fd = new FormData();
    fd.append("usage_csv", usage);
    if (tariffs) fd.append("tariffs_csv", tariffs);
    if (carbon) fd.append("carbon_csv", carbon);

    try {
      setLoading(true);
      setMsg("Uploading and analyzing…");
      const res = await fetch(`${API}/upload`, { method: "POST", body: fd });
      const data = await res.json();
      if (!res.ok) throw new Error(data.detail || "Upload failed");
      onUploaded(data.session_id);
      setMsg("Analysis complete ✅");
    } catch (e) {
      setMsg(`Error: ${e.message}`);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="p-5 rounded-2xl bg-white border shadow-sm">
      <h3 className="font-semibold mb-3 text-lg">Upload your energy data</h3>
      <div className="space-y-2 text-sm">
        <input type="file" accept=".csv" onChange={e=>setUsage(e.target.files[0])} />
        <input type="file" accept=".csv" onChange={e=>setTariffs(e.target.files[0])} />
        <input type="file" accept=".csv" onChange={e=>setCarbon(e.target.files[0])} />
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
        CSV headers: usage <code>timestamp,kwh</code> · tariffs <code>timestamp,price_per_kwh</code> · carbon <code>timestamp,g_per_kwh</code>.
      </p>
    </div>
  );
}
