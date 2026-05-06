"use client";

import { Nav } from "@/components/Nav";
import { Footer } from "@/components/Footer";
import { motion } from "framer-motion";
import { History, Tag, Clock } from "lucide-react";

const TimelineEvent = ({ version, date, desc, delay }: any) => (
  <motion.div 
    initial={{ opacity: 0, x: -20 }}
    whileInView={{ opacity: 1, x: 0 }}
    transition={{ delay }}
    className="relative pl-12 pb-16 last:pb-0"
  >
    <div className="absolute left-0 top-0 w-px h-full bg-white/10" />
    <div className="absolute left-[-4px] top-2 w-2 h-2 rounded-full bg-amber-500 shadow-[0_0_15px_rgba(245,158,11,0.5)]" />
    
    <div className="flex items-center gap-3 mb-2">
      <h3 className="text-2xl font-bold tracking-tight">{version}</h3>
      <span className="px-2 py-0.5 rounded bg-white/5 border border-white/10 text-[10px] font-bold text-white/40 uppercase tracking-widest">Stable</span>
    </div>
    <div className="text-sm text-white/40 mb-4 flex items-center gap-2">
      <Clock size={14} /> {date}
    </div>
    <p className="text-white/60 leading-relaxed max-w-xl">{desc}</p>
  </motion.div>
);

export default function Changelog() {
  return (
    <main className="min-h-screen bg-black">
      <Nav />
      <section className="pt-40 pb-20">
        <div className="max-w-3xl mx-auto px-6">
          <motion.div initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }} className="mb-20">
            <h1 className="text-6xl font-black tracking-tighter mb-4">Changelog</h1>
            <p className="text-xl text-white/40">The evolution of local-first orchestration.</p>
          </motion.div>

          <div className="space-y-4">
            <TimelineEvent 
              version="v3.4.1 — The Maturity Layer" 
              date="May 7, 2026" 
              desc="Introduction of autonomous environment isolation (.tmp_envs), dependency self-repair loop, and hierarchical semantic retrieval for large-file navigation."
              delay={0.1}
            />
            <TimelineEvent 
              version="v3.3.0 — Safety First" 
              date="May 1, 2026" 
              desc="Implemented atomic git rollbacks and dry-run containment modes. Verified 100% host isolation for complex file operations."
              delay={0.2}
            />
            <TimelineEvent 
              version="v2.0.0 — ReAct Core" 
              date="April 15, 2026" 
              desc="First stable release of the execution-grounded ReAct loop. Integrated Ollama local model support and FAISS-powered code context indexing."
              delay={0.3}
            />
          </div>
        </div>
      </section>
      <Footer />
    </main>
  );
}
