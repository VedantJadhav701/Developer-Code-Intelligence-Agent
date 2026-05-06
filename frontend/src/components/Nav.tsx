"use client";

import Link from "next/link";
import Image from "next/image";
import { motion } from "framer-motion";
import { GithubIcon } from "./GithubIcon";

export const Nav = () => (
  <motion.nav 
    initial={{ y: -100 }}
    animate={{ y: 0 }}
    className="fixed top-0 w-full z-50 border-b border-white/10 bg-black/80 backdrop-blur-md"
  >
    <div className="max-w-7xl mx-auto px-6 h-20 flex items-center justify-between">
      <Link href="/" className="flex items-center gap-4 hover:opacity-80 transition-opacity">
        <Image src="/logo.png" alt="DevAgent Logo" width={56} height={56} className="rounded-xl shadow-lg shadow-white/5" />
        <span className="text-2xl font-extrabold tracking-tighter">DevAgent <span className="text-white/30 font-medium ml-1 text-base tracking-normal">v3.4.1</span></span>
      </Link>
      <div className="hidden md:flex items-center gap-8">
        <Link href="/docs" className="text-sm font-semibold text-white/60 hover:text-white transition-colors">Docs</Link>
        <Link href="/benchmarks" className="text-sm font-semibold text-white/60 hover:text-white transition-colors">Benchmarks</Link>
        <Link href="/changelog" className="text-sm font-semibold text-white/60 hover:text-white transition-colors">Changelog</Link>
        <Link href="/download" className="text-sm font-semibold text-white/60 hover:text-white transition-colors">Download</Link>
        <a 
          href="https://github.com/VedantJadhav701/Developer-Code-Intelligence-Agent"
          target="_blank"
          rel="noopener noreferrer"
          className="px-5 py-2.5 rounded-full bg-white text-black text-sm font-bold hover:scale-105 transition-transform flex items-center gap-2"
        >
          <GithubIcon size={18} /> Star on GitHub
        </a>
      </div>
    </div>
  </motion.nav>
);
