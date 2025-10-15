'use client';

import { useState } from 'react';
import ChatPanel from '@/components/ChatPanel';
import FileTree from '@/components/FileTree';
import MetricsPanel from '@/components/MetricsPanel';

export default function Home() {
  const [sessionId, setSessionId] = useState<string | null>(null);
  const [latencies, setLatencies] = useState<number[]>([]);

  const handleLatencyUpdate = (latency: number) => {
    setLatencies(prev => {
      const updated = [...prev, latency];
      // Keep only last 10 latencies for running average
      return updated.slice(-10);
    });
  };

  return (
    <div className="h-screen bg-gradient-to-br from-gray-50 to-gray-100 p-6 flex items-center justify-center">
      <div className="w-full max-w-7xl h-full flex gap-6">
        {/* Left Column: Chat */}
        <div className="flex-1 flex flex-col bg-white rounded-2xl shadow-xl overflow-hidden">
          <header className="bg-gradient-to-r from-blue-500 to-blue-600 text-white p-6 shadow-md">
            <h1 className="text-2xl font-bold">Coding Agent</h1>
            <p className="text-blue-100 text-sm mt-1">AI-powered coding assistant</p>
          </header>
          <ChatPanel 
            sessionId={sessionId} 
            onSessionChange={setSessionId} 
            onLatencyUpdate={handleLatencyUpdate}
          />
        </div>

        {/* Right Column: File Tree + Metrics */}
        <div className="w-96 flex flex-col gap-6">
          {/* File Tree (top) */}
          <div className="flex-1 bg-white rounded-2xl shadow-xl overflow-hidden">
            <FileTree />
          </div>

          {/* Metrics (bottom) */}
          <div className="h-72 bg-white rounded-2xl shadow-xl overflow-hidden">
            <MetricsPanel sessionId={sessionId} latencies={latencies} />
          </div>
        </div>
      </div>
    </div>
  );
}

