"use client";

import { Nav } from "@/components/Nav";
import { Footer } from "@/components/Footer";
import { motion } from "framer-motion";
import { Book, Code, Terminal, Shield } from "lucide-react";

export default function Docs() {
  return (
    <main className="min-h-screen bg-black">
      <Nav />
      
      <div className="pt-32 pb-20 max-w-7xl mx-auto px-6 grid grid-cols-1 md:grid-cols-[250px_1fr_200px] gap-12">
        {/* Sidebar */}
        <aside className="hidden md:block sticky top-32 h-fit space-y-8">
          <div>
            <h4 className="text-xs uppercase tracking-widest text-white/40 font-bold mb-4">Getting Started</h4>
            <div className="space-y-2">
              {["Introduction", "Installation", "Quickstart"].map(link => (
                <a key={link} href="#" className="block text-sm text-white/60 hover:text-white transition-colors py-1">{link}</a>
              ))}
            </div>
          </div>
          <div>
            <h4 className="text-xs uppercase tracking-widest text-white/40 font-bold mb-4">Core Tech</h4>
            <div className="space-y-2">
              {["Venv Isolation", "Surgical Patching", "Repair Loop"].map(link => (
                <a key={link} href="#" className="block text-sm text-white/60 hover:text-white transition-colors py-1">{link}</a>
              ))}
            </div>
          </div>
        </aside>

        {/* Content */}
        <motion.div 
          initial={{ opacity: 0, y: 10 }}
          animate={{ opacity: 1, y: 0 }}
          className="prose prose-invert prose-blue max-w-none"
        >
          <h1 className="text-5xl font-extrabold tracking-tighter mb-8">Documentation</h1>
          <p className="text-xl text-white/60 mb-12">Learn how to orchestrate your local codebase with DevAgent.</p>

          <section className="space-y-12">
            <div className="glass p-8 rounded-3xl border border-white/10">
              <div className="flex items-center gap-3 mb-4 text-blue-400">
                <Shield size={24} />
                <h2 className="text-2xl font-bold m-0">The Maturity Layer</h2>
              </div>
              <p className="text-white/60">DevAgent enters a repository and automatically creates an isolated execution environment. This prevents side effects on your host machine and ensures every patch is validated in a bit-perfect clone of your runtime.</p>
            </div>

            <div className="space-y-4">
              <h2 className="text-2xl font-bold">Quick Install</h2>
              <div className="bg-black border border-white/10 p-6 rounded-2xl flex items-center justify-between">
                <code className="text-blue-400 font-mono">pip install devagent-cli</code>
                <button className="text-xs font-bold uppercase tracking-widest hover:text-blue-400 transition-colors">Copy</button>
              </div>
            </div>

            <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
              <div className="p-6 rounded-2xl border border-white/10 hover:bg-white/5 transition-colors group cursor-pointer">
                <Book className="mb-4 text-blue-400" />
                <h3 className="font-bold mb-2">Introduction Guide</h3>
                <p className="text-sm text-white/40">Learn the philosophy behind execution-grounded agents.</p>
              </div>
              <div className="p-6 rounded-2xl border border-white/10 hover:bg-white/5 transition-colors group cursor-pointer">
                <Terminal className="mb-4 text-blue-400" />
                <h3 className="font-bold mb-2">CLI Reference</h3>
                <p className="text-sm text-white/40">Complete command list for devagent run, doctor, and more.</p>
              </div>
            </div>
          </section>
        </motion.div>

        {/* Table of Contents */}
        <aside className="hidden lg:block sticky top-32 h-fit">
          <h4 className="text-xs uppercase tracking-widest text-white/40 font-bold mb-4">On this page</h4>
          <div className="space-y-2 border-l border-white/10 pl-4">
            {["Introduction", "Maturity Layer", "Quick Install", "Guides"].map(link => (
              <a key={link} href="#" className="block text-xs text-white/30 hover:text-white transition-colors">{link}</a>
            ))}
          </div>
        </aside>
      </div>

      <Footer />
    </main>
  );
}
