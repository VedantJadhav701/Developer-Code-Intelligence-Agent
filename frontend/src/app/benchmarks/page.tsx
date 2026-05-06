"use client";

import { Nav } from "@/components/Nav";
import { Footer } from "@/components/Footer";
import { motion } from "framer-motion";
import { Activity, BarChart3, PieChart, Zap } from "lucide-react";

const MetricCard = ({ label, value, color }: any) => (
  <div className="glass p-10 rounded-[2rem] text-center relative overflow-hidden group">
    <div className={`absolute inset-0 opacity-10 blur-[60px] group-hover:opacity-20 transition-opacity ${color}`} />
    <motion.div 
      initial={{ scale: 0.9, opacity: 0 }}
      whileInView={{ scale: 1, opacity: 1 }}
      className="relative"
    >
      <div className="text-6xl font-black tracking-tighter mb-2">{value}</div>
      <div className="text-xs uppercase tracking-widest text-white/40 font-bold">{label}</div>
    </motion.div>
  </div>
);

export default function Benchmarks() {
  return (
    <main className="min-h-screen bg-black">
      <Nav />
      
      <header className="pt-40 pb-20 text-center">
        <div className="max-w-7xl mx-auto px-6">
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
          >
            <span className="text-blue-400 font-bold uppercase tracking-widest text-xs mb-4 block">Empirical Validation v3.4.1</span>
            <h1 className="text-6xl md:text-8xl font-black tracking-tighter mb-8">Integrity Over Hype.</h1>
            <p className="text-xl text-white/40 max-w-2xl mx-auto">We don't hide our failures. DevAgent is continuously benchmarked against real-world repositories to ensure orchestration reliability.</p>
          </motion.div>
        </div>
      </header>

      <section className="py-20">
        <div className="max-w-7xl mx-auto px-6">
          <div className="grid grid-cols-1 md:grid-cols-3 gap-8 mb-20">
            <MetricCard label="Dependency Repair" value="95%" color="bg-blue-500" />
            <MetricCard label="Unit Bugfixes" value="80%" color="bg-purple-500" />
            <MetricCard label="Isolation Safety" value="100%" color="bg-emerald-500" />
          </div>

          <div className="glass p-12 rounded-[3rem] border border-white/10">
            <h2 className="text-3xl font-bold mb-12 flex items-center gap-3">
              <BarChart3 className="text-blue-400" /> Success Rate by Category
            </h2>
            <div className="space-y-8">
              {[
                { label: "Import Errors", value: "95%", w: "95%", c: "bg-emerald-500" },
                { label: "Syntax Errors", value: "85%", w: "85%", c: "bg-blue-500" },
                { label: "Logic Validation", value: "70%", w: "70%", c: "bg-blue-500" },
                { label: "Cross-File Refactor", value: "20%", w: "20%", c: "bg-white/10" }
              ].map((item, i) => (
                <div key={i} className="space-y-2">
                  <div className="flex justify-between text-sm font-bold">
                    <span className="text-white/60">{item.label}</span>
                    <span>{item.value}</span>
                  </div>
                  <div className="h-3 w-full bg-white/5 rounded-full overflow-hidden">
                    <motion.div 
                      initial={{ width: 0 }}
                      whileInView={{ width: item.w }}
                      transition={{ duration: 1, delay: i * 0.1 }}
                      className={`h-full ${item.c}`}
                    />
                  </div>
                </div>
              ))}
            </div>
          </div>
        </div>
      </section>

      <Footer />
    </main>
  );
}
