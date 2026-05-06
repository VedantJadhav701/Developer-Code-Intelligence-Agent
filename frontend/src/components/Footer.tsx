"use client";

import Image from "next/image";
import Link from "next/link";

export const Footer = () => (
  <footer className="py-20 border-t border-white/10 bg-black">
    <div className="max-w-7xl mx-auto px-6">
      <div className="flex flex-col md:flex-row justify-between items-center gap-8">
        <div className="flex items-center gap-4">
          <Image src="/logo.png" alt="DevAgent Logo" width={40} height={40} className="rounded-lg" />
          <span className="text-xl font-bold tracking-tight">DevAgent</span>
        </div>
        <div className="flex gap-8 text-sm text-white/40">
          <Link href="/docs" className="hover:text-white transition-colors">Documentation</Link>
          <a href="https://github.com/VedantJadhav701/Developer-Code-Intelligence-Agent" className="hover:text-white transition-colors">GitHub</a>
          <a href="https://pypi.org/project/devagent-cli/" className="hover:text-white transition-colors">PyPI</a>
        </div>
        <p className="text-sm text-white/20">&copy; 2026 DevAgent. Built for Operational Integrity.</p>
      </div>
    </div>
  </footer>
);
