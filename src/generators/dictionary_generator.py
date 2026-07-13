import json
from pathlib import Path
from typing import Any

import pandas as pd
from pandas.errors import EmptyDataError

from config.settings import (
    DICTIONARY_DIR,
    INVENTORY_DIR,
    SCHEMA_DIR,
    STATISTICS_DIR,
    PRIMARY_KEY_DIR,
    DATATYPE_DIR,
)


class DictionaryGenerator:

    def __init__(self) -> None:

        DICTIONARY_DIR.mkdir(parents=True, exist_ok=True)

    @staticmethod
    def _load_inventory() -> pd.DataFrame:

        inventory_path = INVENTORY_DIR / "inventory.csv"
        if inventory_path.exists():
            return pd.read_csv(inventory_path)
        return pd.DataFrame(columns=["dataset_name"])

    @staticmethod
    def _load_schema_metadata() -> pd.DataFrame:

        schema_frames: list[pd.DataFrame] = []

        for schema_file in sorted(SCHEMA_DIR.glob("*_schema.csv")):
            frame = pd.read_csv(schema_file)
            schema_frames.append(frame)

        if not schema_frames:
            return pd.DataFrame(columns=["dataset_name", "column_name"])

        return pd.concat(schema_frames, ignore_index=True)

    @staticmethod
    def _read_valid_statistics_file(statistics_file: Path) -> pd.DataFrame | None:

        if statistics_file.stat().st_size == 0:
            return None

        try:
            frame = pd.read_csv(statistics_file)
        except EmptyDataError:
            return None

        if frame.empty:
            return None

        return frame

    @staticmethod
    def _load_statistics() -> pd.DataFrame:

        statistics_frames: list[pd.DataFrame] = []

        for statistics_file in sorted(STATISTICS_DIR.glob("*_numeric.csv")):
            frame = DictionaryGenerator._read_valid_statistics_file(statistics_file)
            if frame is None:
                continue
            frame["dataset_name"] = statistics_file.stem.replace("_numeric", "")
            statistics_frames.append(frame)

        for statistics_file in sorted(STATISTICS_DIR.glob("*_categorical.csv")):
            frame = DictionaryGenerator._read_valid_statistics_file(statistics_file)
            if frame is None:
                continue
            frame["dataset_name"] = statistics_file.stem.replace("_categorical", "")
            statistics_frames.append(frame)

        if not statistics_frames:
            return pd.DataFrame(columns=["dataset_name", "column_name"])

        return pd.concat(statistics_frames, ignore_index=True)

    @staticmethod
    def _load_primary_keys() -> pd.DataFrame:

        primary_keys_path = PRIMARY_KEY_DIR / "primary_key_candidates.csv"
        if primary_keys_path.exists():
            return pd.read_csv(primary_keys_path)
        return pd.DataFrame(columns=["dataset_name", "column_name"])

    @staticmethod
    def _load_semantic_datatypes() -> pd.DataFrame:

        datatype_path = DATATYPE_DIR / "semantic_datatypes.csv"
        if datatype_path.exists():
            return pd.read_csv(datatype_path)
        return pd.DataFrame(columns=["dataset_name", "column_name", "business_datatype"])

    @staticmethod
    def _coerce_sample_values(values: Any) -> str:

        if pd.isna(values):
            return ""

        if isinstance(values, list):
            return ", ".join(str(value) for value in values[:5])

        if isinstance(values, str):
            return values

        return str(values)

    def generate(self) -> pd.DataFrame:

        inventory_df = self._load_inventory()
        schema_df = self._load_schema_metadata()
        statistics_df = self._load_statistics()
        primary_key_df = self._load_primary_keys()
        datatype_df = self._load_semantic_datatypes()

        dictionary_rows: list[dict[str, Any]] = []

        schema_df = schema_df.copy()
        schema_df["dataset_name"] = schema_df["dataset_name"].astype(str)
        schema_df["column_name"] = schema_df["column_name"].astype(str)

        inventory_lookup = inventory_df[["dataset_name", "source_file", "rows", "columns"]].copy()
        inventory_lookup["dataset_name"] = inventory_lookup["dataset_name"].astype(str)

        statistics_lookup = statistics_df[["dataset_name", "column_name", "count", "min", "max", "mean", "median", "mode"]].copy()
        statistics_lookup["dataset_name"] = statistics_lookup["dataset_name"].astype(str)
        statistics_lookup["column_name"] = statistics_lookup["column_name"].astype(str)

        pk_lookup = primary_key_df[["dataset_name", "column_name", "confidence"]].copy()
        pk_lookup["dataset_name"] = pk_lookup["dataset_name"].astype(str)
        pk_lookup["column_name"] = pk_lookup["column_name"].astype(str)

        datatype_lookup = datatype_df[["dataset_name", "column_name", "business_datatype"]].copy()
        datatype_lookup["dataset_name"] = datatype_lookup["dataset_name"].astype(str)
        datatype_lookup["column_name"] = datatype_lookup["column_name"].astype(str)

        merged_df = schema_df.merge(
            inventory_lookup,
            on="dataset_name",
            how="left",
        )
        merged_df = merged_df.merge(
            statistics_lookup,
            on=["dataset_name", "column_name"],
            how="left",
        )
        merged_df = merged_df.merge(
            pk_lookup,
            on=["dataset_name", "column_name"],
            how="left",
        )
        merged_df = merged_df.merge(
            datatype_lookup,
            on=["dataset_name", "column_name"],
            how="left",
        )

        for _, row in merged_df.iterrows():
            dictionary_rows.append({
                "Dataset": str(row["dataset_name"]),
                "Column": str(row["column_name"]),
                "Pandas Datatype": str(row["pandas_dtype"]),
                "Business Datatype": str(row.get("business_datatype", "Text") or "Text"),
                "Nullable": "Yes" if bool(row.get("nullable", False)) else "No",
                "Missing %": round(float(row.get("missing_percentage", 0.0)), 2),
                "Unique %": round(float(row.get("unique_percentage", 0.0)), 2),
                "Primary Key Candidate": "Yes" if str(row.get("confidence", "")).lower() in {"very high", "high", "medium"} else "No",
                "Sample Values": self._coerce_sample_values(row.get("sample_values", "")),
                "Description": "",
                "Source File": str(row.get("source_file", "")),
                "Rows": int(row.get("rows", 0)) if pd.notna(row.get("rows")) else 0,
                "Columns": int(row.get("columns", 0)) if pd.notna(row.get("columns")) else 0,
                "Mean": row.get("mean"),
                "Median": row.get("median"),
                "Mode": row.get("mode"),
            })

        dictionary_df = pd.DataFrame(dictionary_rows)
        if "Business Datatype" in dictionary_df.columns:
            dictionary_df["Business Datatype"] = dictionary_df["Business Datatype"].fillna("Text")
        dictionary_df.to_csv(DICTIONARY_DIR / "data_dictionary.csv", index=False)
        dictionary_df.to_excel(DICTIONARY_DIR / "data_dictionary.xlsx", index=False, engine="openpyxl")

        markdown_summary = self._build_markdown_summary(dictionary_df)
        with open(DICTIONARY_DIR / "data_dictionary.md", "w", encoding="utf-8") as file_handle:
            file_handle.write(markdown_summary)

        print("Generated data dictionary.")

        return dictionary_df

    @staticmethod
    def _build_markdown_summary(dictionary_df: pd.DataFrame) -> str:

        lines = ["# Data Dictionary", ""]

        for dataset_name, dataset_frame in dictionary_df.groupby("Dataset"):
            lines.append(f"## {dataset_name}")
            for _, row in dataset_frame.iterrows():
                lines.append(
                    f"- {row['Column']}: {row['Business Datatype']} ({row['Pandas Datatype']})"
                )
            lines.append("")

        return "\n".join(lines).strip() + "\n"
