import React from 'react';
import { ExternalLink, CheckCircle, BookOpen } from 'lucide-react';

export default function SourceCard({ citation, onOpenEvidence }) {
  if (!citation) return null;

  return (
    <div className="mt-3 p-3.5 bg-emerald-50/70 border border-emerald-200/80 rounded-xl hover:bg-emerald-50 transition-all text-sm">
      <div className="flex items-start justify-between">
        <div className="flex items-center space-x-2">
          <span className="inline-flex items-center px-2 py-0.5 rounded-md text-xs font-bold bg-emerald-600 text-white">
            <CheckCircle className="w-3 h-3 mr-1" />
            {citation.organization || 'WHO / MoHFW'}
          </span>
          <span className="text-xs text-slate-500 font-medium">
            Page {citation.page || 1}
          </span>
        </div>

        {citation.source_url && (
          <a
            href={citation.source_url}
            target="_blank"
            rel="noopener noreferrer"
            className="text-xs text-emerald-700 hover:text-emerald-900 font-semibold flex items-center space-x-1"
          >
            <span>View Source</span>
            <ExternalLink className="w-3 h-3" />
          </a>
        )}
      </div>

      <h4 className="mt-1.5 font-bold text-slate-900 text-sm leading-snug">
        {citation.document_title}
      </h4>

      {citation.snippet && (
        <p className="mt-1.5 text-xs text-slate-600 italic bg-white/70 p-2 rounded-lg border border-emerald-100">
          "{citation.snippet}"
        </p>
      )}
    </div>
  );
}
