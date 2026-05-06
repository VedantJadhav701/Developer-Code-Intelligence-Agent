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
      <>
        <p className="text-xl text-white/60 mb-8">DevAgent is a research-grade, local-first coding agent runtime designed for high-integrity repository orchestration.</p>
        <p>Unlike traditional AI assistants that simply generate text, DevAgent operates with **full execution grounding**. It manages the entire lifecycle of a fix: scanning the environment, provisioning isolated runtimes, and verifying patches against actual tests.</p>
        <div className="grid grid-cols-1 md:grid-cols-2 gap-6 mt-12">
          <div className="glass p-6 rounded-2xl border border-white/10">
            <Shield className="text-blue-400 mb-4" />
            <h3 className="font-bold mb-2">Safety First</h3>
            <p className="text-sm text-white/40">100% local execution via Ollama and isolated .tmp_envs workspaces.</p>
          </div>
          <div className="glass p-6 rounded-2xl border border-white/10">
            <Zap className="text-blue-400 mb-4" />
            <h3 className="font-bold mb-2">Self-Repairing</h3>
            <p className="text-sm text-white/40">Autonomously resolves missing dependencies to ensure runtime health.</p>
          </div>
        </div>
      </>
    )
  },
  installation: {
    title: "Installation",
    content: (
      <>
        <p className="text-white/60 mb-8">Get DevAgent up and running in seconds. DevAgent is distributed via PyPI for seamless integration into any workflow.</p>
        <h3 className="text-xl font-bold mb-4">Prerequisites</h3>
        <ul className="list-disc pl-6 space-y-2 text-white/60 mb-8">
          <li>Python 3.11 or higher</li>
          <li>Ollama (for local model hosting)</li>
          <li>Git (for surgical patching support)</li>
        </ul>
        <div className="bg-black border border-white/10 p-6 rounded-2xl flex items-center justify-between group">
          <code className="text-blue-400">pip install devagent-cli</code>
          <button className="p-2 hover:bg-white/5 rounded-lg transition-colors"><Copy size={16} /></button>
        </div>
      </>
    )
  },
  quickstart: {
    title: "Quickstart",
    content: (
      <>
        <p className="text-white/60 mb-8">Resolve your first bug with DevAgent in three simple steps.</p>
        <div className="space-y-8">
          <div className="flex gap-4">
            <div className="w-8 h-8 rounded-full bg-blue-500/20 text-blue-400 flex items-center justify-center font-bold shrink-0">1</div>
            <div>
              <h4 className="font-bold mb-2">Check Infrastructure</h4>
              <p className="text-sm text-white/40 mb-4">Verify your local environment and model connectivity.</p>
              <code className="bg-black p-3 rounded-lg border border-white/5 block text-blue-400">devagent doctor</code>
            </div>
          </div>
          <div className="flex gap-4">
            <div className="w-8 h-8 rounded-full bg-blue-500/20 text-blue-400 flex items-center justify-center font-bold shrink-0">2</div>
            <div>
              <h4 className="font-bold mb-2">Run a Task</h4>
              <p className="text-sm text-white/40 mb-4">Provide a natural language instruction to any local repository.</p>
              <code className="bg-black p-3 rounded-lg border border-white/5 block text-blue-400">devagent run --task "Fix the failing tests"</code>
            </div>
          </div>
        </div>
      </>
    )
  },
  "venv-isolation": {
    title: "Venv Isolation",
    content: (
      <>
        <p className="text-white/60 mb-8">Total host containment. DevAgent never operates directly on your production environment during the validation phase.</p>
        <p className="mb-8">When a task starts, DevAgent creates a hidden **`.tmp_envs/`** directory. It clones your project structure and provisions a bit-perfect virtual environment to ensure your host system remains clean and stable.</p>
        <div className="glass p-8 rounded-3xl border border-white/10 flex items-center gap-6">
           <div className="p-4 bg-emerald-500/10 rounded-2xl text-emerald-400"><Shield size={32} /></div>
           <div>
             <h4 className="font-bold mb-1">Zero Pollutants</h4>
             <p className="text-sm text-white/40 m-0">No library pollution. No side effects. No accidental deletions.</p>
           </div>
        </div>
      </>
    )
  },
  "surgical-patching": {
    title: "Surgical Patching",
    content: (
      <>
        <p className="text-white/60 mb-8">Maintain your architecture. DevAgent respects your code style and git history.</p>
        <p>Unlike standard agents that rewrite entire files (and destroy context), DevAgent generates **line-level unified diffs**. It only touches what needs fixing, preserving your comments, indentation, and logic structure.</p>
        <div className="mt-8 bg-black border border-white/10 rounded-2xl overflow-hidden font-mono text-sm">
          <div className="p-4 bg-white/5 border-b border-white/10 text-white/40">patch.diff</div>
          <div className="p-6">
            <div className="text-red-400">- return a + b</div>
            <div className="text-emerald-400">+ return int(a) + int(b) # Fixed type mismatch</div>
          </div>
        </div>
      </>
    )
  },
  "repair-loop": {
    title: "Repair Loop",
    content: (
      <>
        <p className="text-white/60 mb-8">Autonomous recovery from runtime failures.</p>
        <p>If DevAgent encounters a `ModuleNotFoundError` or a dependency conflict during validation, it doesn't crash. It invokes the **Autonomous Repair Loop** to resolve missing packages and stabilize the environment in real-time.</p>
        <div className="mt-8 relative p-12 glass rounded-[2rem] border border-white/10 overflow-hidden text-center">
           <div className="absolute inset-0 bg-blue-500/5 blur-[80px]" />
           <Cpu size={48} className="text-blue-400 mx-auto mb-6" />
           <h3 className="text-2xl font-bold mb-4">Self-Healing Infrastructure</h3>
           <p className="text-white/40 max-w-md mx-auto">The agent proactively repairs the validation environment so you don't have to manage dependencies manually.</p>
        </div>
      </>
    )
  }
};

export default function Docs() {
  const [activeSection, setActiveSection] = useState("introduction");

  return (
    <main className="min-h-screen bg-black">
      <Nav />
      
      <div className="pt-32 pb-20 max-w-7xl mx-auto px-6 grid grid-cols-1 md:grid-cols-[280px_1fr] gap-16">
        {/* Sidebar */}
        <aside className="hidden md:block sticky top-32 h-fit space-y-10">
          <div>
            <h4 className="text-[10px] uppercase tracking-[0.2em] text-white/30 font-black mb-6">Getting Started</h4>
            <div className="space-y-1">
              {[
                { id: "introduction", label: "Introduction", icon: Book },
                { id: "installation", label: "Installation", icon: Terminal },
                { id: "quickstart", label: "Quickstart", icon: Zap }
              ].map(item => (
                <button 
                  key={item.id}
                  onClick={() => setActiveSection(item.id)}
                  className={`w-full text-left px-4 py-2.5 rounded-xl text-sm font-semibold transition-all flex items-center gap-3 ${activeSection === item.id ? "bg-white/5 text-white border border-white/10" : "text-white/40 hover:text-white/60"}`}
                >
                  <item.icon size={16} />
                  {item.label}
                </button>
              ))}
            </div>
          </div>
          <div>
            <h4 className="text-[10px] uppercase tracking-[0.2em] text-white/30 font-black mb-6">Core Tech</h4>
            <div className="space-y-1">
              {[
                { id: "venv-isolation", label: "Venv Isolation", icon: Shield },
                { id: "surgical-patching", label: "Surgical Patching", icon: Code },
                { id: "repair-loop", label: "Repair Loop", icon: Cpu }
              ].map(item => (
                <button 
                  key={item.id}
                  onClick={() => setActiveSection(item.id)}
                  className={`w-full text-left px-4 py-2.5 rounded-xl text-sm font-semibold transition-all flex items-center gap-3 ${activeSection === item.id ? "bg-white/5 text-white border border-white/10" : "text-white/40 hover:text-white/60"}`}
                >
                  <item.icon size={16} />
                  {item.label}
                </button>
              ))}
            </div>
          </div>
        </aside>

        {/* Content */}
        <div className="min-h-[600px]">
          <AnimatePresence mode="wait">
            <motion.section
              key={activeSection}
              initial={{ opacity: 0, x: 20 }}
              animate={{ opacity: 1, x: 0 }}
              exit={{ opacity: 0, x: -20 }}
              transition={{ duration: 0.3 }}
              className="max-w-3xl"
            >
              <h1 className="text-5xl md:text-7xl font-black tracking-tighter mb-10">
                {(sections as any)[activeSection].title}
              </h1>
              <div className="prose prose-invert prose-blue max-w-none">
                {(sections as any)[activeSection].content}
              </div>
              
              <div className="mt-20 pt-10 border-t border-white/5 flex justify-between items-center text-sm">
                <span className="text-white/20">Last updated: May 7, 2026</span>
                <a href="#" className="text-blue-400 hover:underline flex items-center gap-1 font-bold">
                  Edit this page on GitHub <ChevronRight size={14} />
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
