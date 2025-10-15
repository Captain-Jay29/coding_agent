'use client';

import { useState, useRef, useEffect } from 'react';

interface Message {
  role: 'user' | 'assistant';
  content: string;
  metadata?: any;
}

interface ChatPanelProps {
  sessionId: string | null;
  onSessionChange: (id: string) => void;
  onLatencyUpdate?: (latency: number) => void;
}

export default function ChatPanel({ sessionId, onSessionChange, onLatencyUpdate }: ChatPanelProps) {
  const [messages, setMessages] = useState<Message[]>([]);
  const [input, setInput] = useState('');
  const [isStreaming, setIsStreaming] = useState(false);
  const messagesEndRef = useRef<HTMLDivElement>(null);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages]);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!input.trim() || isStreaming) return;

    const userMessage: Message = { role: 'user', content: input };
    setMessages(prev => [...prev, userMessage]);
    setInput('');
    setIsStreaming(true);

    try {
      const response = await fetch('http://localhost:8000/api/chat', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          message: input,
          session_id: sessionId
        })
      });

      const reader = response.body?.getReader();
      const decoder = new TextDecoder();
      let assistantMessage = '';

      setMessages(prev => [...prev, { role: 'assistant', content: '' }]);

      while (true) {
        const { done, value } = await reader!.read();
        if (done) break;

        const chunk = decoder.decode(value);
        const lines = chunk.split('\n');

        for (const line of lines) {
          if (line.startsWith('data: ')) {
            try {
              const data = JSON.parse(line.slice(6));
              console.log('Received event:', data.event, data);

              if (data.event === 'on_chat_model_stream') {
                const token = data.data?.chunk?.content || '';
                assistantMessage += token;
                setMessages(prev => {
                  const updated = [...prev];
                  updated[updated.length - 1].content = assistantMessage;
                  return updated;
                });
              } else if (data.event === 'on_complete') {
                console.log('Stream complete', data.data?.metadata);
                // Send latency to parent for metrics
                if (data.data?.metadata?.latency_seconds && onLatencyUpdate) {
                  onLatencyUpdate(data.data.metadata.latency_seconds);
                }
              } else if (data.event === 'done') {
                if (data.data?.session_id) {
                  onSessionChange(data.data.session_id);
                }
              } else if (data.event === 'error') {
                console.error('Backend error:', data.data);
                setMessages(prev => {
                  const updated = [...prev];
                  updated[updated.length - 1].content = `Error: ${data.data.error}`;
                  return updated;
                });
              }
            } catch (e) {
              console.error('Failed to parse SSE line:', line, e);
            }
          }
        }
      }
    } catch (error) {
      console.error('Chat error:', error);
      setMessages(prev => [
        ...prev,
        { role: 'assistant', content: 'Error: Failed to get response' }
      ]);
    } finally {
      setIsStreaming(false);
    }
  };

  const handleNewSession = async () => {
    try {
      const res = await fetch('http://localhost:8000/api/sessions', {
        method: 'POST'
      });
      const data = await res.json();
      setMessages([]);
      onSessionChange(data.session_id);
    } catch (error) {
      console.error('Failed to create session:', error);
    }
  };

  return (
    <div className="flex flex-col h-full">
      {/* Session Controls */}
      <div className="border-b border-gray-100 px-6 py-3 bg-gray-50 flex items-center justify-between">
        <div className="text-sm text-gray-500 font-medium">
          {sessionId ? `Session: ${sessionId.slice(0, 8)}...` : 'No active session'}
        </div>
        <button
          onClick={handleNewSession}
          className="text-sm bg-blue-500 hover:bg-blue-600 text-white px-4 py-1.5 rounded-lg transition-colors font-medium"
        >
          New Session
        </button>
      </div>

      {/* Messages */}
      <div className="flex-1 overflow-auto p-6 space-y-4">
        {messages.length === 0 && (
          <div className="flex items-center justify-center h-full text-gray-400">
            <div className="text-center">
              <div className="text-4xl mb-2">💬</div>
              <p className="text-sm">Start a conversation with your coding agent</p>
            </div>
          </div>
        )}
        {messages.map((msg, idx) => (
          <div
            key={idx}
            className={`flex ${msg.role === 'user' ? 'justify-end' : 'justify-start'}`}
          >
            <div
              className={`max-w-[75%] rounded-2xl p-4 shadow-sm ${
                msg.role === 'user'
                  ? 'bg-gradient-to-r from-blue-500 to-blue-600 text-white'
                  : 'bg-gray-50 border border-gray-100'
              }`}
            >
              <div className={`text-xs font-semibold mb-2 ${
                msg.role === 'user' ? 'text-blue-100' : 'text-gray-500'
              }`}>
                {msg.role === 'user' ? '👤 You' : '🤖 Agent'}
              </div>
              <div className="whitespace-pre-wrap leading-relaxed">{msg.content}</div>
            </div>
          </div>
        ))}
        <div ref={messagesEndRef} />
      </div>

      {/* Input */}
      <form onSubmit={handleSubmit} className="border-t border-gray-100 p-6 bg-white">
        <div className="flex gap-3">
          <input
            type="text"
            value={input}
            onChange={(e) => setInput(e.target.value)}
            placeholder="Ask me to create, edit, or run code..."
            className="flex-1 border border-gray-200 rounded-xl px-5 py-3 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent transition-all"
            disabled={isStreaming}
          />
          <button
            type="submit"
            disabled={isStreaming || !input.trim()}
            className="bg-gradient-to-r from-blue-500 to-blue-600 text-white px-8 py-3 rounded-xl hover:from-blue-600 hover:to-blue-700 disabled:from-gray-300 disabled:to-gray-300 disabled:cursor-not-allowed font-medium shadow-sm transition-all"
          >
            {isStreaming ? (
              <span className="flex items-center gap-2">
                <span className="animate-pulse">●</span> Sending...
              </span>
            ) : (
              'Send'
            )}
          </button>
        </div>
      </form>
    </div>
  );
}

