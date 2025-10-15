'use client';

import { useState, useEffect } from 'react';

interface FileNode {
  name: string;
  path: string;
  type: 'file' | 'directory';
  size?: number;
  children?: FileNode[];
}

export default function FileTree() {
  const [tree, setTree] = useState<FileNode[]>([]);
  const [expanded, setExpanded] = useState<Set<string>>(new Set());
  const [isConnected, setIsConnected] = useState(true);

  useEffect(() => {
    fetchTree();
    const interval = setInterval(fetchTree, 3000); // Refresh every 3s
    return () => clearInterval(interval);
  }, []);

  const fetchTree = async () => {
    try {
      const res = await fetch('http://localhost:8000/api/workspace/tree');
      if (!res.ok) {
        throw new Error(`HTTP error! status: ${res.status}`);
      }
      const data = await res.json();
      setTree(data.children || []);
      setIsConnected(true);
    } catch (error) {
      // Backend not running - show disconnected state
      setTree([]);
      setIsConnected(false);
    }
  };

  const toggleExpand = (path: string) => {
    setExpanded(prev => {
      const next = new Set(prev);
      if (next.has(path)) {
        next.delete(path);
      } else {
        next.add(path);
      }
      return next;
    });
  };

  const renderNode = (node: FileNode, depth = 0) => {
    const isExpanded = expanded.has(node.path);
    const isDir = node.type === 'directory';

    return (
      <div key={node.path}>
        <div
          className="flex items-center gap-2 px-3 py-2 hover:bg-blue-50 rounded-lg cursor-pointer transition-colors group"
          style={{ marginLeft: `${depth * 16}px` }}
          onClick={() => isDir && toggleExpand(node.path)}
        >
          {isDir && (
            <span className="text-gray-400 group-hover:text-blue-500 transition-colors">
              {isExpanded ? '▼' : '▶'}
            </span>
          )}
          <span className="text-lg">{isDir ? '📂' : '📄'}</span>
          <span className="text-sm font-medium text-gray-700 group-hover:text-blue-600 flex-1">
            {node.name}
          </span>
          {node.size && (
            <span className="text-xs text-gray-400 bg-gray-100 px-2 py-0.5 rounded-full">
              {(node.size / 1024).toFixed(1)}KB
            </span>
          )}
        </div>
        {isDir && isExpanded && node.children && (
          <div className="mt-1">
            {node.children.map(child => renderNode(child, depth + 1))}
          </div>
        )}
      </div>
    );
  };

  return (
    <div className="h-full flex flex-col">
      <div className="border-b border-gray-100 p-4 bg-gradient-to-r from-green-50 to-emerald-50">
        <h3 className="font-bold text-gray-700 flex items-center gap-2">
          <span>📁</span>
          <span>Workspace Files</span>
        </h3>
        <p className="text-xs text-gray-500 mt-1">Auto-refreshes every 3s</p>
      </div>
      <div className="flex-1 overflow-auto p-2">
        {!isConnected ? (
          <div className="flex items-center justify-center h-full text-gray-400">
            <div className="text-center">
              <div className="text-3xl mb-2">🔌</div>
              <p className="text-sm font-medium mb-1">Backend not connected</p>
              <p className="text-xs text-gray-400">Start backend server first</p>
            </div>
          </div>
        ) : tree.length === 0 ? (
          <div className="flex items-center justify-center h-full text-gray-400">
            <div className="text-center">
              <div className="text-3xl mb-2">📂</div>
              <p className="text-sm">No files yet</p>
            </div>
          </div>
        ) : (
          tree.map(node => renderNode(node))
        )}
      </div>
    </div>
  );
}

