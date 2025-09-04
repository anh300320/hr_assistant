import io
import os
import re

import pandas as pd
import pdfkit
import pypandoc
from docx2pdf import convert
from mailmerge import MailMerge

from src.payslip.email_service import send_email


class PayslipWorker:
    def __init__(self):
        self._payslip_template_fp = "resources/PayslipTemplate.docx"
        self.target_start = 0
        self.target_end = 1000000
        self.target_list = []
        self.email_column = "Email"

    def run(self, payslip_sheet: bytes):
        yield from self._merge_data(payslip_sheet)

    def _merge_data(
        self,
        payslip_sheet: bytes,
    ) -> list[str]:
        # Load the Excel data
        excel_data = pd.read_excel(
            io.BytesIO(payslip_sheet),
            sheet_name=None,
            skiprows=None,
            dtype=str,
            engine="openpyxl",
        )

        target_sheet = None
        for sheet_name, sheet_data in excel_data.items():
            if target_sheet is None or len(sheet_data) > len(target_sheet):
                target_sheet = sheet_data

        pdf_files = []

        # Iterate through each row in the Excel data and perform the merge
        for index, row in target_sheet.iterrows():
            if not self.target_start <= int(index) + 1 <= self.target_end:
                continue
            if self.target_list and int(index) + 1 not in self.target_list:
                continue
            with MailMerge(self._payslip_template_fp) as document:
                # Prepare the merge fields dictionary from the current row
                columns = {col: str(row[col]) for col in target_sheet.columns if
                                isinstance(col, str)}

                fields = document.get_merge_fields()

                normalized_fields = {}
                for field in fields:
                    normalized = re.sub(r'[^A-Za-z0-9]', '', field)
                    normalized_fields[normalized] = field

                merged_fields = {}
                for col, value in columns.items():
                    if not isinstance(col, str):
                        continue
                    normalized_col = re.sub(r'[^A-Za-z0-9]', '', col)
                    according_field = normalized_fields.get(normalized_col)
                    if not according_field:
                        continue
                    merged_fields[according_field] = value if value != "nan" else ""

                # Execute the merge
                document.merge(**merged_fields)

                file_data = io.BytesIO()

                # Save the merged document (e.g., with a unique name)
                name = merged_fields.get('Full_name', 'Payslip')
                docx_fp = f"temp/{name}.docx"
                pdf_fp = docx_fp.replace("docx", "pdf")

                document.write(file_data)
                with open(docx_fp, "wb") as fd:
                    fd.write(file_data.getvalue())

                convert(docx_fp, pdf_fp)

                email = columns.get(self.email_column)
                if not email:
                    email = "tranmingthu001@gmail.com"

                send_email(email, pdf_fp)

                os.remove(pdf_fp)
                os.remove(docx_fp)

                if name != "Payslip":
                    yield name, email
