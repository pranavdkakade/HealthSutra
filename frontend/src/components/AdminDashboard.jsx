import React, { useEffect, useState } from 'react';
import { fetchAdminAnalytics } from '../services/api';

const toPct = (v) => `${(100 * (v || 0)).toFixed(1)}%`;

export default function AdminDashboard({ language }) {
  const isHindi = language === 'hi';
  const [data, setData] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');

  useEffect(() => {
    let mounted = true;
    fetchAdminAnalytics()
      .then((resp) => {
        if (!mounted) return;
        setData(resp);
      })
      .catch(() => {
        if (!mounted) return;
        setError(isHindi ? 'एडमिन डेटा लोड नहीं हो सका।' : 'Failed to load admin analytics.');
      })
      .finally(() => {
        if (mounted) setLoading(false);
      });

    return () => {
      mounted = false;
    };
  }, [isHindi]);

  if (loading) {
    return <div className="max-w-5xl mx-auto px-4 sm:px-6 py-8 text-slate-600">{isHindi ? 'लोड हो रहा है...' : 'Loading admin analytics...'}</div>;
  }

  if (error) {
    return <div className="max-w-5xl mx-auto px-4 sm:px-6 py-8 text-rose-700">{error}</div>;
  }

  const totals = data?.totals || {};
  const rates = data?.rates || {};
  const perf = data?.performance || {};
  const traffic = data?.traffic_last_7_days || [];

  return (
    <div className="max-w-5xl mx-auto px-4 sm:px-6 py-8">
      <h2 className="text-2xl sm:text-3xl font-extrabold text-slate-900 mb-6">
        {isHindi ? 'एडमिन एनालिटिक्स डैशबोर्ड' : 'Admin Analytics Dashboard'}
      </h2>

      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4 mb-6">
        <div className="bg-white border border-slate-200 rounded-xl p-4"><p className="text-xs text-slate-500">{isHindi ? 'कुल प्रश्न' : 'Total Queries'}</p><p className="text-2xl font-bold text-slate-900">{totals.queries || 0}</p></div>
        <div className="bg-white border border-slate-200 rounded-xl p-4"><p className="text-xs text-slate-500">{isHindi ? 'उत्तर दिए गए' : 'Answered'}</p><p className="text-2xl font-bold text-emerald-700">{totals.answered || 0}</p></div>
        <div className="bg-white border border-slate-200 rounded-xl p-4"><p className="text-xs text-slate-500">{isHindi ? 'रिफ्यूज किए गए' : 'Refused'}</p><p className="text-2xl font-bold text-amber-700">{totals.refused || 0}</p></div>
        <div className="bg-white border border-slate-200 rounded-xl p-4"><p className="text-xs text-slate-500">{isHindi ? 'इमरजेंसी फ्लैग' : 'Emergency Alerts'}</p><p className="text-2xl font-bold text-rose-700">{totals.emergency_alerts || 0}</p></div>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-4 mb-6">
        <div className="bg-white border border-slate-200 rounded-xl p-4">
          <h3 className="font-bold text-slate-900 mb-3">{isHindi ? 'दरें' : 'Rates'}</h3>
          <p className="text-sm text-slate-700">{isHindi ? 'उत्तर दर' : 'Answer Rate'}: <span className="font-semibold">{toPct(rates.answer_rate)}</span></p>
          <p className="text-sm text-slate-700">{isHindi ? 'रिफ्यूजल दर' : 'Refusal Rate'}: <span className="font-semibold">{toPct(rates.refusal_rate)}</span></p>
          <p className="text-sm text-slate-700">{isHindi ? 'सहायक फीडबैक दर' : 'Helpful Feedback Rate'}: <span className="font-semibold">{toPct(rates.helpful_feedback_rate)}</span></p>
        </div>

        <div className="bg-white border border-slate-200 rounded-xl p-4">
          <h3 className="font-bold text-slate-900 mb-3">{isHindi ? 'प्रदर्शन' : 'Performance'}</h3>
          <p className="text-sm text-slate-700">{isHindi ? 'औसत विलंबता (ms)' : 'Average Latency (ms)'}: <span className="font-semibold">{(perf.avg_latency_ms || 0).toFixed(2)}</span></p>
          <p className="text-sm text-slate-700">{isHindi ? 'औसत समानता स्कोर' : 'Average Similarity Score'}: <span className="font-semibold">{(perf.avg_top_similarity_score || 0).toFixed(3)}</span></p>
          <p className="text-sm text-slate-700">{isHindi ? 'कुल फीडबैक' : 'Total Feedback'}: <span className="font-semibold">{totals.feedback_total || 0}</span></p>
        </div>
      </div>

      <div className="bg-white border border-slate-200 rounded-xl p-4">
        <h3 className="font-bold text-slate-900 mb-3">{isHindi ? 'पिछले 7 दिनों का ट्रैफिक' : 'Traffic Last 7 Days'}</h3>
        {traffic.length === 0 ? (
          <p className="text-sm text-slate-600">{isHindi ? 'अभी कोई ट्रैफिक डेटा उपलब्ध नहीं है।' : 'No traffic data available yet.'}</p>
        ) : (
          <div className="space-y-2">
            {traffic.map((row) => (
              <div key={row.date} className="flex items-center justify-between text-sm border-b border-slate-100 pb-2">
                <span className="text-slate-600">{row.date}</span>
                <span className="font-semibold text-slate-900">{row.count}</span>
              </div>
            ))}
          </div>
        )}
      </div>
    </div>
  );
}
