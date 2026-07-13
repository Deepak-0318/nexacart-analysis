import ast
import json
import re
from typing import Any

import pandas as pd

from config.settings import (
    DATATYPE_DIR,
    PRIMARY_KEY_DIR,
    FOREIGN_KEY_DIR,
    SCHEMA_DIR,
)


class DatatypeDetector:

    def __init__(self) -> None:

        DATATYPE_DIR.mkdir(parents=True, exist_ok=True)

    @staticmethod
    def _parse_sample_values(values: Any) -> list[Any]:

        if isinstance(values, list):
            return values

        if isinstance(values, str):
            try:
                parsed = ast.literal_eval(values)
                if isinstance(parsed, list):
                    return parsed
            except (ValueError, SyntaxError):
                return []

        return []

    @staticmethod
    def _normalize_column_name(column_name: str) -> str:

        return str(column_name).strip().lower()

    @staticmethod
    def _contains_any(text: str, tokens: tuple[str, ...]) -> bool:

        return any(token in text for token in tokens)

    @staticmethod
    def _is_boolean_column(column_name: str, pandas_dtype: str, sample_values: list[str]) -> bool:

        lowered_name = DatatypeDetector._normalize_column_name(column_name)
        if lowered_name.startswith(("is_", "has_")):
            return True
        if "flag" in lowered_name:
            return True
        return pandas_dtype.lower().startswith("bool") or any(
            value.strip().lower() in {"true", "false", "yes", "no", "y", "n", "1", "0"}
            for value in sample_values
        )

    @staticmethod
    def _is_integer_column(pandas_dtype: str) -> bool:

        return pandas_dtype.lower() in {
            "int64",
            "int32",
            "int16",
            "int8",
            "uint64",
            "uint32",
            "uint16",
            "uint8",
        }

    @staticmethod
    def _is_decimal_column(pandas_dtype: str) -> bool:

        return pandas_dtype.lower() in {"float64", "float32", "float16"}

    def detect(self) -> pd.DataFrame:

        pk_df = pd.read_csv(PRIMARY_KEY_DIR / "primary_key_candidates.csv") if (PRIMARY_KEY_DIR / "primary_key_candidates.csv").exists() else pd.DataFrame(columns=["dataset_name", "column_name", "confidence"])
        fk_df = pd.read_csv(FOREIGN_KEY_DIR / "foreign_key_candidates.csv") if (FOREIGN_KEY_DIR / "foreign_key_candidates.csv").exists() else pd.DataFrame(columns=["child_dataset", "child_column"])

        pk_candidates = pk_df[
            pk_df["confidence"].astype(str).isin({"Very High", "High"})
        ] if not pk_df.empty else pd.DataFrame(columns=["dataset_name", "column_name"])
        fk_candidates = fk_df if not fk_df.empty else pd.DataFrame(columns=["child_dataset", "child_column"])

        pk_index = set(
            zip(pk_candidates["dataset_name"].astype(str), pk_candidates["column_name"].astype(str))
        )
        fk_index = set(
            zip(fk_candidates["child_dataset"].astype(str), fk_candidates["child_column"].astype(str))
        )

        rows: list[dict[str, Any]] = []

        for schema_file in sorted(SCHEMA_DIR.glob("*_schema.csv")):

            schema_df = pd.read_csv(schema_file)

            for _, row in schema_df.iterrows():

                dataset_name = str(row["dataset_name"])
                column_name = str(row["column_name"])
                column_label = self._normalize_column_name(column_name)
                pandas_dtype = str(row["pandas_dtype"])
                sample_values = self._parse_sample_values(row.get("sample_values", []))
                string_values = [str(value) for value in sample_values if pd.notna(value)]

                semantic_type = self._infer_semantic_datatype(
                    column_name=column_name,
                    column_label=column_label,
                    pandas_dtype=pandas_dtype,
                    sample_values=string_values,
                    pk_index=pk_index,
                    fk_index=fk_index,
                    dataset_name=dataset_name,
                )

                rows.append({
                    "dataset_name": dataset_name,
                    "column_name": column_name,
                    "pandas_dtype": pandas_dtype,
                    "business_datatype": semantic_type,
                    "sample_values": sample_values,
                })

        datatype_df = pd.DataFrame(rows)

        datatype_df.to_csv(
            DATATYPE_DIR / "semantic_datatypes.csv",
            index=False,
        )

        with open(
            DATATYPE_DIR / "semantic_datatypes.json",
            "w",
            encoding="utf-8",
        ) as file_handle:
            json.dump(datatype_df.to_dict(orient="records"), file_handle, indent=4)

        print("Generated semantic datatypes.")

        return datatype_df

    def _infer_semantic_datatype(
        self,
        *,
        column_name: str,
        column_label: str,
        pandas_dtype: str,
        sample_values: list[str],
        pk_index: set[tuple[str, str]],
        fk_index: set[tuple[str, str]],
        dataset_name: str,
    ) -> str:

        if (dataset_name, column_name) in pk_index:
            return "Primary Key"

        if (dataset_name, column_name) in fk_index:
            return "Foreign Key"

        if column_label.endswith(("_id", "id")):
            return "Identifier"

        if self._contains_any(column_label, ("date", "time", "timestamp", "created", "updated", "purchase", "delivery", "approved")):
            return "Datetime"

        if self._contains_any(column_label, ("price", "payment", "amount", "revenue", "sales", "cost", "profit", "freight")):
            return "Currency"

        if self._contains_any(column_label, ("rating", "review_score", "score", "stars")):
            return "Rating"

        if "city" in column_label:
            return "City"

        if "state" in column_label:
            return "State"

        if "country" in column_label:
            return "Country"

        if "lat" in column_label:
            return "Latitude"

        if "lng" in column_label or "longitude" in column_label:
            return "Longitude"

        if "weight" in column_label:
            return "Weight"

        if self._contains_any(column_label, ("length", "height", "width", "depth")):
            return "Dimension"

        if self._contains_any(column_label, ("zip", "postal", "postcode")):
            return "Postal Code"

        if self._contains_any(column_label, ("type", "category", "status", "method")):
            return "Category"

        if self._is_boolean_column(column_name, pandas_dtype, sample_values):
            return "Boolean"

        if self._is_integer_column(pandas_dtype):
            return "Integer"

        if self._is_decimal_column(pandas_dtype):
            return "Decimal"

        return "Text"
