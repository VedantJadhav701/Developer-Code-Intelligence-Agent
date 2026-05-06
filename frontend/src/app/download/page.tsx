"use client";

import { Nav } from "@/components/Nav";
import { Footer } from "@/components/Footer";
import { motion } from "framer-motion";
import { Download, Terminal, Copy, Check } from "lucide-react";
import { useState } from "react";

export default function DownloadPage() {
  const [copied, setCopied] = useState(false);
  const cmd = "pip install devagent-cli";

  const handleCopy = () => {
    navigator.clipboard.writeText(cmd);
    setCopied(true);
    setTimeout(() => setCopied(false), 2000);
  };

  return (
    <main className="min-h-screen bg-black">
      <Nav />
      <section className="pt-40 pb-20">
        <div className="max-w-4xl mx-auto px-6 text-center">
          <motion.div initial={{ opacity: 0 }} animate={{ opacity: 1 }}>
            <h1 className="text-6xl font-black tracking-tighter mb-8">Ready to Build?</h1>
            <p className="text-xl text-white/40 mb-12">Install the DevAgent CLI via PyPI. 100% Local. Zero configuration required.</p>
            
            <div className="glass p-12 rounded-[3rem] border border-white/10 relative overflow-hidden">
               <div className="absolute inset-0 bg-amber-500/5 blur-[80px]" />
               <div className="relative">
                  <div className="flex items-center gap-3 mb-6 text-amber-400 justify-center">
                    <Terminal size={24} />
                    <span className="font-bold uppercase tracking-widest text-xs">Standard Installation</span>
                  </div>
                  <div className="bg-black border border-white/10 p-8 rounded-3xl flex items-center justify-between group">
                    <code className="text-2xl font-mono text-amber-400">{cmd}</code>
                    <button 
                      onClick={handleCopy}
                      className="p-4 rounded-2xl bg-white/5 hover:bg-white/10 transition-colors text-white"
                    >
                      {copied ? <Check className="text-green-500" /> : <Copy size={20} />}
                    </button>
                  </div>
                  <p className="mt-8 text-sm text-white/20">Requires Python 3.11+ and Ollama running locally.</p>
               </div>
            </div>
          </motion.div>
        </div>
      </section>
      <Footer />
    </main>
  );
}
