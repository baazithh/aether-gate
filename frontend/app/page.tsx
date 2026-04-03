"use client";
import { useEffect, useState } from "react";
import { motion, AnimatePresence } from "framer-motion";
import { Activity, ShieldAlert, CheckCircle } from "lucide-react";

export default function SurgerySuite() {
  const [interventions, setInterventions] = useState([]);

  // Poll the backend every 3 seconds for new "dirty" data
  useEffect(() => {
    const fetchInterventions = async () => {
      try {
        const res = await fetch("http://localhost:8000/pending-interventions");
        const data = await res.json();
        // Parse the strings from Redis into JSON objects
        const items = data.items.map((item: string) => JSON.parse(item));
        setInterventions(items);
      } catch (err) {
        console.error("Connection to Aether-Gate Backend lost.");
      }
    };

    const interval = setInterval(fetchInterventions, 3000);
    return () => clearInterval(interval);
  }, []);

  return (
    <main className="min-h-screen bg-black text-white p-8 font-sans">
      {/* Header with Aura Effect */}
      <div className="mb-12 flex justify-between items-end border-b border-red-900/30 pb-6">
        <div>
          <h1 className="text-4xl font-bold tracking-tighter bg-gradient-to-r from-red-500 to-blue-500 bg-clip-text text-transparent">
            AETHER-GATE // SURGERY SUITE
          </h1>
          <p className="text-zinc-500 mt-2 font-mono text-sm uppercase">Real-time Stream Intervention Deck</p>
        </div>
        <div className="flex gap-4 items-center">
          <div className="flex items-center gap-2 text-blue-400 font-mono text-xs">
            <Activity size={14} className="animate-pulse" /> SYSTEM NOMINAL
          </div>
        </div>
      </div>

      {/* Intervention Grid */}
      <div className="grid gap-4">
        <AnimatePresence>
          {interventions.length === 0 ? (
            <motion.div 
              initial={{ opacity: 0 }} animate={{ opacity: 1 }}
              className="border border-dashed border-zinc-800 p-12 text-center text-zinc-600 rounded-lg"
            >
              No high-integrity violations detected. Monitoring stream...
            </motion.div>
          ) : (
            interventions.map((item: any) => (
              <motion.div
                key={item.transaction_id}
                initial={{ x: -20, opacity: 0 }}
                animate={{ x: 0, opacity: 1 }}
                exit={{ x: 20, opacity: 0 }}
                className="bg-zinc-900/40 backdrop-blur-md border border-red-500/20 p-6 rounded-xl flex justify-between items-center group hover:border-red-500/50 transition-all"
              >
                <div className="flex items-center gap-6">
                  <div className="p-3 bg-red-500/10 rounded-full text-red-500 group-hover:shadow-[0_0_15px_rgba(239,68,68,0.3)] transition-all">
                    <ShieldAlert size={24} />
                  </div>
                  <div>
                    <h3 className="font-mono text-lg font-bold">TX_{item.transaction_id}</h3>
                    <p className="text-zinc-400 text-sm">Issue: <span className="text-red-400">{item.currency}</span></p>
                  </div>
                </div>

                <div className="flex gap-4">
                  <button className="px-4 py-2 bg-zinc-800 hover:bg-zinc-700 rounded font-mono text-xs uppercase tracking-widest transition-colors">
                    Discard
                  </button>
                  <button className="px-4 py-2 bg-blue-600 hover:bg-blue-500 rounded font-mono text-xs uppercase tracking-widest transition-all">
                    Fix & Route
                  </button>
                </div>
              </motion.div>
            ))
          )}
        </AnimatePresence>
      </div>
    </main>
  );
}