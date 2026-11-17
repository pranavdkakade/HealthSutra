import React, { useState } from 'react';
import { Send, Sparkles, AlertCircle } from 'lucide-react';

const SUGGESTED_PROMPTS_EN = [
  "What are the symptoms of dengue according to WHO?",
  "How can malaria be prevented?",
  "What support is given to TB patients under Ni-kshay Poshan Yojana?",
  "Why is colostrum important for a newborn infant?",
  "What is the current dengue case count in Rampur village?",
  "I have severe chest pain and difficulty breathing"
];

const SUGGESTED_PROMPTS_HI = [
  "डेंगू के मुख्य लक्षण और सावधानियां क्या हैं?",
  "मलेरिया से बचाव के लिए क्या उपाय करें?",
  "टीबी के मरीज को निक्षय पोषण योजना में कितनी सहायता मिलती है?",
  "नवजात शिशु को माँ का पहला दूध क्यों पिलाना चाहिए?",
  "मेरे गाँव में कल रात कितने मलेरिया के मरीज मिले?",
  "मरीज की छाती में तेज दर्द है और सांस फूल रही है"
];

export default function ChatInput({ onSendMessage, disabled, language }) {
  const [text, setText] = useState('');
  const isHindi = language === 'hi';
  const suggestions = isHindi ? SUGGESTED_PROMPTS_HI : SUGGESTED_PROMPTS_EN;

  const handleSubmit = (e) => {
    e.preventDefault();
    if (!text.trim() || disabled) return;
    onSendMessage(text.trim());
    setText('');
  };

  const handleSuggestionClick = (prompt) => {
    if (disabled) return;
    onSendMessage(prompt);
  };

  return (
    <div className="border-t border-slate-200 bg-white/95 backdrop-blur-md p-4 sticky bottom-0">
      <div className="max-w-4xl mx-auto">
        
        {/* Suggestion Pills */}
        <div className="flex items-center space-x-2 overflow-x-auto pb-2 mb-2 scrollbar-none text-xs">
          <span className="text-slate-400 font-semibold flex items-center shrink-0">
            <Sparkles className="w-3.5 h-3.5 mr-1 text-emerald-600" />
            {isHindi ? 'सुझाए गए प्रश्न:' : 'Try asking:'}
          </span>
          {suggestions.map((p, idx) => (
            <button
              key={idx}
              onClick={() => handleSuggestionClick(p)}
              disabled={disabled}
              className="shrink-0 px-2.5 py-1 bg-slate-100 hover:bg-emerald-50 hover:text-emerald-800 text-slate-700 rounded-lg text-xs font-medium border border-slate-200 transition-all text-left"
            >
              {p}
            </button>
          ))}
        </div>

        {/* Input Form */}
        <form onSubmit={handleSubmit} className="flex items-center space-x-2">
          <input
            type="text"
            value={text}
            onChange={(e) => setText(e.target.value)}
            disabled={disabled}
            placeholder={
              isHindi
                ? "स्वास्थ्य संबंधी प्रश्न पूछें (उदा. डेंगू के लक्षण, मलेरिया से बचाव)..."
                : "Ask a public health question (e.g. Dengue symptoms, TB guidelines)..."
            }
            className="flex-1 px-4 py-3 bg-slate-50 border border-slate-300 rounded-xl focus:outline-none focus:ring-2 focus:ring-emerald-500/50 focus:border-emerald-600 text-sm sm:text-base text-slate-900 placeholder:text-slate-400 transition-all"
          />

          <button
            type="submit"
            disabled={!text.trim() || disabled}
            className="px-5 py-3 bg-emerald-600 hover:bg-emerald-700 disabled:bg-slate-300 text-white rounded-xl font-bold shadow-sm transition-all flex items-center justify-center shrink-0"
          >
            <Send className="w-4 h-4 sm:mr-1.5" />
            <span className="hidden sm:inline text-sm">
              {isHindi ? 'पूछें' : 'Send'}
            </span>
          </button>
        </form>

        {/* Grounding and Medical Awareness Banner */}
        <p className="mt-2 text-[11px] text-center text-slate-400 flex items-center justify-center">
          <AlertCircle className="w-3 h-3 mr-1 text-emerald-600" />
          {isHindi
            ? 'हेल्थसूत्र केवल WHO और भारत सरकार के आधिकारिक दस्तावेजों से उत्तर देता है। यह चिकित्सीय सलाह नहीं है।'
            : 'HealthSutra answers strictly using verified WHO and Indian Government sources. For public awareness only.'}
        </p>

      </div>
    </div>
  );
}
