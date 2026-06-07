"""
Table Extractor — converts tabular data to structured text for RAG
"""
from typing import List, Dict, Any
from app.utils.logger import logger


class TableExtractor:
    async def extract_from_excel(self, file_path: str) -> List[Dict[str, Any]]:
        """Extract tables from Excel files."""
        try:
            import pandas as pd

            xl = pd.ExcelFile(file_path)
            tables = []
            for sheet_name in xl.sheet_names:
                df = xl.parse(sheet_name)
                if df.empty:
                    continue
                tables.append({
                    "sheet": sheet_name,
                    "data": df.to_dict(orient="records"),
                    "markdown": df.to_markdown(index=False),
                    "text": f"Table from sheet '{sheet_name}':\n{df.to_string(index=False)}",
                    "shape": df.shape,
                    "modality": "table",
                })
            return tables
        except Exception as e:
            logger.error(f"[TableExtractor] Excel error: {e}")
            return []

    async def extract_from_csv(self, file_path: str) -> List[Dict[str, Any]]:
        """Extract tables from CSV."""
        try:
            import pandas as pd

            df = pd.read_csv(file_path)
            return [{
                "sheet": "main",
                "data": df.to_dict(orient="records"),
                "markdown": df.to_markdown(index=False),
                "text": df.to_string(index=False),
                "shape": df.shape,
                "modality": "table",
            }]
        except Exception as e:
            logger.error(f"[TableExtractor] CSV error: {e}")
            return []

    def table_to_text(self, table_data: List[List]) -> str:
        """Convert a 2D list table to readable text."""
        if not table_data:
            return ""
        header = table_data[0]
        rows = table_data[1:]
        lines = [" | ".join(str(c) for c in header), "-" * 40]
        for row in rows:
            lines.append(" | ".join(str(c) for c in row))
        return "\n".join(lines)
