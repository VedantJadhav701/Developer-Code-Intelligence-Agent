"use client";

import React from "react";
import Image from "next/image";
import Link from "next/link";
import { motion } from "framer-motion";
import { 
  Shield, 
  Cpu, 
  Zap, 
  CheckCircle2, 
  Activity
} from "lucide-react";
import { Nav } from "@/components/Nav";
import { Footer } from "@/components/Footer";

const Hero = () => (
  <section className="relative pt-40 pb-20 overflow-hidden">
    <div className="max-w-7xl mx-auto px-6 text-center">
      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.5 }}
      >
        <span className="inline-flex items-center gap-2 px-4 py-1.5 rounded-full bg-amber-500/10 border border-amber-500/20 text-amber-400 text-xs font-bold uppercase tracking-widest mb-8">
          <Activity size={14} /> The Maturity Layer is Live
        </span>
        <h1 className="text-6xl md:text-8xl font-extrabold tracking-tighter mb-8 leading-[0.9]">
          Local-First.<br />
          <span className="accent-gradient">Execution-Grounded.</span>
        </h1>
        <p className="text-lg md:text-xl text-white/50 max-w-2xl mx-auto mb-12">
          The autonomous coding agent runtime that prioritizes operational safety and environment integrity over generative hype.
        </p>
        <div className="flex flex-col md:flex-row items-center justify-center gap-4">
          <Link href="/download" className="w-full md:w-auto px-8 py-4 rounded-xl bg-white text-black font-bold text-lg hover:scale-105 transition-transform">
            pip install devagent-cli
          </Link>
          <Link href="/docs" className="w-full md:w-auto px-8 py-4 rounded-xl bg-white/5 border border-white/10 font-bold text-lg hover:bg-white/10 transition-colors">
            View Docs
          </Link>
        </div>
      </motion.div>

      <motion.div 
        initial={{ opacity: 0, scale: 0.95 }}
        animate={{ opacity: 1, scale: 1 }}
        transition={{ delay: 0.3, duration: 0.8 }}
        className="mt-20 relative group"
      >
        <div className="absolute inset-0 bg-amber-500/20 blur-[100px] rounded-full group-hover:bg-amber-500/30 transition-colors" />
        <div className="relative glass rounded-3xl overflow-hidden shadow-2xl shadow-black">
          <video 
            autoPlay 
            muted 
            loop 
            playsInline 
            className="w-full aspect-video object-cover"
          >
            <source src="/video.mp4" type="video/mp4" />
          </video>
        </div>
      </motion.div>
    </div>
  </section>
);

const FeatureCard = ({ icon: Icon, title, desc, delay }: any) => (
  <motion.div
    initial={{ opacity: 0, y: 20 }}
    whileInView={{ opacity: 1, y: 0 }}
    viewport={{ once: true }}
    transition={{ delay }}
    className="p-8 rounded-3xl glass hover:border-white/20 transition-colors"
  >
    <div className="w-12 h-12 rounded-2xl bg-amber-500/10 flex items-center justify-center text-amber-400 mb-6">
      <Icon size={24} />
    </div>
    <h3 className="text-xl font-bold mb-4">{title}</h3>
    <p className="text-white/40 leading-relaxed">{desc}</p>
  </motion.div>
);

const Comparison = () => (
  <section id="compare" className="py-20">
    <div className="max-w-7xl mx-auto px-6">
      <div className="mb-20 text-center">
        <h2 className="text-4xl md:text-5xl font-bold tracking-tight mb-4">Engineered for Integrity</h2>
        <p className="text-white/40">Why DevAgent defines the standard for local orchestration.</p>
      </div>
      <div className="glass rounded-3xl overflow-hidden overflow-x-auto">
        <table className="w-full text-left min-w-[600px]">
          <thead>
            <tr className="border-b border-white/10 bg-white/5">
              <th className="p-8 text-xs uppercase tracking-widest text-white/40">Capability</th>
              <th className="p-8 text-xs uppercase tracking-widest text-white/40">Traditional</th>
              <th className="p-8 text-xs uppercase tracking-widest text-white/40">OpenCode.ai</th>
              <th className="p-8 text-xs uppercase tracking-widest text-amber-400">DevAgent</th>
            </tr>
          </thead>
          <tbody className="divide-y divide-white/5">
            {[
              { cap: "Autonomous Venv Isolation", trad: false, open: false, dev: true },
              { cap: "Self-Repairing Runtime", trad: false, open: false, dev: true },
              { cap: "Surgical Patching", trad: false, open: true, dev: true },
              { cap: "Local-First Privacy", trad: false, open: true, dev: true },
              { cap: "Atomic Rollbacks", trad: false, open: false, dev: true },
            ].map((row, i) => (
              <tr key={i} className="hover:bg-white/5 transition-colors">
                <td className="p-8 font-semibold">{row.cap}</td>
                <td className="p-8">{row.trad ? <CheckCircle2 className="text-green-500" /> : <div className="w-6 h-6 rounded-full border border-white/10" />}</td>
                <td className="p-8">{row.open ? <CheckCircle2 className="text-green-500" /> : <div className="w-6 h-6 rounded-full border border-white/10" />}</td>
                <td className="p-8 bg-amber-500/5"><CheckCircle2 className="text-amber-400" /></td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  </section>
);

export default function Home() {
  return (
    <main className="min-h-screen">
      <Nav />
      <Hero />
      
      <section id="features" className="py-20">
        <div className="max-w-7xl mx-auto px-6">
          <div className="grid grid-cols-1 md:grid-cols-3 gap-8">
            <FeatureCard 
              icon={Shield}
              title="Venv Isolation"
              desc="Every execution is contained in a provisioned .tmp_envs environment, ensuring bit-perfect isolation."
              delay={0.1}
            />
            <FeatureCard 
              icon={Zap}
              title="Self-Repairing"
              desc="Automatically detects missing dependencies and invokes the repair loop to resolve runtimes."
              delay={0.2}
            />
            <FeatureCard 
              icon={Cpu}
              title="Local-First"
              desc="Powered by Ollama. 100% offline. Zero data leakage. Your code stays in your project root."
              delay={0.3}
            />
          </div>
        </div>
      </section>

      <Comparison />

      <section className="py-40">
        <div className="max-w-7xl mx-auto px-6">
          <div className="p-20 rounded-[3rem] glass text-center relative overflow-hidden">
            <div className="absolute inset-0 bg-amber-500/10 blur-[120px]" />
            <h2 className="text-5xl font-bold mb-8 relative">Ready to fix the execution gap?</h2>
            <div className="flex justify-center gap-4 relative">
              <Link href="/download" className="px-10 py-5 rounded-2xl bg-white text-black font-bold text-xl hover:scale-105 transition-transform">
                Get Started for Free
              </Link>
            </div>
          </div>
        </div>
      </section>

      <Footer />
    </main>
  );
}
