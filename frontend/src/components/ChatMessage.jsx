import React, { useState } from 'react';
import { ShieldCheck, AlertTriangle, AlertCircle, ThumbsUp, ThumbsDown, Check, User, Bot } from 'lucide-react';
import SourceCard from './SourceCard';
import { submitFeedback } from '../services/api';

export default function ChatMessage({ message, language }) {
  const isUser = message.sender === 'user';
  const isHindi = language === 'hi';
  const [feedbackGiven, setFeedbackGiven] = useState(null);

  const handleFeedback = async (rating) => {
    if (feedbackGiven) return;
    setFeedbackGiven(rating);
    try {
      await submitFeedback({
        question: message.questionText,
        answer: message.text,
        rating: rating,
        comment: rating === 1 ? 'Helpful and grounded' : 'Unhelpful'
      });
    } catch (err) {
      console.error('Feedback submission error', err);
    }
  };

  if (isUser) {
    return (
      <div className="flex justify-end mb-4">
        <div className="flex items-start max-w-[85%] sm:max-w-[75%] space-x-2">
          <div className="bg-emerald-700 text-white px-4 py-3 rounded-2xl rounded-tr-sm shadow-sm text-sm leading-relaxed font-medium">
            {message.text}
          </div>
          <div className="w-8 h-8 rounded-full bg-slate-200 flex items-center justify-center text-slate-600 shrink-0 mt-1">
            <User className="w-4 h-4" />
          </div>
        </div>
      </div>
    );
  }

  // Assistant Response styling by status
  const status = message.status || 'answered';
  const isEmergency = status === 'emergency_alert';
  const isRefusal = status === 'insufficient_evidence';
  const isViolation = status === 'safety_violation';

  return (
    <div className="flex justify-start mb-6">
      <div className="flex items-start max-w-[95%] sm:max-w-[85%] space-x-2">
        <div className={`w-8 h-8 rounded-full flex items-center justify-center shrink-0 mt-1 shadow-sm ${
          isEmergency ? 'bg-rose-600 text-white' :
          isRefusal ? 'bg-amber-600 text-white' :
          'bg-emerald-600 text-white'
        }`}>
          <Bot className="w-4 h-4" />
        </div>

        <div className="flex-1">
          {/* Main Bubble */}
          <div className={`p-4 sm:p-5 rounded-2xl rounded-tl-sm border shadow-sm ${
            isEmergency
              ? 'bg-rose-50/90 border-rose-300 text-rose-950'
              : isRefusal
              ? 'bg-amber-50/80 border-amber-300 text-amber-950'
              : isViolation
              ? 'bg-slate-100 border-slate-300 text-slate-800'
              : 'bg-white border-slate-200 text-slate-800'
          }`}>
            
            {/* Status Header Pill */}
            <div className="flex items-center space-x-2 mb-2.5 pb-2 border-b border-slate-100">
              {isEmergency && (
                <span className="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-extrabold bg-rose-600 text-white animate-pulse">
                  <AlertCircle className="w-3.5 h-3.5 mr-1" />
                  {isHindi ? 'आपातकालीन चेतावनी' : 'EMERGENCY ALERT'}
                </span>
              )}
              {isRefusal && (
                <span className="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-bold bg-amber-500 text-white">
                  <AlertTriangle className="w-3.5 h-3.5 mr-1" />
                  {isHindi ? 'सत्यापित साक्ष्य अनुपलब्ध' : 'Insufficient Verified Evidence'}
                </span>
              )}
              {!isEmergency && !isRefusal && !isViolation && (
                <span className="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-bold bg-emerald-100 text-emerald-800">
                  <ShieldCheck className="w-3.5 h-3.5 mr-1 text-emerald-600" />
                  {isHindi ? 'सत्यापित आधिकारिक साक्ष्य' : 'Verified Evidence-Grounded'}
                </span>
              )}

              {message.latency_ms && (
                <span className="text-xs text-slate-400 font-mono ml-auto">
                  {Math.round(message.latency_ms)}ms
                </span>
              )}
            </div>

            {/* Answer Content */}
            <div className="text-sm sm:text-base leading-relaxed whitespace-pre-line font-normal">
              {message.text}
            </div>

            {/* Verified Citations List */}
            {message.citations && message.citations.length > 0 && (
              <div className="mt-4 pt-3 border-t border-slate-200/70">
                <span className="text-xs font-bold text-slate-600 uppercase tracking-wider block mb-1">
                  {isHindi ? 'सत्यापित दस्तावेज़ स्रोत:' : 'Official Verified Sources:'}
                </span>
                <div className="space-y-2">
                  {message.citations.map((c, idx) => (
                    <SourceCard key={idx} citation={c} />
                  ))}
                </div>
              </div>
            )}

            {/* Safety Notice Footer */}
            {message.safety_notice && (
              <div className={`mt-3.5 text-xs p-2.5 rounded-lg border font-medium ${
                isEmergency
                  ? 'bg-rose-100/80 border-rose-300 text-rose-900 font-bold'
                  : 'bg-slate-50 border-slate-200 text-slate-500'
              }`}>
                {message.safety_notice}
              </div>
            )}
          </div>

          {/* Citizen Feedback Actions */}
          {!isEmergency && (
            <div className="flex items-center justify-end space-x-2 mt-1.5 px-1 text-xs text-slate-400">
              <span className="text-[11px]">{isHindi ? 'क्या यह उपयोगी था?' : 'Was this helpful?'}</span>
              <button
                onClick={() => handleFeedback(1)}
                disabled={feedbackGiven !== null}
                className={`p-1 rounded hover:bg-slate-200 transition-all ${
                  feedbackGiven === 1 ? 'text-emerald-600 font-bold' : ''
                }`}
                title="Helpful"
              >
                <ThumbsUp className="w-3.5 h-3.5" />
              </button>
              <button
                onClick={() => handleFeedback(-1)}
                disabled={feedbackGiven !== null}
                className={`p-1 rounded hover:bg-slate-200 transition-all ${
                  feedbackGiven === -1 ? 'text-rose-600 font-bold' : ''
                }`}
                title="Not helpful"
              >
                <ThumbsDown className="w-3.5 h-3.5" />
              </button>
              {feedbackGiven && (
                <span className="text-emerald-600 text-[11px] font-semibold flex items-center">
                  <Check className="w-3 h-3 mr-0.5" /> {isHindi ? 'धन्यवाद' : 'Feedback logged'}
                </span>
              )}
            </div>
          )}
        </div>
      </div>
    </div>
  );
}
