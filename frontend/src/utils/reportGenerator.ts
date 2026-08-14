import type { InvestigationData } from '../types/investigation';

export function generateInvestigationReport(investigation: InvestigationData) {
  const timestamp = new Date().toLocaleString('en-US', {
    dateStyle: 'full',
    timeStyle: 'medium'
  });

  const {
    investigation_question,
    investigation_scope,
    production_performance,
    major_downtime_events,
    maintenance_evidence,
    quality_evidence,
    relevant_sops,
    likely_contributing_factor,
    supporting_evidence,
    recommended_action,
    confidence,
    limitations
  } = investigation;

  const htmlContent = `
<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <title>MFGX AI - Production Investigation Report</title>
  <style>
    @media print {
      body {
        background: #ffffff !important;
        color: #000000 !important;
        font-size: 11pt;
      }
      .no-print {
        display: none !important;
      }
      .page-break {
        page-break-before: always;
      }
      .card {
        border: 1px solid #cccccc !important;
        box-shadow: none !important;
      }
    }

    body {
      font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Helvetica, Arial, sans-serif;
      color: #1e293b;
      background-color: #f8fafc;
      margin: 0;
      padding: 40px 20px;
    }

    .report-container {
      max-width: 900px;
      margin: 0 auto;
      background: #ffffff;
      padding: 40px;
      border: 1px solid #e2e8f0;
      border-radius: 8px;
      box-shadow: 0 4px 6px -1px rgba(0,0,0,0.05);
    }

    .header-table {
      width: 100%;
      border-bottom: 2px solid #0f172a;
      padding-bottom: 16px;
      margin-bottom: 24px;
    }

    .brand-title {
      font-size: 24px;
      font-weight: 800;
      color: #0f172a;
      letter-spacing: -0.5px;
      margin: 0;
    }

    .brand-subtitle {
      font-size: 13px;
      font-weight: 600;
      color: #2563eb;
      text-transform: uppercase;
      letter-spacing: 0.5px;
      margin-top: 2px;
    }

    .meta-box {
      text-align: right;
      font-size: 12px;
      color: #64748b;
    }

    .meta-badge {
      display: inline-block;
      padding: 4px 10px;
      border-radius: 4px;
      font-weight: 700;
      font-size: 11px;
      text-transform: uppercase;
      margin-bottom: 6px;
    }

    .badge-high { background: #dcfce7; color: #166534; border: 1px solid #86efac; }
    .badge-medium { background: #fef9c3; color: #854d0e; border: 1px solid #fde047; }
    .badge-low { background: #fee2e2; color: #991b1b; border: 1px solid #fca5a5; }

    .section-title {
      font-size: 14px;
      font-weight: 700;
      color: #0f172a;
      text-transform: uppercase;
      letter-spacing: 0.5px;
      border-bottom: 1px solid #cbd5e1;
      padding-bottom: 6px;
      margin-top: 28px;
      margin-bottom: 12px;
    }

    .question-box {
      background: #f1f5f9;
      border-left: 4px solid #2563eb;
      padding: 12px 16px;
      border-radius: 0 6px 6px 0;
      font-size: 15px;
      font-weight: 600;
      color: #0f172a;
      margin-bottom: 20px;
    }

    .summary-card {
      background: #eff6ff;
      border: 1px solid #bfdbfe;
      padding: 16px;
      border-radius: 6px;
      margin-bottom: 20px;
    }

    .summary-card h4 {
      margin: 0 0 6px 0;
      font-size: 13px;
      color: #1e40af;
      text-transform: uppercase;
    }

    .summary-card p {
      margin: 0;
      font-size: 14px;
      line-height: 1.5;
      color: #1e293b;
    }

    .rec-card {
      background: #f0fdf4;
      border: 1px solid #bbf7d0;
      padding: 16px;
      border-radius: 6px;
      margin-bottom: 20px;
    }

    .rec-card h4 {
      margin: 0 0 6px 0;
      font-size: 13px;
      color: #166534;
      text-transform: uppercase;
    }

    .rec-card p {
      margin: 0;
      font-size: 14px;
      line-height: 1.5;
      color: #14532d;
      font-weight: 500;
    }

    table {
      width: 100%;
      border-collapse: collapse;
      margin-bottom: 16px;
      font-size: 12px;
    }

    th {
      background-color: #f1f5f9;
      color: #334155;
      text-align: left;
      padding: 8px 12px;
      font-weight: 600;
      border: 1px solid #cbd5e1;
    }

    td {
      padding: 8px 12px;
      border: 1px solid #e2e8f0;
      color: #334155;
    }

    tr:nth-child(even) td {
      background-color: #f8fafc;
    }

    .source-tag {
      font-size: 10px;
      font-weight: 600;
      color: #64748b;
      background: #e2e8f0;
      padding: 2px 6px;
      border-radius: 3px;
      margin-left: 6px;
    }

    .sop-item {
      border: 1px solid #cbd5e1;
      border-radius: 6px;
      padding: 12px;
      margin-bottom: 10px;
      background: #ffffff;
    }

    .sop-header {
      display: flex;
      justify-content: space-between;
      font-weight: 700;
      font-size: 12px;
      color: #0f172a;
      margin-bottom: 4px;
    }

    .sop-relevance {
      font-size: 12px;
      color: #334155;
      margin-bottom: 6px;
    }

    .sop-excerpt {
      font-family: monospace;
      font-size: 11px;
      background: #f8fafc;
      padding: 8px;
      border: 1px solid #e2e8f0;
      border-radius: 4px;
      color: #475569;
      white-space: pre-wrap;
    }

    .evidence-list {
      padding-left: 20px;
      margin: 0 0 16px 0;
      font-size: 13px;
      color: #334155;
    }

    .evidence-list li {
      margin-bottom: 6px;
      line-height: 1.4;
    }

    .limitations-box {
      background: #fffbe6;
      border: 1px solid #ffe58f;
      padding: 12px 16px;
      border-radius: 6px;
      font-size: 12px;
      color: #722ed1;
    }

    .footer-text {
      margin-top: 36px;
      padding-top: 16px;
      border-top: 1px solid #e2e8f0;
      text-align: center;
      font-size: 11px;
      color: #94a3b8;
      font-family: monospace;
    }

    .btn-print {
      background: #2563eb;
      color: #ffffff;
      border: none;
      padding: 10px 20px;
      border-radius: 6px;
      font-weight: 600;
      font-size: 13px;
      cursor: pointer;
      margin-bottom: 20px;
    }
  </style>
</head>
<body>

  <div class="report-container">
    <div class="no-print" style="text-align: right;">
      <button class="btn-print" onclick="window.print()">🖨️ Print / Save as PDF</button>
    </div>

    <table class="header-table">
      <tr>
        <td>
          <div class="brand-title">MFGX AI</div>
          <div class="brand-subtitle">Production Investigation Report</div>
        </td>
        <td class="meta-box">
          <div class="meta-badge badge-${confidence.toLowerCase()}">${confidence} Confidence</div>
          <div><strong>Generated:</strong> ${timestamp}</div>
          <div><strong>Scope:</strong> Line ${investigation_scope.line} | Date: ${investigation_scope.date}</div>
        </td>
      </tr>
    </table>

    <div class="question-box">
      Investigated Issue: "${investigation_question}"
    </div>

    <div class="summary-card">
      <h4>Likely Contributing Factor (AI Assessment)</h4>
      <p>${likely_contributing_factor}</p>
    </div>

    <div class="rec-card">
      <h4>Recommended Supervisor Action</h4>
      <p>${recommended_action}</p>
    </div>

    <div class="section-title">
      Production Performance <span class="source-tag">Source: Production Data CSV</span>
    </div>
    ${production_performance ? `
    <table>
      <thead>
        <tr>
          <th>Target Quantity</th>
          <th>Actual Quantity</th>
          <th>Shortfall</th>
          <th>Shortfall Rate</th>
        </tr>
      </thead>
      <tbody>
        <tr>
          <td><strong>${production_performance.target?.toLocaleString()}</strong></td>
          <td>${production_performance.actual?.toLocaleString()}</td>
          <td style="color: #dc2626; font-weight: bold;">-${production_performance.shortfall?.toLocaleString()}</td>
          <td style="color: #d97706; font-weight: bold;">${production_performance.shortfall_percentage?.toFixed(2)}%</td>
        </tr>
      </tbody>
    </table>
    ` : '<p style="font-size:12px; color:#64748b;">No production metrics available.</p>'}

    <div class="section-title">
      Major Downtime Stoppages <span class="source-tag">Source: Downtime Data CSV</span>
    </div>
    ${major_downtime_events && major_downtime_events.length > 0 ? `
    <table>
      <thead>
        <tr>
          <th>Machine ID</th>
          <th>Start Time</th>
          <th>Duration</th>
          <th>Reason</th>
          <th>Category</th>
        </tr>
      </thead>
      <tbody>
        ${major_downtime_events.map(d => `
        <tr>
          <td><strong>${d.machine_id}</strong></td>
          <td>${d.start_time || 'N/A'}</td>
          <td><strong>${d.duration_minutes} mins</strong></td>
          <td>${d.reason}</td>
          <td>${d.category}</td>
        </tr>
        `).join('')}
      </tbody>
    </table>
    ` : '<p style="font-size:12px; color:#64748b;">No major downtime events recorded.</p>'}

    <div class="section-title">
      Historical Maintenance Evidence <span class="source-tag">Source: Maintenance Data CSV</span>
    </div>
    ${maintenance_evidence && maintenance_evidence.length > 0 ? `
    <table>
      <thead>
        <tr>
          <th>Date</th>
          <th>Machine</th>
          <th>Reported Problem</th>
          <th>Maintenance Action</th>
          <th>Status</th>
        </tr>
      </thead>
      <tbody>
        ${maintenance_evidence.map(m => `
        <tr>
          <td>${m.date}</td>
          <td><strong>${m.machine_id}</strong></td>
          <td>${m.reported_problem}</td>
          <td>${m.maintenance_action}</td>
          <td><span style="font-weight:600; color:${m.status?.toLowerCase().includes('pending') ? '#d97706' : '#166534'}">${m.status}</span></td>
        </tr>
        `).join('')}
      </tbody>
    </table>
    ` : '<p style="font-size:12px; color:#64748b;">No prior maintenance logs found.</p>'}

    <div class="section-title">
      Quality Inspection Findings <span class="source-tag">Source: Quality Data CSV</span>
    </div>
    ${quality_evidence ? `
    <table>
      <thead>
        <tr>
          <th>Total Inspected</th>
          <th>Total Rejected</th>
          <th>Rejection Rate</th>
          <th>Primary Defect Types</th>
        </tr>
      </thead>
      <tbody>
        <tr>
          <td>${quality_evidence.total_produced?.toLocaleString()}</td>
          <td style="color: #dc2626; font-weight: bold;">${quality_evidence.total_rejected?.toLocaleString()}</td>
          <td style="color: #dc2626; font-weight: bold;">${quality_evidence.rejection_rate?.toFixed(2)}%</td>
          <td>${quality_evidence.defect_types?.join(', ') || 'N/A'}</td>
        </tr>
      </tbody>
    </table>
    ` : '<p style="font-size:12px; color:#64748b;">No quality inspection data available.</p>'}

    <div class="section-title">
      SOP Guidance Traceability <span class="source-tag">Source: Vector SOP RAG</span>
    </div>
    ${relevant_sops && relevant_sops.length > 0 ? relevant_sops.map(sop => `
      <div class="sop-item">
        <div class="sop-header">
          <span>${sop.sop_id} — ${sop.source}</span>
          <span>Page ${sop.page}</span>
        </div>
        <div class="sop-relevance">${sop.relevance}</div>
        ${sop.text ? `<div class="sop-excerpt">${sop.text}</div>` : ''}
      </div>
    `).join('') : '<p style="font-size:12px; color:#64748b;">No specific SOP documents retrieved.</p>'}

    <div class="section-title">
      Verified Evidence List
    </div>
    <ol class="evidence-list">
      ${supporting_evidence.map(item => `<li>${item}</li>`).join('')}
    </ol>

    ${limitations && limitations.length > 0 ? `
    <div class="section-title">
      Dataset Scope & Model Limitations
    </div>
    <div class="limitations-box">
      <ul style="margin:0; padding-left:18px;">
        ${limitations.map(l => `<li>${l}</li>`).join('')}
      </ul>
    </div>
    ` : ''}

    <div class="footer-text">
      MFGX AI • Production Investigation Copilot • Verified Synthetic Factory Investigation Environment
    </div>
  </div>

</body>
</html>
  `;

  const reportWindow = window.open('', '_blank');
  if (reportWindow) {
    reportWindow.document.write(htmlContent);
    reportWindow.document.close();
  } else {
    alert('Pop-up blocked. Please allow pop-ups for this site to view the generated investigation report.');
  }
}
