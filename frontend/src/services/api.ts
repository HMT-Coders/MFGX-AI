import type { InvestigationResponse } from '../types/investigation';

const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || 'http://127.0.0.1:8000';

export async function submitInvestigation(question: string): Promise<InvestigationResponse> {
  const trimmed = question.trim();
  if (!trimmed) {
    throw new Error('Please enter a question before submitting.');
  }

  try {
    const response = await fetch(`${API_BASE_URL}/investigate`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({ question: trimmed }),
    });

    const data = await response.json();

    if (!response.ok) {
      if (response.status === 400) {
        return {
          status: 'clarification_required',
          detail: data.detail || 'Could not identify target production line or date. Please specify line (e.g. L3) and date (e.g. August 4).',
        };
      }
      if (response.status === 404) {
        return {
          status: 'not_found',
          detail: data.detail || 'No factory records found matching your specified criteria.',
        };
      }
      throw new Error(data.detail || `Server error (${response.status})`);
    }

    return data as InvestigationResponse;
  } catch (error: any) {
    if (error.name === 'TypeError' && error.message.includes('fetch')) {
      throw new Error('Unable to connect to MFGX AI backend. Please check that the server is running at ' + API_BASE_URL);
    }
    throw error;
  }
}
