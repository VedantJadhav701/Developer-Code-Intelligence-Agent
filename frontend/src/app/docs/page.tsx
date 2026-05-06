"use client";

import { useState } from "react";
import { Nav } from "@/components/Nav";
import { Footer } from "@/components/Footer";
import { motion, AnimatePresence } from "framer-motion";
import { Book, Code, Terminal, Shield, Cpu, Zap, ChevronRight, Copy, Check } from "lucide-react";

const sections = {
  introduction: {
    title: "Introduction",
    content: (
      <div className="space-y-6">
        <p className="text-xl text-white/60 leading-relaxed">DevAgent is a research-grade, local-first coding agent runtime designed for high-integrity repository orchestration.</p>
        <p className="text-white/40">Unlike traditional AI assistants that simply generate text, DevAgent operates with **full execution grounding**. It manages the entire lifecycle of a fix: scanning the environment, provisioning isolated runtimes, and verifying patches against actual tests.</p>
        <div className="grid grid-cols-1 md:grid-cols-2 gap-6 mt-12">
          <div className="glass p-6 rounded-2xl border border-white/10 relative overflow-hidden group">
            <div className="absolute inset-0 bg-blue-500/5 blur-2xl group-hover:bg-blue-500/10 transition-colors" />
            <Shield className="text-blue-400 mb-4 relative" />
            <h3 className="font-bold mb-2 relative">Safety First</h3>
            <p className="text-sm text-white/40 relative">100% local execution via Ollama and isolated .tmp_envs workspaces.</p>
          </div>
          <div className="glass p-6 rounded-2xl border border-white/10 relative overflow-hidden group">
            <div className="absolute inset-0 bg-blue-500/5 blur-2xl group-hover:bg-blue-500/10 transition-colors" />
            <Zap className="text-blue-400 mb-4 relative" />
            <h3 className="font-bold mb-2 relative">Self-Repairing</h3>
            <p className="text-sm text-white/40 relative">Autonomously resolves missing dependencies to ensure runtime health.</p>
          </div>
        </div>
      </div>
    )
  },
  installation: {
    title: "Installation",
    content: (
      <div className="space-y-6">
        <p className="text-white/60 leading-relaxed">Get DevAgent up and running in seconds. DevAgent is distributed via PyPI for seamless integration into any workflow.</p>
        <h3 className="text-xl font-bold mt-10 mb-4">Prerequisites</h3>
        <ul className="space-y-4 text-white/60">
          <li className="flex items-center gap-3"><CheckCircle size={18} className="text-emerald-500" /> Python 3.11 or higher</li>
          <li className="flex items-center gap-3"><CheckCircle size={18} className="text-emerald-500" /> Ollama (for local model hosting)</li>
          <li className="flex items-center gap-3"><CheckCircle size={18} className="text-emerald-500" /> Git (for surgical patching support)</li>
        </ul>
        <h3 className="text-xl font-bold mt-12 mb-4">Install via pip</h3>
        <div className="bg-black border border-white/10 p-6 rounded-2xl flex items-center justify-between group">
          <code className="text-blue-400 font-mono">pip install devagent-cli</code>
          <button className="p-2 hover:bg-white/5 rounded-lg transition-colors text-white/40 hover:text-white"><Copy size={18} /></button>
        </div>
      </div>
    )
  },
  quickstart: {
    title: "Quickstart",
    content: (
      <div className="space-y-12">
        <p className="text-white/60 leading-relaxed">Resolve your first bug with DevAgent in three simple steps.</p>
        <div className="space-y-12">
          <div className="flex gap-6">
            <div className="w-10 h-10 rounded-2xl bg-blue-500/20 text-blue-400 flex items-center justify-center font-bold shrink-0 border border-blue-500/20">1</div>
            <div className="flex-1">
              <h4 className="text-xl font-bold mb-2">Check Infrastructure</h4>
              <p className="text-white/40 mb-4">Verify your local environment, model connectivity, and dependency health.</p>
              <code className="bg-black p-4 rounded-xl border border-white/5 block text-blue-400 font-mono">devagent doctor</code>
            </div>
          </div>
          <div className="flex gap-6">
            <div className="w-10 h-10 rounded-2xl bg-blue-500/20 text-blue-400 flex items-center justify-center font-bold shrink-0 border border-blue-500/20">2</div>
            <div className="flex-1">
              <h4 className="text-xl font-bold mb-2">Run a Task</h4>
              <p className="text-white/40 mb-4">Provide a natural language instruction to any local repository.</p>
              <code className="bg-black p-4 rounded-xl border border-white/5 block text-blue-400 font-mono">devagent run --task "Fix the failing login tests"</code>
            </div>
          </div>
        </div>
      </div>
    )
  },
  "venv-isolation": {
    title: "Venv Isolation",
    content: (
      <div className="space-y-6">
        <p className="text-white/60 leading-relaxed">Total host containment. DevAgent never operates directly on your production environment during the validation phase.</p>
        <p className="text-white/40">When a task starts, DevAgent creates a hidden **`.tmp_envs/`** directory. It clones your project structure and provisions a bit-perfect virtual environment to ensure your host system remains clean and stable.</p>
        <div className="mt-10 glass p-8 rounded-3xl border border-white/10 flex items-center gap-6 relative overflow-hidden">
           <div className="absolute inset-0 bg-emerald-500/5 blur-3xl" />
           <div className="p-4 bg-emerald-500/10 rounded-2xl text-emerald-400 relative"><Shield size={32} /></div>
           <div className="relative">
             <h4 className="text-lg font-bold mb-1">Zero Pollutants</h4>
             <p className="text-sm text-white/40 m-0">No library pollution. No side effects. No accidental deletions.</p>
           </div>
        </div>
      </div>
    )
  },
  "surgical-patching": {
    title: "Surgical Patching",
    content: (
      <div className="space-y-6">
        <p className="text-white/60 leading-relaxed">Maintain your architecture. DevAgent respects your code style and git history.</p>
        <p className="text-white/40">Unlike standard agents that rewrite entire files (and destroy context), DevAgent generates **line-level unified diffs**. It only touches what needs fixing, preserving your comments, indentation, and logic structure.</p>
        <div className="mt-10 bg-black border border-white/10 rounded-2xl overflow-hidden font-mono text-sm">
          <div className="p-4 bg-white/5 border-b border-white/10 text-white/40 flex items-center justify-between">
            <span>patch.diff</span>
            <span className="text-[10px] uppercase tracking-widest px-2 py-0.5 bg-blue-500/10 text-blue-400 rounded">Unified Diff</span>
          </div>
          <div className="p-8 space-y-1">
            <div className="text-white/20">@@ -15,4 +15,4 @@</div>
            <div className="text-red-400/80">- return a + b</div>
            <div className="text-emerald-400">+ return int(a) + int(b) # Fixed type mismatch</div>
            <div className="text-white/20"> unchanged_context_line()</div>
          </div>
        </div>
      </div>
    )
  },
  "repair-loop": {
    title: "Repair Loop",
    content: (
      <div className="space-y-8">
        <p className="text-white/60 leading-relaxed">Autonomous recovery from runtime failures.</p>
        <p className="text-white/40">If DevAgent encounters a `ModuleNotFoundError` or a dependency conflict during validation, it doesn't crash. It invokes the **Autonomous Repair Loop** to resolve missing packages and stabilize the environment in real-time.</p>
        <div className="mt-12 relative p-16 glass rounded-[3rem] border border-white/10 overflow-hidden text-center group">
           <div className="absolute inset-0 bg-blue-500/5 blur-[100px] group-hover:bg-blue-500/10 transition-colors" />
           <Cpu size={56} className="text-blue-400 mx-auto mb-8 relative" />
           <h3 className="text-3xl font-black tracking-tight mb-4 relative">Self-Healing Infrastructure</h3>
           <p className="text-white/40 max-w-md mx-auto relative leading-relaxed">The agent proactively repairs the validation environment so you don't have to manage dependencies manually.</p>
        </div>
      </div>
    )
  }
};

const CheckCircle = ({ size, className }: any) => (
  <svg width={size} height={size} viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.5" strokeLinecap="round" strokeLinejoin="round" className={className}>
    <path d="M22 11.08V12a10 10 0 1 1-5.93-9.14" />
    <polyline points="22 4 12 14.01 9 11.01" />
  </svg>
);

export default function Docs() {
  const [activeSection, setActiveSection] = useState("introduction");

  return (
    <main className="min-h-screen bg-black">
      <Nav />
      
      <div className="pt-32 pb-20 max-w-7xl mx-auto px-6 grid grid-cols-1 md:grid-cols-[280px_1fr] gap-16">
        {/* Sidebar */}
        <aside className="hidden md:block sticky top-32 h-fit space-y-12">
          <div>
            <h4 className="text-[10px] uppercase tracking-[0.25em] text-white/20 font-black mb-8 px-4">Getting Started</h4>
            <div className="space-y-1">
              {[
                { id: "introduction", label: "Introduction", icon: Book },
                { id: "installation", label: "Installation", icon: Terminal },
                { id: "quickstart", label: "Quickstart", icon: Zap }
              ].map(item => (
                <button 
                  key={item.id}
                  onClick={() => setActiveSection(item.id)}
                  className={`w-full text-left px-4 py-3 rounded-xl text-sm font-bold transition-all flex items-center gap-3 border ${activeSection === item.id ? "bg-white/5 text-white border-white/10 shadow-lg shadow-white/[0.02]" : "text-white/30 border-transparent hover:text-white/60 hover:bg-white/[0.02]"}`}
                >
                  <item.icon size={18} className={activeSection === item.id ? "text-blue-400" : ""} />
                  {item.label}
                </button>
              ))}
            </div>
          </div>
          <div>
            <h4 className="text-[10px] uppercase tracking-[0.25em] text-white/20 font-black mb-8 px-4">Core Tech</h4>
            <div className="space-y-1">
              {[
                { id: "venv-isolation", label: "Venv Isolation", icon: Shield },
                { id: "surgical-patching", label: "Surgical Patching", icon: Code },
                { id: "repair-loop", label: "Repair Loop", icon: Cpu }
              ].map(item => (
                <button 
                  key={item.id}
                  onClick={() => setActiveSection(item.id)}
                  className={`w-full text-left px-4 py-3 rounded-xl text-sm font-bold transition-all flex items-center gap-3 border ${activeSection === item.id ? "bg-white/5 text-white border-white/10 shadow-lg shadow-white/[0.02]" : "text-white/30 border-transparent hover:text-white/60 hover:bg-white/[0.02]"}`}
                >
                  <item.icon size={18} className={activeSection === item.id ? "text-blue-400" : ""} />
                  {item.label}
                </button>
              ))}
            </div>
          </div>
        </aside>

        {/* Content Area */}
        <div className="min-h-[700px]">
          <AnimatePresence mode="wait">
            <motion.section
              key={activeSection}
              initial={{ opacity: 0, y: 10 }}
              animate={{ opacity: 1, y: 0 }}
              exit={{ opacity: 0, y: -10 }}
              transition={{ duration: 0.25, ease: "easeOut" }}
              className="max-w-4xl"
            >
              <div className="mb-16">
                <motion.div 
                  initial={{ width: 0 }}
                  animate={{ width: 40 }}
                  className="h-1 bg-blue-500 mb-6"
                />
                <h1 className="text-6xl md:text-8xl font-black tracking-tighter leading-none">
                  {(sections as any)[activeSection].title}
                </h1>
              </div>
              
              <div className="prose prose-invert prose-blue max-w-none">
                {(sections as any)[activeSection].content}
              </div>
              
              <div className="mt-32 pt-12 border-t border-white/5 flex flex-col md:flex-row justify-between items-center gap-6">
                <div className="flex items-center gap-3 text-xs font-bold text-white/20 uppercase tracking-widest">
                  <Activity size={14} /> Systems Operational • v3.6.4
                </div>
                <a href="https://github.com/VedantJadhav701/Developer-Code-Intelligence-Agent" target="_blank" rel="noopener noreferrer" className="px-6 py-3 rounded-xl bg-white/5 border border-white/10 text-sm font-bold hover:bg-white/10 transition-colors flex items-center gap-2">
                   Edit on GitHub <ChevronRight size={14} />
                </a>
              </div>
            </motion.section>
          </AnimatePresence>
        </div>
      </div>

      <Footer />
    </main>
  );
}

const Activity = ({ size, className }: any) => (
  <svg width={size} height={size} viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" className={className}>
    <polyline points="22 12 18 12 15 21 9 3 6 12 2 12" />
  </svg>
);
