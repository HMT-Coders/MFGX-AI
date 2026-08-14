from pathlib import Path
from typing import Dict, List, Any, Optional
import pandas as pd


class FactoryDataEngine:
    LINE_MAPPING = {
        "L1": ["M101", "M102", "M103", "M104"],
        "L2": ["M201", "M202", "M203", "M204"],
        "L3": ["M301", "M302", "M303", "M304"],
        "L4": ["M401", "M402", "M403", "M404"],
    }

    _instance: Optional['FactoryDataEngine'] = None

    def __new__(cls, data_dir: Optional[Path] = None):
        if cls._instance is None:
            cls._instance = super(FactoryDataEngine, cls).__new__(cls)
            cls._instance._initialized = False
        return cls._instance

    def __init__(self, data_dir: Optional[Path] = None):
        if getattr(self, "_initialized", False):
            return

        if data_dir is None:
            base_dir = Path(__file__).resolve().parent
            self.data_dir = base_dir.parent / "data"
        else:
            self.data_dir = Path(data_dir)

        self._load_data()
        self._initialized = True

    def _load_data(self):
        prod_path = self.data_dir / "production.csv"
        down_path = self.data_dir / "downtime.csv"
        qual_path = self.data_dir / "quality.csv"
        maint_path = self.data_dir / "maintenance.csv"

        for p in [prod_path, down_path, qual_path, maint_path]:
            if not p.exists():
                raise FileNotFoundError(f"Required data file missing: {p.name}")

        self.production_df = pd.read_csv(prod_path)
        self.downtime_df = pd.read_csv(down_path)
        self.quality_df = pd.read_csv(qual_path)
        self.maintenance_df = pd.read_csv(maint_path)

        # Convert all Date columns to pandas datetime
        self.production_df["Date"] = pd.to_datetime(self.production_df["Date"])
        self.downtime_df["Date"] = pd.to_datetime(self.downtime_df["Date"])
        self.quality_df["Date"] = pd.to_datetime(self.quality_df["Date"])
        self.maintenance_df["Date"] = pd.to_datetime(self.maintenance_df["Date"])

    def investigate_production(self, line: str, date_str: str) -> Optional[Dict[str, Any]]:
        """
        Filter production data by line and date.
        Returns line, date, target, actual, shortfall, shortfall_percentage, and shifts list.
        """
        try:
            target_date = pd.to_datetime(date_str)
        except Exception:
            raise ValueError(f"Invalid date format: {date_str}. Expected YYYY-MM-DD.")

        df = self.production_df[
            (self.production_df["Line"] == line) & 
            (self.production_df["Date"] == target_date)
        ]

        if df.empty:
            return None

        target = int(df["Target"].sum())
        actual = int(df["Actual"].sum())
        shortfall = target - actual
        shortfall_percentage = round((shortfall / target) * 100, 2) if target > 0 else 0.0

        shifts = []
        for _, row in df.iterrows():
            shifts.append({
                "shift": str(row["Shift"]),
                "product": str(row["Product"]),
                "target": int(row["Target"]),
                "actual": int(row["Actual"]),
                "shortfall": int(row["Target"] - row["Actual"])
            })

        formatted_date = target_date.strftime("%Y-%m-%d")
        return {
            "line": line,
            "date": formatted_date,
            "target": target,
            "actual": actual,
            "shortfall": shortfall,
            "shortfall_percentage": shortfall_percentage,
            "shifts": shifts
        }

    def get_downtime(self, line: str, date_str: str) -> Optional[Dict[str, Any]]:
        """
        Return downtime records for the selected line and date using line-to-machine mapping.
        """
        if line not in self.LINE_MAPPING:
            raise ValueError(f"Unknown production line: {line}")

        try:
            target_date = pd.to_datetime(date_str)
        except Exception:
            raise ValueError(f"Invalid date format: {date_str}. Expected YYYY-MM-DD.")

        machines = self.LINE_MAPPING[line]
        df = self.downtime_df[
            (self.downtime_df["Machine ID"].isin(machines)) & 
            (self.downtime_df["Date"] == target_date)
        ]

        if df.empty:
            return {
                "line": line,
                "date": target_date.strftime("%Y-%m-%d"),
                "total_downtime_minutes": 0,
                "records": []
            }

        total_downtime = int(df["Duration"].sum())
        records = []
        for _, row in df.iterrows():
            records.append({
                "machine_id": str(row["Machine ID"]),
                "start_time": str(row.get("Start Time", "")),
                "duration": int(row["Duration"]),
                "reason": str(row["Reason"]),
                "category": str(row.get("Category", "Unscheduled"))
            })

        return {
            "line": line,
            "date": target_date.strftime("%Y-%m-%d"),
            "total_downtime_minutes": total_downtime,
            "records": records
        }

    def get_quality(self, line: str, date_str: str) -> Optional[Dict[str, Any]]:
        """
        Return quality inspection records, defect counts, total produced, total rejected,
        and calculated rejection rate.
        """
        try:
            target_date = pd.to_datetime(date_str)
        except Exception:
            raise ValueError(f"Invalid date format: {date_str}. Expected YYYY-MM-DD.")

        df = self.quality_df[
            (self.quality_df["Line"] == line) & 
            (self.quality_df["Date"] == target_date)
        ]

        if df.empty:
            return None

        total_produced = int(df["Total Produced"].sum())
        total_rejected = int(df["Rejected Quantity"].sum())
        rejection_rate = round((total_rejected / total_produced) * 100, 2) if total_produced > 0 else 0.0

        records = []
        for _, row in df.iterrows():
            records.append({
                "shift": str(row.get("Shift", "")),
                "inspected": int(row["Total Produced"]),
                "rejected": int(row["Rejected Quantity"]),
                "defect_type": str(row.get("Defect Type", "General"))
            })

        return {
            "line": line,
            "date": target_date.strftime("%Y-%m-%d"),
            "total_produced": total_produced,
            "total_rejected": total_rejected,
            "rejection_rate": rejection_rate,
            "records": records
        }

    def get_maintenance_history(self, machine_id: str) -> Optional[Dict[str, Any]]:
        """
        Filter maintenance records for a specific machine ID across all dates.
        """
        df = self.maintenance_df[self.maintenance_df["Machine ID"] == machine_id].sort_values("Date", ascending=False)

        if df.empty:
            return None

        records = []
        for _, row in df.iterrows():
            d_val = row["Date"]
            d_str = d_val.strftime("%Y-%m-%d") if hasattr(d_val, "strftime") else str(d_val)
            records.append({
                "machine_id": str(row["Machine ID"]),
                "date": d_str,
                "reported_problem": str(row["Reported Problem"]),
                "maintenance_action": str(row["Maintenance Action"]),
                "status": str(row.get("Status", "Resolved"))
            })

        return {
            "machine_id": machine_id,
            "total_incidents": len(records),
            "records": records
        }
