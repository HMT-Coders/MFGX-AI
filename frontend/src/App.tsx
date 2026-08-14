import React, { useState } from 'react';
import { submitInvestigation } from './services/api';
import type { InvestigationData } from './types/investigation';
import { generateInvestigationReport } from './utils/reportGenerator';
import { Header } from './components/Header';
import { InvestigationInput } from './components/InvestigationInput';
import { ProductionCard } from './components/ProductionCard';
import { DowntimeSection } from './components/DowntimeSection';
import { MaintenanceSection } from './components/MaintenanceSection';
import { QualitySection } from './components/QualitySection';
import { SopEvidence } from './components/SopEvidence';
import { ContributingFactor } from './components/ContributingFactor';
import { EvidenceList } from './components/EvidenceList';
import { Recommendation } from './components/Recommendation';
import { ConfidenceBadge } from './components/ConfidenceBadge';
import { Limitations } from './components/Limitations';
import { LoadingState } from './components/LoadingState';
import { ErrorBanner } from './components/ErrorBanner';
import { ScopeGuidance } from './components/ScopeGuidance';
import { EmptyState } from './components/EmptyState';
import { Calendar, MapPin, FileSpreadsheet, Printer } from 'lucide-react';

export const App: React.FC = () => {
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [notice, setNotice] = useState<{ message: string; type: 'clarification' | 'not_found' } | null>(null);
  const [investigation, setInvestigation] = useState<InvestigationData | null>(null);

  const handleInvestigate = async (question: string) => {
    setIsLoading(true);
    setError(null);
    setNotice(null);

    try {
      const response = await submitInvestigation(question);

      if (response.status === 'clarification_required') {
        setNotice({
          message: response.detail || 'Please specify a target production line (L1–L4) or machine ID (e.g. M301).',
          type: 'clarification'
        });
        setInvestigation(null);
      } else if (response.status === 'not_found') {
        setNotice({
          message: response.detail || 'No factory records found matching your specified query scope.',
          type: 'not_found'
        });
        setInvestigation(null);
      } else if (response.investigation) {
        setInvestigation(response.investigation);
      } else {
        setError('Received incomplete investigation payload from backend server.');
      }
    } catch (err: any) {
      setError(err.message || 'An unexpected error occurred while communicating with the backend.');
      setInvestigation(null);
    } finally {
      setIsLoading(false);
    }
  };

  const handleGenerateReport = () => {
    if (investigation) {
      generateInvestigationReport(investigation);
    }
  };

  const scopeLine = investigation?.investigation_scope?.line || '';
  const displayScopeTag = scopeLine.startsWith('Machine') || scopeLine.startsWith('M')
    ? (scopeLine.startsWith('Machine') ? scopeLine : `Machine ${scopeLine}`)
    : `Line ${scopeLine}`;

  return (
    <div className="min-h-screen bg-slate-950 text-slate-100 flex flex-col font-sans antialiased selection:bg-blue-600 selection:text-white">
      <Header />

      <main className="flex-1 max-w-7xl w-full mx-auto px-4 sm:px-6 py-6 space-y-6">
        <InvestigationInput onInvestigate={handleInvestigate} isLoading={isLoading} />

        {isLoading && <LoadingState />}

        {error && !isLoading && (
          <ErrorBanner message={error} onRetry={() => setError(null)} />
        )}

        {notice && !isLoading && (
          <ScopeGuidance 
            message={notice.message} 
            type={notice.type} 
            onSelectPreset={(q) => handleInvestigate(q)} 
          />
        )}

        {!isLoading && !error && !notice && !investigation && (
          <EmptyState onSelectPreset={(q) => handleInvestigate(q)} />
        )}

        {!isLoading && investigation && (
          <div className="space-y-6 animate-fadeIn">
            {/* Investigation Meta Header & Report Trigger */}
            <div className="bg-slate-900 border border-slate-800 rounded-xl p-5 shadow-lg flex flex-col md:flex-row md:items-center justify-between gap-4">
              <div>
                <div className="flex items-center space-x-2 mb-1">
                  <span className="bg-blue-900/60 text-blue-300 text-xs font-mono font-bold px-2.5 py-0.5 rounded border border-blue-700/50 flex items-center space-x-1">
                    <MapPin className="h-3.5 w-3.5" />
                    <span>{displayScopeTag}</span>
                  </span>
                  <span className="bg-slate-800 text-slate-300 text-xs font-mono font-bold px-2.5 py-0.5 rounded border border-slate-700 flex items-center space-x-1">
                    <Calendar className="h-3.5 w-3.5 text-slate-400" />
                    <span>{investigation.investigation_scope?.date}</span>
                  </span>
                </div>
                <h2 className="text-base font-semibold text-slate-100 mt-2">
                  "{investigation.investigation_question}"
                </h2>
              </div>

              <div className="flex items-center space-x-3 self-start md:self-center flex-shrink-0">
                <ConfidenceBadge confidence={investigation.confidence} />
                
                <button
                  type="button"
                  onClick={handleGenerateReport}
                  className="flex items-center space-x-2 bg-blue-600 hover:bg-blue-500 text-white text-xs font-semibold px-4 py-2 rounded-lg transition-colors shadow-md border border-blue-400/30 cursor-pointer"
                >
                  <FileSpreadsheet className="h-4 w-4" />
                  <span>Generate Investigation Report</span>
                  <Printer className="h-3.5 w-3.5 text-blue-200" />
                </button>
              </div>
            </div>

            {/* AI Assessment & Recommendation Block */}
            <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
              <ContributingFactor factor={investigation.likely_contributing_factor} />
              <Recommendation action={investigation.recommended_action} />
            </div>

            {/* Production Performance Metrics */}
            {investigation.production_performance && investigation.production_performance.target > 0 && (
              <ProductionCard data={investigation.production_performance} />
            )}

            {/* Operational Fact Grid: Downtime & Maintenance */}
            {(investigation.major_downtime_events?.length > 0 || investigation.maintenance_evidence?.length > 0) && (
              <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
                <DowntimeSection events={investigation.major_downtime_events} />
                <MaintenanceSection records={investigation.maintenance_evidence} />
              </div>
            )}

            {/* Quality & Supporting Evidence */}
            <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
              {investigation.quality_evidence && investigation.quality_evidence.total_produced > 0 && (
                <QualitySection data={investigation.quality_evidence} />
              )}
              {investigation.supporting_evidence?.length > 0 && (
                <EvidenceList evidence={investigation.supporting_evidence} />
              )}
            </div>

            {/* Standard Operating Procedures (SOP) Evidence */}
            {investigation.relevant_sops?.length > 0 && (
              <SopEvidence sops={investigation.relevant_sops} />
            )}

            {/* Limitations & Data Scope Disclaimer */}
            <Limitations limitations={investigation.limitations} />
          </div>
        )}
      </main>

      <footer className="bg-slate-900/80 border-t border-slate-800 py-4 px-6 text-center text-xs text-slate-500 font-mono mt-auto">
        MFGX AI • Synthetic Factory Investigation Environment
      </footer>
    </div>
  );
};
