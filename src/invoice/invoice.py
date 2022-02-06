from dataclasses import dataclass
from datetime import datetime, timedelta
from decimal import Decimal
from pathlib import Path

from borb.pdf.canvas.layout.image.image import Image
from borb.pdf.canvas.layout.layout_element import Alignment
from borb.pdf.canvas.layout.page_layout.multi_column_layout import SingleColumnLayout
from borb.pdf.canvas.layout.table.fixed_column_width_table import FixedColumnWidthTable as Table
from borb.pdf.canvas.layout.table.flexible_column_width_table import (
    FlexibleColumnWidthTable as FTable,
)
from borb.pdf.canvas.layout.table.table import TableCell
from borb.pdf.canvas.layout.text.paragraph import Paragraph
from borb.pdf.document import Document
from borb.pdf.page.page import Page
from borb.pdf.pdf import PDF
from config.paths import PROJECT_ROOT


@dataclass
class Font:
    default: str = "Courier"
    oblique: str = "Courier-oblique"
    bold: str = "Courier-bold"
    bold_oblique: str = "Courier-bold-oblique"


def initialize_document():
    pdf = Document()
    page = Page()
    pdf.append_page(page)
    page_layout = SingleColumnLayout(
        page, vertical_margin=Decimal(30), horizontal_margin=Decimal(30)
    )
    return pdf, page_layout


def get_logo_image():
    logo_path = Path(PROJECT_ROOT + "/resources/medexy_logo_low_res.jpg")
    return Image(image=logo_path, width=100, height=19)


def get_title():
    t = Table(number_of_rows=3, number_of_columns=1, padding_bottom=Decimal(10))
    title = Paragraph(
        "VAT INVOICE",
        font=Font.bold,
        font_size=Decimal(14),
        horizontal_alignment=Alignment.CENTERED,
    )
    invoice_number = Paragraph(
        "Doc. Nr. MDS0001234",
        font=Font.default,
        font_size=Decimal(11),
        horizontal_alignment=Alignment.CENTERED,
    )
    invoice_date = Paragraph(
        datetime.now().strftime("%Y-%m-%d"),
        font=Font.default,
        font_size=Decimal(11),
        horizontal_alignment=Alignment.CENTERED,
    )
    t.add(title).add(invoice_number).add(invoice_date)
    t.no_borders()
    return t


def get_buyer_seller_info():
    t = Table(number_of_rows=6, number_of_columns=2)
    info_items = [
        "Seller:",
        "Buyer:",
        "UAB Medexy",
        "Some buyer name",
        "Code: 123456789",
        "Code: 987654321",
        "VAT Code: LT000000123456",
        "VAT Code: LT000000654321",
        "Address: Ukmerges 241, Vilnius",
        "Address: Some Address 777, Kaunas",
        "Tel.: +37012345678",
        "Tel.: +37087654321",
    ]
    for item in info_items:
        font = Font.bold if item in ["UAB Medexy", "Some buyer name"] else Font.default
        t.add(Paragraph(item, font=font, font_size=Decimal(10)))

    t.no_borders()
    return t


def build_item_table():
    def add_header(t):
        column_names = [
            "Nr.",
            "Product Code",
            "Product Name",
            "Quantity",
            "Price EUR",
            "Sum EUR",
            "Sum with VAT EUR",
        ]

        for column_name in column_names:
            text = Paragraph(
                column_name,
                font=Font.bold,
                font_size=Decimal(10),
                text_alignment=Alignment.CENTERED,
            )
            t.add(TableCell(text))

        return t

    def add_items(t):
        items = [
            ["123", "Product1", 1, 10.00, 10.00, 12.10],
            ["456", "Product2", 2, 5.00, 10.00, 12.10],
            ["789", "Product3", 10, 100.00, 1000.00, 1210.00],
        ]

        for row_num, item in enumerate(items):
            item = [row_num] + item
            for i in item:
                text = Paragraph(
                    str(i),
                    font=Font.default,
                    font_size=Decimal(8),
                    text_alignment=Alignment.CENTERED,
                )
                t.add(TableCell(text))

        return t

    def add_sums(t):
        cell = lambda text, align=Alignment.CENTERED, col_span=1: TableCell(
            Paragraph(text, font=Font.bold, font_size=Decimal(8), text_alignment=align),
            col_span=col_span,
            border_bottom=False,
            border_top=False,
            border_left=False,
            border_right=False,
        )
        t.add(cell("Total Sum EUR:", Alignment.RIGHT, col_span=6))
        t.add(cell("1020.00"))
        t.add(cell("VAT 21%", Alignment.RIGHT, col_span=6))
        t.add(cell("214.20"))
        t.add(cell("Total Sum VAT EUR", Alignment.RIGHT, col_span=6))
        t.add(cell("1234.20"))
        return t

    t = FTable(number_of_rows=7, number_of_columns=7, padding_top=Decimal(20))

    t = add_header(t)
    t = add_items(t)
    t = add_sums(t)

    t.set_padding_on_all_cells(Decimal(2), Decimal(2), Decimal(2), Decimal(2))
    return t


def add_payment_info():
    t = Table(number_of_rows=6, number_of_columns=1, padding_top=Decimal(20))
    payment_due_date = (datetime.now() + timedelta(days=30)).strftime("%Y-%m-%d")
    info = [
        "Invoice issued by: Baron Munchausen",
        f"Payment terms: 30 days, {payment_due_date}",
        "Tel.: +370 800 12345",
        "Bank: Lehmann Brothers",
        "Account: LT79 1234 5678 7777 0000",
        "Please include invoice number in payment details",
    ]
    for text in info:
        t.add(TableCell(Paragraph(text, font=Font.default, font_size=Decimal(8))))
    t.no_borders()
    return t


def main():
    pdf, page_layout = initialize_document()
    item_list = [
        get_logo_image(),
        get_title(),
        get_buyer_seller_info(),
        build_item_table(),
        add_payment_info(),
    ]
    for item in item_list:
        page_layout.add(item)

    with open(PROJECT_ROOT + "/output.pdf", "wb") as pdf_file_handle:
        PDF.dumps(pdf_file_handle, pdf)
