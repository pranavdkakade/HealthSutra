import React, { useState, useRef, useEffect } from 'react';
import Navbar from './components/Navbar';
import ChatMessage from './components/ChatMessage';
import ChatInput from './components/ChatInput';
import DocumentsView from './components/DocumentsView';
import EvaluationDashboard from './components/EvaluationDashboard';
import AdminDashboard from './components/AdminDashboard';
import { sendChatMessage } from './services/api';
import { ShieldCheck, Sparkles, HeartPulse, AlertTriangle } from 'lucide-react';

export default function App() {
  const [activeTab, setActiveTab] = useState('chat');
  const [language, setLanguage] = useState('en');
  const [messages, setMessages] = useState([
    {
      id: 'welcome_1',
      sender: 'assistant',
      status: 'answered',
      text: (
        "Namaste! I am HealthSutra (स्वास्थ्यसूत्र), your verified public health awareness assistant for SIH25049.\n\n" +
        "Every factual answer I provide is strictly grounded in official World Health Organization (WHO) and Government of India (MoHFW) health guidelines, with verifiable citations.\n\n" +
        "How can I help you today? You may ask about disease symptoms, prevention guidelines, or government health schemes in English or हिन्दी."
      ),
      citations: [
        {
          document_id: "WHO_DENGUE_2024",
          document_title: "WHO & Government of India Health Guidelines Registry",
          organization: "WHO / MoHFW",
          page: 1,
          source_url: "https://www.who.int",
          snippet: "Controlled health awareness knowledge base active."
        }
      ],
      safety_notice: "HealthSutra provides public health awareness and does not replace examination by a qualified doctor."
    }
  ]);
  const [loading, setLoading] = useState(false);
  const chatBottomRef = useRef(null);

  useEffect(() => {
    chatBottomRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [messages, loading]);

  const handleSendMessage = async (userText) => {
    const userMsgId = `user_${Date.now()}`;
    const newMessages = [
      ...messages,
      {
        id: userMsgId,
        sender: 'user',
        text: userText,
        questionText: userText
      }
    ];
    setMessages(newMessages);
    setLoading(true);

    try {
      const resp = await sendChatMessage(userText, language);
      const assistantMsg = {
        id: `assistant_${Date.now()}`,
        sender: 'assistant',
        status: resp.status,
        text: resp.answer,
        citations: resp.citations || [],
        safety_notice: resp.safety_notice,
        top_score: resp.top_score,
        latency_ms: resp.latency_ms,
        questionText: userText
      };
      setMessages([...newMessages, assistantMsg]);
    } catch (err) {
      setMessages([
        ...newMessages,
        {
          id: `error_${Date.now()}`,
          sender: 'assistant',
          status: 'insufficient_evidence',
          text: (
            language === 'hi'
              ? "तकनीकी त्रुटि: सर्वर से संपर्क नहीं हो सका। कृपया सुनिश्चित करें कि बैकएंड सेवा चालू है।"
              : "Connection Error: Unable to communicate with HealthSutra backend. Please ensure the backend is running."
          ),
          citations: [],
          safety_notice: "Check server connection."
        }
      ]);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="min-h-screen flex flex-col bg-slate-50 text-slate-800">
      
      {/* Navbar */}
      <Navbar
        activeTab={activeTab}
        setActiveTab={setActiveTab}
        language={language}
        setLanguage={setLanguage}
      />

      {/* Main Body */}
      <main className="flex-1 flex flex-col">
        {activeTab === 'chat' && (
          <div className="flex-1 flex flex-col max-w-4xl w-full mx-auto px-4 sm:px-6 py-6">
            
            {/* Top Info Banner */}
            <div className="mb-6 p-3 bg-emerald-50 border border-emerald-200 rounded-xl flex items-center justify-between text-xs text-emerald-900 font-medium">
              <div className="flex items-center space-x-2">
                <ShieldCheck className="w-4 h-4 text-emerald-600 shrink-0" />
                <span>
                  {language === 'hi'
                    ? 'जीरो-हैलुसिनेशन नीति: बिना सत्यापित सरकारी/WHO दस्तावेज़ के उत्तर नहीं दिया जाएगा।'
                    : 'Zero-Hallucination Policy: Health answers are generated exclusively from verified official documents.'}
                </span>
              </div>
              <span className="hidden sm:inline font-bold bg-emerald-200/70 text-emerald-800 px-2 py-0.5 rounded text-[11px]">
                100% Traceable
              </span>
            </div>

            {/* Messages Feed */}
            <div className="flex-1 space-y-4">
              {messages.map((m) => (
                <ChatMessage key={m.id} message={m} language={language} />
              ))}

              {loading && (
                <div className="flex items-center space-x-2 text-slate-400 text-sm py-3 px-2">
                  <div className="w-2.5 h-2.5 rounded-full bg-emerald-500 animate-bounce"></div>
                  <div className="w-2.5 h-2.5 rounded-full bg-emerald-500 animate-bounce [animation-delay:0.2s]"></div>
                  <div className="w-2.5 h-2.5 rounded-full bg-emerald-500 animate-bounce [animation-delay:0.4s]"></div>
                  <span className="font-medium text-xs text-slate-500 ml-1">
                    {language === 'hi'
                      ? 'सत्यापित दस्तावेजों में खोज व साक्ष्य सत्यापन जारी...'
                      : 'Retrieving & verifying official document evidence...'}
                  </span>
                </div>
              )}
              <div ref={chatBottomRef} />
            </div>

            {/* Input Component */}
            <ChatInput
              onSendMessage={handleSendMessage}
              disabled={loading}
              language={language}
            />

          </div>
        )}

        {activeTab === 'documents' && (
          <DocumentsView language={language} />
        )}

        {activeTab === 'evaluation' && (
          <EvaluationDashboard language={language} />
        )}

        {activeTab === 'admin' && (
          <AdminDashboard language={language} />
        )}
      </main>

    </div>
  );
}
