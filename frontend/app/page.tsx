"use client";
import { useEffect, useState } from "react";
import { motion, AnimatePresence } from "framer-motion";
import { Activity, ShieldAlert, Trash2, Zap, Database } from "lucide-react";

export default function SurgerySuite() {
  const [interventions, setInterventions] = useState([]);
  const [status, setStatus] = useState("CONNECTED");

  // 1. Fetching logic with error handling for status
  useEffect(() => {
    const fetchInterventions = async () => {
      try {
        const res = await fetch("http://localhost:8000/pending-interventions");
        if (!res.ok) throw new Error("CORS or Server Error");
        
        const data = await res.json();
        const items = data.items.map((item: string) => JSON.parse(item));
        setInterventions(items);
        setStatus("CONNECTED");
      } catch (err) {
        setStatus("CONNECTION_LOST");
        console.error("Aether-Gate Backend Link Severed.");
      }
    };

    const interval = setInterval(fetchInterventions, 2000);
    return () => clearInterval(interval);
  }, []);

  // 2. Intervention Logic: Sends the "Fix" signal back to FastAPI
  const handleIntervention = async (id: string, action: 'fix' | 'discard') => {
    try {
      const res = await fetch(`http://localhost:8000/intervene/${id}`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ 
            action: action,
            resolver: "ADMIN_BAZITH",
            timestamp: new Date().toISOString()
        }),
      });

      if (res.ok) {
        // Smoothly remove from UI
        setInterventions(prev => prev.filter((item: any) => item.transaction_id !== id));
      }
    } catch (err) {
      console.error("Transmission Failed.");
    }
  };

  return (
    <main className="min-h-screen bg-[#050505] text-zinc-100 p-6 lg:p-12 font-sans selection:bg-red-500/30">
      {/* Background Decorative Aura */}
      <div className="fixed top-0 left-1/2 -translate-x-1/2 w-[800px] h-[300px] bg-red-900/10 blur-[120px] pointer-events-none" />

      {/* Header */}
      <div className="relative mb-16 flex flex-col md:flex-row justify-between items-start md:items-end border-b border-zinc-800 pb-8">
        <div>
          <div className="flex items-center gap-3 mb-2">
            <Database className="text-blue-500" size={20} />
            <span className="text-xs font-mono tracking-[0.3em] text-zinc-500 uppercase">Integrity Layer 02</span>
          </div>
          <h1 className="text-5xl font-black tracking-tighter bg-gradient-to-br from-white via-zinc-400 to-zinc-800 bg-clip-text text-transparent">
            AETHER<span className="text-red-600">_</span>GATE
          </h1>
          <p className="text-zinc-500 mt-2 font-mono text-xs uppercase tracking-widest">Surgery Suite // Manual Intervention Deck</p>
        </div>

        <div className={`mt-6 md:mt-0 flex items-center gap-3 px-4 py-2 rounded-full border ${status === "CONNECTED" ? 'border-blue-500/20 bg-blue-500/5 text-blue-400' : 'border-red-500/20 bg-red-500/5 text-red-500'} font-mono text-[10px] tracking-widest transition-all uppercase`}>
          <Activity size={12} className={status === "CONNECTED" ? "animate-pulse" : ""} />
          {status}
        </div>
      </div>

      {/* Stats Mini-Bar */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-6 mb-10">
        <div className="bg-zinc-900/20 border border-zinc-800 p-4 rounded-lg">
          <p className="text-zinc-500 text-[10px] uppercase font-mono mb-1">Pending Surgery</p>
          <p className="text-2xl font-bold font-mono">{interventions.length}</p>
        </div>
      </div>

      {/* Intervention List */}
      <div className="space-y-4 relative">
        <AnimatePresence mode="popLayout">
          {interventions.length === 0 ? (
            <motion.div 
              initial={{ opacity: 0 }} animate={{ opacity: 1 }}
              className="border border-zinc-900 bg-zinc-950/50 p-20 text-center rounded-2xl"
            >
              <p className="text-zinc-700 font-mono text-sm tracking-widest uppercase italic">Scanning stream for anomalies...</p>
            </motion.div>
          ) : (
            interventions.map((item: any) => (
              <motion.div
                key={item.transaction_id}
                layout
                initial={{ x: -20, opacity: 0 }}
                animate={{ x: 0, opacity: 1 }}
                exit={{ scale: 0.95, opacity: 0 }}
                className="relative overflow-hidden bg-zinc-900/30 backdrop-blur-xl border border-white/5 p-6 rounded-2xl flex flex-col md:flex-row justify-between items-center group hover:border-red-500/30 transition-all duration-500"
              >
                {/* Scanning Light Effect */}
                <div className="absolute inset-0 bg-gradient-to-r from-transparent via-red-500/5 to-transparent -translate-x-full group-hover:animate-[shimmer_2s_infinite] pointer-events-none" />

                <div className="flex items-center gap-8 w-full md:w-auto">
                  <div className="relative">
                    <div className="p-4 bg-red-500/10 rounded-xl text-red-500 shadow-[0_0_20px_rgba(239,68,68,0.1)] group-hover:shadow-red-500/20 transition-all">
                      <ShieldAlert size={28} />
                    </div>
                  </div>
                  
                  <div className="space-y-1">
                    <div className="flex items-center gap-3">
                      <span className="text-[10px] font-mono text-zinc-500 bg-zinc-800 px-2 py-0.5 rounded uppercase">CRITICAL_VULN</span>
                      <h3 className="font-mono text-lg font-bold tracking-tight">TX_{item.transaction_id}</h3>
                    </div>
                    <p className="text-zinc-400 text-xs font-mono uppercase tracking-tighter">
                      Detected Asset: <span className="text-red-400">{item.currency}</span> 
                      <span className="mx-2 text-zinc-700">|</span> 
                      Amount: <span className="text-zinc-200">${item.amount}</span>
                    </p>
                  </div>
                </div>

                <div className="flex gap-3 mt-6 md:mt-0 w-full md:w-auto">
                  <button 
                    onClick={() => handleIntervention(item.transaction_id, 'discard')}
                    className="flex-1 md:flex-none flex items-center justify-center gap-2 px-6 py-3 bg-zinc-900 hover:bg-red-950/30 text-zinc-500 hover:text-red-400 rounded-xl font-mono text-[10px] uppercase tracking-[0.2em] border border-zinc-800 hover:border-red-500/40 transition-all"
                  >
                    <Trash2 size={14} /> Discard
                  </button>
                  <button 
                    onClick={() => handleIntervention(item.transaction_id, 'fix')}
                    className="flex-1 md:flex-none flex items-center justify-center gap-2 px-8 py-3 bg-blue-600 hover:bg-blue-500 text-white rounded-xl font-mono text-[10px] uppercase tracking-[0.2em] shadow-[0_10px_20px_rgba(37,99,235,0.2)] hover:shadow-blue-500/40 active:scale-95 transition-all"
                  >
                    <Zap size={14} fill="currentColor" /> Fix & Route
                  </button>
                </div>
              </motion.div>
            ))
          )}
        </AnimatePresence>
      </div>

      <style jsx global>{`
        @keyframes shimmer {
          100% { transform: translateX(100%); }
        }
      `}</style>
    </main>
  );
}