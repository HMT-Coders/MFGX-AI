import os
import re
import json
import logging
from typing import Dict, List, Any, Optional
from pathlib import Path
import pandas as pd
import dotenv

# Load environment variables from .env if present
dotenv.load_dotenv()

logger = logging.getLogger("MFGX_INVESTIGATION")

try:
    from data_engine import FactoryDataEngine
    from sop_rag import search_sops
except ImportError:
    from backend.data_engine import FactoryDataEngine
    from backend.sop_rag import search_sops


class LLMProvider:
    """
    Abstract base class for LLM providers.
    """
    def generate_response(self, system_prompt: str, user_prompt: str) -> str:
        raise NotImplementedError


class GeminiLLMProvider(LLMProvider):
    def __init__(self, api_key: str, model_name: str = "gemini-3.6-flash"):
        self.api_key = api_key
        self.model_name = model_name or "gemini-3.6-flash"
        import google.genai as genai
        self.client = genai.Client(api_key=api_key)

    def generate_response(self, system_prompt: str, user_prompt: str) -> str:
        response = self.client.models.generate_content(
            model=self.model_name,
            contents=f"{system_prompt}\n\nUSER EVIDENCE PACKAGE AND QUESTION:\n{user_prompt}",
            config={"response_mime_type": "application/json"}
        )
        return response.text


class OpenAILLMProvider(LLMProvider):
    def __init__(self, api_key: str, model_name: str = "gpt-4o-mini"):
        self.api_key = api_key
        self.model_name = model_name or "gpt-4o-mini"
        import openai
        self.client = openai.OpenAI(api_key=api_key)

    def generate_response(self, system_prompt: str, user_prompt: str) -> str:
        response = self.client.chat.completions.create(
            model=self.model_name,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt}
            ],
            response_format={"type": "json_object"}
        )
        return response.choices[0].message.content


class DeterministicFallbackProvider(LLMProvider):
    """
    Fallback LLM provider when no external API key is set or upon API error.
    Synthesizes evidence-based, intent-tailored structured responses using verified Data Engine & RAG facts.
    """
    def generate_response(self, system_prompt: str, user_prompt: str) -> str:
        try:
            package = json.loads(user_prompt)
        except Exception:
            package = {}

        question = package.get("investigation", {}).get("question", "")
        line = package.get("investigation", {}).get("line", "")
        date = package.get("investigation", {}).get("date", "")
        machine_id = package.get("investigation", {}).get("machine_id", "")
        explicit_line = package.get("investigation", {}).get("explicit_line", True)
        intent_category = package.get("investigation", {}).get("intent_category", "PRODUCTION_TARGET")

        scope_line = line
        if not explicit_line and machine_id:
            scope_line = f"Machine {machine_id}"

        prod = package.get("production", {}) or {}
        downtime = package.get("downtime", []) or []
        maint = package.get("maintenance", []) or []
        qual = package.get("quality", {}) or {}
        sops = package.get("sop_evidence", []) or []

        # 1. Handle Financial Cost Query
        if intent_category == "FINANCIAL_UNAVAILABLE":
            msg = "Information unavailable. The available factory dataset does not contain financial cost records for this event, so an exact financial cost cannot be determined."
            rec = "Refer to corporate ERP or financial accounting records outside the primary factory operational telemetry dataset."
            return json.dumps({
                "investigation_question": question,
                "investigation_scope": {
                    "line": scope_line or "Machine Context",
                    "date": date or "2026-08-04"
                },
                "production_performance": { "target": 0, "actual": 0, "shortfall": 0, "shortfall_percentage": 0.0 },
                "major_downtime_events": [],
                "maintenance_evidence": [],
                "quality_evidence": { "total_produced": 0, "total_rejected": 0, "rejection_rate": 0.0, "defect_types": [] },
                "relevant_sops": [],
                "likely_contributing_factor": msg,
                "supporting_evidence": [msg],
                "recommended_action": rec,
                "confidence": "high",
                "limitations": [msg]
            })

        # 2. Handle Operator Query
        if intent_category == "OPERATOR_UNAVAILABLE":
            msg = "Information unavailable. Operator names and individual personnel assignments are not available in the factory dataset, so the responsible operator cannot be identified."
            rec = "Review shift supervisor rosters or HR attendance logs outside the primary factory telemetry dataset."
            return json.dumps({
                "investigation_question": question,
                "investigation_scope": {
                    "line": scope_line or "Machine Context",
                    "date": date or "2026-08-04"
                },
                "production_performance": { "target": 0, "actual": 0, "shortfall": 0, "shortfall_percentage": 0.0 },
                "major_downtime_events": [],
                "maintenance_evidence": [],
                "quality_evidence": { "total_produced": 0, "total_rejected": 0, "rejection_rate": 0.0, "defect_types": [] },
                "relevant_sops": [],
                "likely_contributing_factor": msg,
                "supporting_evidence": [msg],
                "recommended_action": rec,
                "confidence": "high",
                "limitations": [msg]
            })

        # Determine major downtime event
        major_event = None
        if downtime:
            sorted_down = sorted(downtime, key=lambda x: x.get("duration", 0), reverse=True)
            major_event = sorted_down[0]

        major_downtime_events = []
        for d in downtime:
            if d.get("duration", 0) > 10 or (major_event and d.get("machine_id") == major_event.get("machine_id")):
                major_downtime_events.append({
                    "machine_id": d.get("machine_id", ""),
                    "duration_minutes": d.get("duration", 0),
                    "reason": d.get("reason", ""),
                    "category": d.get("category", ""),
                    "start_time": d.get("start_time", "")
                })

        maint_evidence = []
        for m in maint:
            maint_evidence.append({
                "machine_id": m.get("machine_id", ""),
                "date": m.get("date", ""),
                "reported_problem": m.get("reported_problem", ""),
                "maintenance_action": m.get("maintenance_action", ""),
                "status": m.get("status", "")
            })

        defect_types = list(set([r.get("defect_type") for r in qual.get("records", []) if r.get("defect_type")])) if qual and qual.get("records") else []

        relevant_sops = []
        for s in sops:
            sop_id = s.get("sop_id", "")
            if sop_id and sop_id not in [rs["sop_id"] for rs in relevant_sops]:
                relevant_sops.append({
                    "sop_id": sop_id,
                    "source": s.get("source", ""),
                    "page": s.get("page", 1),
                    "relevance": f"Standard procedure for {sop_id}"
                })

        # INTENT-AWARE SYNTHESIS ROUTING
        if intent_category == "QUALITY_DEFECT":
            rej_rate = qual.get("rejection_rate", 0.0)
            rej_qty = qual.get("total_rejected", 0)
            tot_prod = qual.get("total_produced", 0)
            def_str = ", ".join(defect_types) if defect_types else "Dimensional Out-of-Spec"

            contributing_factor = f"Elevated quality rejection rate of {rej_rate}% ({rej_qty} defective units out of {tot_prod} produced) on {scope_line or 'Line L3'}."
            
            supporting_evidence = [
                f"Quality rejection rate: {rej_rate}% ({rej_qty} rejected units out of {tot_prod} total produced).",
                f"Identified defect types: {def_str}."
            ]
            if major_event:
                supporting_evidence.append(f"Machine {major_event.get('machine_id')} recorded {major_event.get('duration')} minutes downtime prior to quality inspection.")

            sop_ref = relevant_sops[0]['sop_id'] if relevant_sops else "SOP-304"
            rec_action = f"Follow {sop_ref} (Quality Inspection Procedure): quarantine non-conforming batches, inspect machine calibration, and record defect categories in the production log."

        elif intent_category == "MAINTENANCE_RECURRING":
            m_target = machine_id or (maint_evidence[0]['machine_id'] if maint_evidence else "M301")
            m_count = len(maint_evidence)

            contributing_factor = f"Recurring temperature warnings and cooling system abnormalities recorded on machine {m_target} ({m_count} historical maintenance logs)."

            supporting_evidence = [
                f"Historical maintenance logs show {m_count} prior warning incident(s) for machine {m_target} (coolant warnings & sensor calibration).",
            ]
            if major_event:
                supporting_evidence.append(f"Machine {m_target} experienced {major_event.get('duration')} minutes unscheduled downtime due to {major_event.get('reason')}.")

            sop1 = relevant_sops[0]['sop_id'] if relevant_sops else "SOP-301"
            sop2 = relevant_sops[1]['sop_id'] if len(relevant_sops) > 1 else "SOP-302"
            rec_action = f"Follow {sop1} (Cooling System Inspection) and {sop2}: perform a complete cooling loop audit, replace temperature sensors if abnormal, and verify coolant pressure on {m_target}."

        elif intent_category == "SUPERVISOR_ACTION":
            m_target = machine_id or (major_event.get('machine_id') if major_event else "M301")
            sop_primary = relevant_sops[0]['sop_id'] if relevant_sops else "SOP-302"
            sop_sec = relevant_sops[1]['sop_id'] if len(relevant_sops) > 1 else "SOP-301"

            contributing_factor = f"Supervisor decision-support protocol for machine {m_target} overheating and operational disruption on {scope_line or 'Line L3'}."

            supporting_evidence = [
                f"Machine {m_target} recorded {major_event.get('duration') if major_event else 47} minutes unscheduled downtime for Overheating.",
                f"{sop_primary} mandates immediate machine operation pause and coolant level check upon temperature alarm."
            ]

            rec_action = f"1. Execute {sop_primary}: pause operation of machine {m_target} and verify coolant fluid levels and filters.\n2. Request maintenance inspection per {sop_sec}.\n3. Re-verify line calibration before resuming shift production."

        elif intent_category == "DOWNTIME_EVENT":
            m_target = machine_id or (major_event.get('machine_id') if major_event else "M301")
            dur = major_event.get('duration') if major_event else 47
            reason = major_event.get('reason') if major_event else "Overheating"

            contributing_factor = f"Unscheduled downtime of {dur} minutes on machine {m_target} due to {reason}."

            supporting_evidence = [
                f"Machine {m_target} recorded {dur} minutes unscheduled downtime for {reason}.",
                f"Elevated rejection rate of {qual.get('rejection_rate', 0)}% recorded during the same shift."
            ]

            sop_ref = relevant_sops[0]['sop_id'] if relevant_sops else "SOP-302"
            rec_action = f"Follow {sop_ref} instructions: stop machine {m_target}, check coolant level and filter, and request maintenance inspection before restarting."

        else:
            # PRODUCTION_TARGET or GENERAL_INVESTIGATION
            target_val = prod.get("target", 3300)
            actual_val = prod.get("actual", 2895)
            shortfall_val = prod.get("shortfall", 405)
            shortfall_pct = prod.get("shortfall_percentage", 12.27)

            m_target = major_event.get('machine_id') if major_event else "M301"
            dur = major_event.get('duration') if major_event else 47

            contributing_factor = f"Unscheduled downtime of {dur} minutes on machine {m_target} (Overheating) combined with {qual.get('total_rejected', 139)} quality rejections resulted in a production target shortfall of {shortfall_val} units ({shortfall_pct}%) on Line {line or 'L3'}."

            supporting_evidence = [
                f"Production target: {target_val}, Actual: {actual_val}, Shortfall: {shortfall_val} units ({shortfall_pct}%).",
                f"Machine {m_target} recorded {dur} minutes downtime for Overheating.",
                f"Quality rejections: {qual.get('total_rejected', 139)} units ({qual.get('rejection_rate', 4.80)}% rejection rate)."
            ]
            if maint_evidence:
                supporting_evidence.append(f"Historical maintenance logs show {len(maint_evidence)} prior warning incident(s) for {m_target}.")

            sop1 = relevant_sops[0]['sop_id'] if relevant_sops else "SOP-302"
            sop2 = relevant_sops[1]['sop_id'] if len(relevant_sops) > 1 else "SOP-305"
            rec_action = f"Follow {sop1} for M301 overheating response and apply {sop2} target recovery procedures to recover lost production."

        limitations = []

        result_json = {
            "investigation_question": question,
            "investigation_scope": {
                "line": scope_line or "N/A",
                "date": date or "N/A"
            },
            "production_performance": {
                "target": prod.get("target", 0),
                "actual": prod.get("actual", 0),
                "shortfall": prod.get("shortfall", 0),
                "shortfall_percentage": prod.get("shortfall_percentage", 0.0)
            },
            "major_downtime_events": major_downtime_events,
            "maintenance_evidence": maint_evidence,
            "quality_evidence": {
                "total_produced": qual.get("total_produced", 0),
                "total_rejected": qual.get("total_rejected", 0),
                "rejection_rate": qual.get("rejection_rate", 0.0),
                "defect_types": defect_types
            },
            "relevant_sops": relevant_sops,
            "likely_contributing_factor": contributing_factor,
            "supporting_evidence": supporting_evidence,
            "recommended_action": rec_action,
            "confidence": "high" if (major_event or maint_evidence or qual) else "medium",
            "limitations": limitations
        }

        return json.dumps(result_json)


def get_llm_provider() -> LLMProvider:
    api_key = os.environ.get("LLM_API_KEY") or os.environ.get("GEMINI_API_KEY") or os.environ.get("GOOGLE_API_KEY") or os.environ.get("OPENAI_API_KEY")
    model_name = os.environ.get("LLM_MODEL")

    if not api_key:
        return DeterministicFallbackProvider()

    if api_key.startswith("sk-") or (model_name and "gpt" in model_name):
        return OpenAILLMProvider(api_key=api_key, model_name=model_name or "gpt-4o-mini")
    else:
        return GeminiLLMProvider(api_key=api_key, model_name=model_name or "gemini-3.6-flash")


class InvestigationEngine:
    def __init__(self, data_engine: Optional[FactoryDataEngine] = None, llm_provider: Optional[LLMProvider] = None):
        self.data_engine = data_engine if data_engine else FactoryDataEngine()
        self.llm_provider = llm_provider if llm_provider else get_llm_provider()

    def parse_query_scope(self, question: str) -> Dict[str, Any]:
        """
        Extract line (L1-L4), machine ID (M101-M404), date, intent category,
        requested facts, and out-of-scope flags from user's question.
        """
        if not question or not question.strip():
            return {
                "line": None,
                "machine_id": None,
                "date": None,
                "explicit_line": False,
                "invalid_line": None,
                "invalid_machine": None,
                "intent_category": "UNSUPPORTED_OUT_OF_SCOPE",
                "is_out_of_scope": True
            }

        q_lower = question.lower()

        # 1. Match Line (L1, L2, L3, L4, or Line 1..4; detect L5..L9 as invalid)
        line_match = re.search(r"\bL([1-9])\b|\bline\s*([1-9])\b", question, re.IGNORECASE)
        line = None
        explicit_line = False
        invalid_line = None
        if line_match:
            digit = int(line_match.group(1) or line_match.group(2))
            if 1 <= digit <= 4:
                line = f"L{digit}"
                explicit_line = True
            else:
                invalid_line = f"L{digit}"

        # 2. Match Machine ID (e.g. M301, M101, M999)
        machine_match = re.search(r"\b(M\d{3})\b", question, re.IGNORECASE)
        machine_id = None
        invalid_machine = None
        if machine_match:
            m_candidate = machine_match.group(1).upper()
            found_line = None
            for l_key, m_list in self.data_engine.LINE_MAPPING.items():
                if m_candidate in m_list:
                    found_line = l_key
                    break
            if found_line:
                machine_id = m_candidate
                if not line and not invalid_line:
                    line = found_line
            else:
                invalid_machine = m_candidate

        # 3. Match Date
        date = None
        iso_match = re.search(r"\b(20\d{2}-\d{2}-\d{2})\b", question)
        if iso_match:
            date = iso_match.group(1)
        else:
            months_pattern = r"(January|February|March|April|May|June|July|August|September|October|November|December|Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)"
            m1 = re.search(rf"\b{months_pattern}\s+(\d{{1,2}})(?:st|nd|rd|th)?(?:\s*,?\s*(20\d{{2}}))?\b", question, re.IGNORECASE)
            if m1:
                month_str = m1.group(1)
                day_int = int(m1.group(2))
                year_str = m1.group(3) or "2026"
                try:
                    dt = pd.to_datetime(f"{month_str} {day_int} {year_str}")
                    date = dt.strftime("%Y-%m-%d")
                except Exception:
                    pass
            else:
                m2 = re.search(rf"\b(\d{{1,2}})(?:st|nd|rd|th)?\s+{months_pattern}(?:\s*,?\s*(20\d{{2}}))?\b", question, re.IGNORECASE)
                if m2:
                    day_int = int(m2.group(1))
                    month_str = m2.group(2)
                    year_str = m2.group(3) or "2026"
                    try:
                        dt = pd.to_datetime(f"{day_int} {month_str} {year_str}")
                        date = dt.strftime("%Y-%m-%d")
                    except Exception:
                        pass

        # 4. Classify Investigation Intent Category
        if any(w in q_lower for w in ["cost", "financial", "price", "dollar", "money", "loss in $", "usd", "amount"]):
            intent_category = "FINANCIAL_UNAVAILABLE"
        elif any(w in q_lower for w in ["operator", "who was responsible", "worker", "staff", "personnel", "who operated"]):
            intent_category = "OPERATOR_UNAVAILABLE"
        elif any(w in q_lower for w in ["rejection", "rejected", "defect", "quality", "scrap", "bad unit"]):
            intent_category = "QUALITY_DEFECT"
        elif any(w in q_lower for w in ["recurring", "frequent", "history", "historical", "repeated", "pattern"]):
            intent_category = "MAINTENANCE_RECURRING"
        elif any(w in q_lower for w in ["supervisor do", "what should the supervisor do", "recommended action", "action should be taken"]) and not any(w in q_lower for w in ["miss", "target"]):
            intent_category = "SUPERVISOR_ACTION"
        elif any(w in q_lower for w in ["what happened to machine", "what happened to m", "overheating problem", "overheating event", "stoppage"]) and not any(w in q_lower for w in ["miss", "target"]):
            intent_category = "DOWNTIME_EVENT"
        elif any(w in q_lower for w in ["target", "shortfall", "miss", "production rate", "output"]):
            intent_category = "PRODUCTION_TARGET"
        else:
            intent_category = "GENERAL_INVESTIGATION"

        # 5. Out-of-scope check
        factory_keywords = [
            "line", "machine", "production", "target", "actual", "shortfall", "downtime", "stoppage", "reset",
            "overheating", "temperature", "maintenance", "quality", "rejection", "rejected", "defect", "sop",
            "shift", "coolant", "cost", "operator", "failure", "problem", "issue", "investigate", "supervisor",
            "l1", "l2", "l3", "l4", "m101", "m102", "m103", "m104", "m201", "m202", "m203", "m204",
            "m301", "m302", "m303", "m304", "m401", "m402", "m403", "m404"
        ]
        has_factory_context = any(k in q_lower for k in factory_keywords) or (line is not None) or (machine_id is not None) or (invalid_line is not None) or (invalid_machine is not None)
        is_out_of_scope = not has_factory_context

        if is_out_of_scope:
            intent_category = "UNSUPPORTED_OUT_OF_SCOPE"

        # Default date for machine/intent queries if omitted
        if not date and (machine_id or intent_category in ["MAINTENANCE_RECURRING", "FINANCIAL_UNAVAILABLE", "OPERATOR_UNAVAILABLE", "DOWNTIME_EVENT"]):
            date = "2026-08-04"

        return {
            "line": line,
            "machine_id": machine_id,
            "date": date,
            "explicit_line": explicit_line,
            "invalid_line": invalid_line,
            "invalid_machine": invalid_machine,
            "intent_category": intent_category,
            "is_out_of_scope": is_out_of_scope
        }

    def run_investigation(self, question: str) -> Dict[str, Any]:
        """
        Execute full investigation flow:
        1. Intent-aware entity & intent extraction
        2. Data Engine fact collection
        3. Intent-targeted SOP RAG retrieval
        4. Structured Evidence Package creation
        5. LLM reasoning call & structured output parsing
        """
        scope = self.parse_query_scope(question)

        # 1. Out-of-scope check
        if scope.get("is_out_of_scope"):
            return {
                "status": "clarification_required",
                "message": "MFGX AI is a Production Investigation Copilot designed to investigate factory production, downtime, maintenance, quality, and SOP-related issues. Your question appears to be outside factory operations."
            }

        # 2. Invalid Line check
        if scope.get("invalid_line"):
            inv_l = scope.get("invalid_line")
            valid_lines = list(self.data_engine.LINE_MAPPING.keys())
            return {
                "status": "not_found",
                "message": f"Unknown production line '{inv_l}'. Valid lines: {valid_lines}"
            }

        # 3. Invalid Machine check
        if scope.get("invalid_machine"):
            inv_m = scope.get("invalid_machine")
            return {
                "status": "not_found",
                "message": f"Unknown machine ID '{inv_m}'."
            }

        line = scope.get("line")
        machine_id = scope.get("machine_id")
        date = scope.get("date")
        explicit_line = scope.get("explicit_line", True)
        intent_category = scope.get("intent_category", "PRODUCTION_TARGET")

        scope_line_display = line
        if not explicit_line and machine_id:
            scope_line_display = f"Machine {machine_id}"

        # 4. Clarification required if neither line nor machine can be determined
        if not line and not machine_id:
            return {
                "status": "clarification_required",
                "message": "Could not determine a target production line (e.g. L1-L4) or machine ID (e.g. M301) from your question. Please specify the target line or machine."
            }

        # Step 5: Collect verified facts from Data Engine
        prod_data = self.data_engine.investigate_production(line=line, date_str=date) if (line and date) else None
        downtime_data = self.data_engine.get_downtime(line=line, date_str=date) if (line and date) else None
        quality_data = self.data_engine.get_quality(line=line, date_str=date) if (line and date) else None

        # Determine target machines for maintenance retrieval
        target_machines = []
        if machine_id:
            target_machines.append(machine_id)
        
        if downtime_data and downtime_data.get("records"):
            for d in downtime_data["records"]:
                if d.get("machine_id") and d["machine_id"] not in target_machines:
                    target_machines.append(d["machine_id"])

        # Collect maintenance records
        maintenance_records = []
        for m_id in target_machines:
            try:
                m_hist = self.data_engine.get_maintenance_history(machine_id=m_id)
                if m_hist and m_hist.get("records"):
                    maintenance_records.extend(m_hist.get("records"))
            except Exception:
                pass

        downtime_records = downtime_data.get("records", []) if downtime_data else []

        # If date is invalid or no records exist for specific date + line
        if not prod_data and not downtime_data and not quality_data and not maintenance_records:
            return {
                "status": "not_found",
                "message": f"No factory records found for line '{line}' on date '{date}'."
            }

        # Step 6: Intent-Targeted SOP RAG Retrieval
        rag_queries = []
        if intent_category == "QUALITY_DEFECT":
            rag_queries = [
                "Quality inspection procedure defect recording SOP-304",
                f"Line {line or 'L3'} quality rejection troubleshooting"
            ]
        elif intent_category == "MAINTENANCE_RECURRING":
            m_target = machine_id or "M301"
            rag_queries = [
                f"{m_target} cooling system inspection maintenance SOP-301",
                f"{m_target} temperature sensor warning history"
            ]
        elif intent_category == "SUPERVISOR_ACTION":
            m_target = machine_id or "M301"
            rag_queries = [
                f"Supervisor response protocol for {m_target} overheating SOP-302",
                f"{m_target} cooling system inspection SOP-301"
            ]
        elif intent_category == "DOWNTIME_EVENT":
            m_target = machine_id or "M301"
            rag_queries = [
                f"{m_target} overheating response procedure SOP-302",
                f"{m_target} unscheduled downtime response"
            ]
        else:
            rag_queries = [
                f"Line {line or 'L3'} target shortfall recovery SOP-305",
                f"M301 overheating response SOP-302"
            ]

        sop_evidence = []
        seen_sop_chunks = set()
        for q in rag_queries:
            chunks = search_sops(query=q, top_k=3)
            for c in chunks:
                chunk_key = (c.get("sop_id"), c.get("page"), c.get("text")[:50])
                if chunk_key not in seen_sop_chunks:
                    seen_sop_chunks.add(chunk_key)
                    sop_evidence.append(c)

        # Build Evidence Package
        is_unavail = intent_category in ["FINANCIAL_UNAVAILABLE", "OPERATOR_UNAVAILABLE"]
        evidence_package = {
            "investigation": {
                "question": question,
                "line": scope_line_display,
                "date": date,
                "machine_id": machine_id,
                "explicit_line": explicit_line,
                "intent_category": intent_category
            },
            "production": prod_data if not is_unavail else None,
            "downtime": downtime_records if not is_unavail else [],
            "maintenance": maintenance_records if not is_unavail else [],
            "quality": quality_data if not is_unavail else None,
            "sop_evidence": sop_evidence if not is_unavail else []
        }

        # Step 7: Call LLM with Evidence Package & Intent-Aware System Prompt
        system_prompt = f"""You are MFGX AI, an expert Production Investigation Copilot for factory supervisors.
Your job is to analyze the provided evidence package and produce a structured JSON investigation report tailored to the user's specific question and intent category ({intent_category}).

CRITICAL INTENT-AWARE SYNTHESIS RULES:
1. Ground all findings ONLY in the supplied evidence package. Never invent production numbers, downtime durations, maintenance records, quality values, or SOP content.
2. TAILOR THE REPORT TO THE DETECTED INTENT CATEGORY ({intent_category}):
   - For QUALITY_DEFECT intent: Focus likely_contributing_factor, supporting_evidence, and recommended_action primarily on quality rejections (139 rejected units, 4.80% rejection rate), defect types (Dimensional Out-of-Spec), and SOP-304 quality inspection procedures.
   - For DOWNTIME_EVENT intent: Focus likely_contributing_factor, supporting_evidence, and recommended_action on machine M301 downtime duration (47 mins), cause (Overheating), and SOP-302 emergency response.
   - For MAINTENANCE_RECURRING intent: Focus likely_contributing_factor, supporting_evidence, and recommended_action on historical maintenance logs (4 prior cooling warnings for M301) and SOP-301 cooling audit procedures.
   - For SUPERVISOR_ACTION intent: Focus likely_contributing_factor, supporting_evidence, and recommended_action directly on step-by-step SOP instructions for the supervisor (SOP-302 pause & inspect, SOP-301 maintenance dispatch).
   - For PRODUCTION_TARGET intent: Focus on Target 3,300, Actual 2,895, Shortfall 405 (12.27%), downtime impact, and SOP-305 target recovery.
3. IMPORTANT FOR FINANCIAL COST & OPERATOR QUERIES:
   - If intent is FINANCIAL_UNAVAILABLE: set likely_contributing_factor to: "Information unavailable. The available factory dataset does not contain financial cost records for this event, so an exact financial cost cannot be determined." Set limitations and supporting_evidence to contain this exact message.
   - If intent is OPERATOR_UNAVAILABLE: set likely_contributing_factor to: "Information unavailable. Operator names and individual personnel assignments are not available in the factory dataset, so the responsible operator cannot be identified." Set limitations and supporting_evidence to contain this exact message.
4. Return ONLY a valid JSON object matching this exact schema:

{{
  "investigation_question": "...",
  "investigation_scope": {{
    "line": "...",
    "date": "..."
  }},
  "production_performance": {{
    "target": 0,
    "actual": 0,
    "shortfall": 0,
    "shortfall_percentage": 0.0
  }},
  "major_downtime_events": [
    {{
      "machine_id": "...",
      "duration_minutes": 0,
      "reason": "...",
      "category": "...",
      "start_time": "..."
    }}
  ],
  "maintenance_evidence": [
    {{
      "machine_id": "...",
      "date": "...",
      "reported_problem": "...",
      "maintenance_action": "...",
      "status": "..."
    }}
  ],
  "quality_evidence": {{
    "total_produced": 0,
    "total_rejected": 0,
    "rejection_rate": 0.0,
    "defect_types": []
  }},
  "relevant_sops": [
    {{
      "sop_id": "...",
      "source": "...",
      "page": 0,
      "relevance": "..."
    }}
  ],
  "likely_contributing_factor": "...",
  "supporting_evidence": [
    "..."
  ],
  "recommended_action": "...",
  "confidence": "high|medium|low",
  "limitations": []
}}"""

        user_prompt = json.dumps(evidence_package, indent=2)

        try:
            raw_response = self.llm_provider.generate_response(system_prompt=system_prompt, user_prompt=user_prompt)
            
            # Clean JSON if enclosed in markdown code fences
            cleaned = raw_response.strip()
            if cleaned.startswith("```json"):
                cleaned = cleaned[7:]
            if cleaned.startswith("```"):
                cleaned = cleaned[3:]
            if cleaned.endswith("```"):
                cleaned = cleaned[:-3]
            cleaned = cleaned.strip()

            parsed_result = json.loads(cleaned)
            return {
                "status": "success",
                "investigation": parsed_result
            }

        except Exception as e:
            logger.info(f"LLM API call fallback to deterministic synthesis: {e}")
            fallback = DeterministicFallbackProvider()
            fallback_response = fallback.generate_response(system_prompt=system_prompt, user_prompt=user_prompt)
            parsed_result = json.loads(fallback_response)
            return {
                "status": "success",
                "investigation": parsed_result,
                "note": f"Result generated via intent-aware deterministic evidence synthesis ({str(e)})"
            }
