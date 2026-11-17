import React, { useState, useEffect } from 'react';
import { FileText, CheckCircle, ExternalLink, Search, RefreshCw, Shield } from 'lucide-react';
import { fetchDocuments } from '../services/api';

export default function DocumentsView({ language }) {
  const isHindi = language === 'hi';
  const [documents, setDocuments] = useState([]);
  const [loading, setLoading] = useState(true);
  const [searchTerm, setSearchTerm] = useState('');

  const loadDocs = async () => {
    setLoading(true);
    try {
      const data = await fetchDocuments();
      setDocuments(data.documents || []);
    } catch (err) {
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    loadDocs();
  }, []);

  const filtered = documents.filter(d => 
    d.title.toLowerCase().includes(searchTerm.toLowerCase()) ||
    d.organization.toLowerCase().includes(searchTerm.toLowerCase()) ||
    (d.disease_category && d.disease_category.toLowerCase().includes(searchTerm.toLowerCase()))
  );

  return (
    <div className="max-w-5xl mx-auto px-4 sm:px-6 py-8">
      
      {/* Header */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4 mb-6">
        <div>
          <h2 className="text-2xl font-extrabold text-slate-900 flex items-center">
            <Shield className="w-6 h-6 mr-2 text-emerald-600" />
            {isHindi ? 'सत्यापित स्वास्थ्य दस्तावेज़ संग्रह' : 'Approved Health Documents Registry'}
          </h2>
          <p className="text-sm text-slate-500 mt-1">
            {isHindi
              ? 'हेल्थसूत्र केवल इन आधिकारिक सरकारी और विश्व स्वास्थ्य संगठन (WHO) दस्तावेजों से उत्तर प्रदान करता है।'
              : 'Every answer is grounded in this verified knowledge base. Unapproved sources are strictly barred.'}
          </p>
        </div>

        <button
          onClick={loadDocs}
          className="px-3 py-2 bg-slate-100 hover:bg-slate-200 text-slate-700 rounded-xl text-xs font-semibold flex items-center space-x-1.5 self-start sm:self-auto"
        >
          <RefreshCw className={`w-3.5 h-3.5 ${loading ? 'animate-spin' : ''}`} />
          <span>{isHindi ? 'ताज़ा करें' : 'Refresh'}</span>
        </button>
      </div>

      {/* Search Input */}
      <div className="relative mb-6">
        <Search className="w-4 h-4 text-slate-400 absolute left-3.5 top-3.5" />
        <input
          type="text"
          value={searchTerm}
          onChange={(e) => setSearchTerm(e.target.value)}
          placeholder={isHindi ? "दस्तावेज़ या बीमारी खोजें..." : "Filter by disease, title or organization..."}
          className="w-full pl-10 pr-4 py-2.5 bg-white border border-slate-300 rounded-xl text-sm focus:outline-none focus:ring-2 focus:ring-emerald-500/50"
        />
      </div>

      {/* Grid of Documents */}
      {loading ? (
        <div className="text-center py-12 text-slate-400 text-sm">
          {isHindi ? 'दस्तावेज़ लोड हो रहे हैं...' : 'Loading verified documents...'}
        </div>
      ) : filtered.length === 0 ? (
        <div className="text-center py-12 text-slate-400 text-sm">
          {isHindi ? 'कोई दस्तावेज़ नहीं मिला।' : 'No verified documents found matching your filter.'}
        </div>
      ) : (
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          {filtered.map((doc) => (
            <div
              key={doc.id}
              className="p-5 bg-white border border-slate-200 rounded-2xl shadow-xs hover:border-emerald-300 hover:shadow-md transition-all flex flex-col justify-between"
            >
              <div>
                <div className="flex items-center justify-between mb-2">
                  <span className={`inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-extrabold ${
                    doc.organization === 'WHO'
                      ? 'bg-blue-100 text-blue-800'
                      : 'bg-emerald-100 text-emerald-800'
                  }`}>
                    {doc.organization}
                  </span>
                  
                  <span className="inline-flex items-center text-xs text-emerald-600 font-semibold">
                    <CheckCircle className="w-3.5 h-3.5 mr-1" />
                    Verified Official
                  </span>
                </div>

                <h3 className="text-base font-bold text-slate-900 leading-snug">
                  {doc.title}
                </h3>

                <div className="mt-2 text-xs text-slate-500 space-y-1">
                  <p><span className="font-semibold text-slate-700">Category:</span> {doc.disease_category || 'General Health'}</p>
                  <p><span className="font-semibold text-slate-700">Published:</span> {doc.publication_date || 'Official Guidance'}</p>
                  <p><span className="font-semibold text-slate-700">Document Type:</span> {doc.document_type}</p>
                  <p><span className="font-semibold text-slate-700">Indexed Chunks:</span> {doc.chunks_count || 'Active'}</p>
                </div>
              </div>

              <div className="mt-4 pt-3 border-t border-slate-100 flex items-center justify-between">
                <span className="text-[11px] text-slate-400 font-mono">
                  ID: {doc.id}
                </span>

                {doc.source_url && (
                  <a
                    href={doc.source_url}
                    target="_blank"
                    rel="noopener noreferrer"
                    className="text-xs font-semibold text-emerald-600 hover:text-emerald-800 flex items-center space-x-1"
                  >
                    <span>Official Portal</span>
                    <ExternalLink className="w-3 h-3" />
                  </a>
                )}
              </div>
            </div>
          ))}
        </div>
      )}

    </div>
  );
}
