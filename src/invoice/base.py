from abc import ABC, abstractmethod
from dataclasses import dataclass
from decimal import Decimal
from enum import Enum
from pathlib import Path

import pandas as pd
from borb.pdf.canvas.layout.image.image import Image
from borb.pdf.canvas.layout.layout_element import Alignment
from borb.pdf.canvas.layout.page_layout.multi_column_layout import \
    SingleColumnLayout
from borb.pdf.canvas.layout.table.fixed_column_width_table import \
    FixedColumnWidthTable as Table
from borb.pdf.canvas.layout.table.table import TableCell
from borb.pdf.canvas.layout.text.paragraph import Paragraph
from borb.pdf.document import Document
from borb.pdf.page.page import Page
from borb.pdf.pdf import PDF
from config.paths import INVOICE_PATH
from src.entities import Customer

# TODO: this probably has to be a separate status table with active accounts/banks payment text
BANK = "Lehmann Brothers"
PAYMENT_ACCOUNT = "LT79 1234 5678 7777 0000"
PAYMENT_TEXT = "Please include invoice number in payment details"


@dataclass
class Font:
    default: str = "Helvetica"
    oblique: str = "Helvetica-oblique"
    bold: str = "Helvetica-bold"
    bold_oblique: str = "Helvetica-bold-oblique"


class InvoiceType(Enum):
    VAT: str = "VAT INVOICE"


class CustomerAttributes(Enum):
    CUSTOMER_NAME: str = "customer_name"
    CUSTOMER_CODE: str = "customer_code"
    VAT_CODE: str = "vat_code"
    ADDRESS: str = "address"
    TELEPHONE: str = "telephone"


@dataclass
class InvoiceInfo:
    invoice_type: InvoiceType
    invoice_number: str
    invoice_date: str
    buyer: Customer
    seller: Customer
    order_df: pd.DataFrame


class InvoiceTemplate(ABC):
    def __init__(self, invoice_info: InvoiceInfo):
        self.invoice_info = invoice_info
        self.pdf: Document = Document()

    @abstractmethod
    def generate(self) -> None:
        ...

    def initialize_document(self) -> SingleColumnLayout:
        page = Page()
        self.pdf.append_page(page)
        return SingleColumnLayout(page, vertical_margin=Decimal(30), horizontal_margin=Decimal(30))

    @staticmethod
    def get_logo_image(path: Path) -> Image:
        return Image(image=path, width=100, height=19)

    def get_title(self) -> Table:
        t = Table(number_of_rows=3, number_of_columns=1, padding_bottom=Decimal(10))
        title = Paragraph(
            self.invoice_info.invoice_type.value,
            font=Font.bold,
            font_size=Decimal(14),
            horizontal_alignment=Alignment.CENTERED,
        )
        invoice_number = Paragraph(
            self.invoice_info.invoice_number,
            font=Font.default,
            font_size=Decimal(11),
            horizontal_alignment=Alignment.CENTERED,
        )
        invoice_date = Paragraph(
            self.invoice_info.invoice_date,
            font=Font.default,
            font_size=Decimal(11),
            horizontal_alignment=Alignment.CENTERED,
        )
        t.add(title).add(invoice_number).add(invoice_date)
        t.no_borders()
        return t

    def get_buyer_seller_info(self) -> Table:
        t = Table(number_of_rows=len(CustomerAttributes) + 1, number_of_columns=2)

        info_items = ["Seller:", "Buyer:"]
        for attribute in CustomerAttributes:
            info_items.append(self.invoice_info.seller.__dict__[attribute.value])
            info_items.append(self.invoice_info.buyer.__dict__[attribute.value])

        for i, item in enumerate(info_items):
            font = Font.bold if i in [2, 3] else Font.default
            t.add(Paragraph(item, font=font, font_size=Decimal(10)))

        t.no_borders()
        return t

    def add_payment_info(self) -> Table:
        t = Table(number_of_rows=6, number_of_columns=1, padding_top=Decimal(20))
        manager = self.invoice_info.order_df.iloc[0].manager_name
        payment_due_date = self.invoice_info.order_df.iloc[0].payment_due
        info = [
            f"Invoice issued by: {manager}",
            f"Payment terms: 30 days, {payment_due_date}",
            f"Tel.: {self.invoice_info.seller.telephone}",
            f"Bank: {BANK}",
            f"Account: {PAYMENT_ACCOUNT}",
            PAYMENT_TEXT,
        ]
        for text in info:
            t.add(TableCell(Paragraph(text, font=Font.default, font_size=Decimal(8))))
        t.no_borders()
        return t

    def save_pdf(self) -> None:
        with open(INVOICE_PATH, "wb") as pdf_file_handle:
            PDF.dumps(pdf_file_handle, self.pdf)
