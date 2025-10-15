'use client';

import { useState, useEffect } from 'react';

interface MetricsPanelProps {
  sessionId: string | null;
  latencies?: number[];
}

export default function MetricsPanel({ sessionId, latencies = [] }: MetricsPanelProps) {
  const [metrics, setMetrics] = useState<any>(null);

  // Calculate average latency
  const avgLatency = latencies.length > 0
    ? latencies.reduce((a, b) => a + b, 0) / latencies.length
    : 0;

  useEffect(() => {
    if (!sessionId) return;

    const fetchMetrics = async () => {
      try {
        const res = await fetch(`http://localhost:8000/api/metrics/${sessionId}`);
        if (!res.ok) {
          throw new Error(`HTTP error! status: ${res.status}`);
        }
        const data = await res.json();
        setMetrics(data);
      } catch (error) {
        // Silently fail if backend is not running
        setMetrics(null);
      }
    };

    fetchMetrics();
    const interval = setInterval(fetchMetrics, 2000);
    return () => clearInterval(interval);
  }, [sessionId]);

  if (!metrics) {
    return (
      <div className="h-full flex flex-col">
        <div className="border-b border-gray-100 p-4 bg-gradient-to-r from-purple-50 to-pink-50">
          <h3 className="font-bold text-gray-700 flex items-center gap-2">
            <span>📊</span>
            <span>Session Metrics</span>
          </h3>
          <p className="text-xs text-gray-500 mt-1">Real-time statistics</p>
        </div>
        <div className="flex-1 flex items-center justify-center text-gray-400">
          <div className="text-center">
            <div className="text-3xl mb-2">📈</div>
            <p className="text-sm">No active session</p>
          </div>
        </div>
      </div>
    );
  }

  return (
    <div className="h-full flex flex-col">
      <div className="border-b border-gray-100 p-4 bg-gradient-to-r from-purple-50 to-pink-50">
        <h3 className="font-bold text-gray-700 flex items-center gap-2">
          <span>📊</span>
          <span>Session Metrics</span>
        </h3>
        <p className="text-xs text-gray-500 mt-1">Updates every 2s</p>
      </div>
      <div className="flex-1 p-4">
        {/* 2x2 Grid Layout */}
        <div className="grid grid-cols-2 gap-3 mb-3">
          {/* Turn */}
          <div className="bg-gradient-to-br from-blue-50 to-blue-100 rounded-lg p-3 text-center">
            <div className="text-xs text-gray-600 font-medium mb-1">Turn</div>
            <div className="text-3xl font-bold text-blue-600">{metrics.turn_number}</div>
          </div>
          
          {/* Messages */}
          <div className="bg-gradient-to-br from-green-50 to-green-100 rounded-lg p-3 text-center">
            <div className="text-xs text-gray-600 font-medium mb-1">Messages</div>
            <div className="text-3xl font-bold text-green-600">{metrics.message_count}</div>
          </div>
          
          {/* Files */}
          <div className="bg-gradient-to-br from-purple-50 to-purple-100 rounded-lg p-3 text-center">
            <div className="text-xs text-gray-600 font-medium mb-1">Files</div>
            <div className="text-3xl font-bold text-purple-600">{metrics.files_in_context}</div>
          </div>
          
          {/* Latency */}
          <div className="bg-gradient-to-br from-orange-50 to-amber-100 rounded-lg p-3 text-center">
            <div className="text-xs text-gray-600 font-medium mb-1">Latency</div>
            {avgLatency > 0 ? (
              <>
                <div className="text-3xl font-bold text-orange-600">{avgLatency.toFixed(1)}s</div>
                <div className="text-xs text-gray-500">avg of {latencies.length}</div>
              </>
            ) : (
              <div className="text-2xl font-bold text-gray-300">-</div>
            )}
          </div>
        </div>
        
        {/* Session ID */}
        <div className="text-xs text-gray-400 text-center bg-gray-50 rounded-lg p-2">
          Session: {metrics.session_id.slice(0, 8)}...
        </div>
      </div>
    </div>
  );
}

