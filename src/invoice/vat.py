from decimal import Decimal
from enum import Enum

from borb.pdf.canvas.layout.layout_element import Alignment
from borb.pdf.canvas.layout.table.fixed_column_width_table import FixedColumnWidthTable as Table
from borb.pdf.canvas.layout.table.flexible_column_width_table import (
    FlexibleColumnWidthTable as FTable,
)
from borb.pdf.canvas.layout.table.table import TableCell
from borb.pdf.canvas.layout.text.paragraph import Paragraph
from config.paths import LOGO_PATH
from src.apps import utils

from .base import Font, InvoiceTemplate


class ItemTableColumns(Enum):
    NUMBER: str = "Nr."
    PRODUCT_ID: str = "Product Code"
    PRODUCT_NAME: str = "Product Name"
    QUANTITY: str = "Quantity"
    PRICE: str = "Price EUR"
    SUM: str = "Sum EUR"
    SUM_VAT: str = "SUM with VAT EUR"


class OrderSummaryItems(Enum):
    total_sum: str = "Total sum EUR"
    vat_sum: str = "VAT EUR"
    total_sum_vat: str = "Total sum with VAT EUR"


class VATInvoice(InvoiceTemplate):
    def generate(self):
        layout = self.initialize_document()
        layout.add(self.get_logo_image(LOGO_PATH))
        layout.add(self.get_title())
        layout.add(self.get_buyer_seller_info())
        layout.add(self.build_item_table())
        layout.add(self.add_payment_info())
        self.save_pdf()

    def build_item_table(self) -> Table:
        table = FTable(
            # header + number of items + 3 sum rows
            number_of_rows=self.invoice_info.order_df.shape[0] + 4,
            number_of_columns=len(ItemTableColumns),
            padding_top=Decimal(20),
        )
        table = self.add_header(table)
        table = self.add_items(table)
        table = self.add_sums(table)
        table.set_padding_on_all_cells(Decimal(2), Decimal(2), Decimal(2), Decimal(2))
        return table

    @staticmethod
    def add_header(table: Table) -> Table:
        for column_name in ItemTableColumns:
            text = Paragraph(
                column_name.value,
                font=Font.bold,
                font_size=Decimal(10),
                text_alignment=Alignment.CENTERED,
            )
            table.add(TableCell(text))
        return table

    def add_items(self, table: Table) -> Table:
        add_cell = lambda text: TableCell(
            Paragraph(
                str(text),
                font=Font.default,
                font_size=Decimal(8),
                text_alignment=Alignment.CENTERED,
            )
        )
        for row_num, row in self.invoice_info.order_df.reset_index(drop=True).iterrows():
            table.add(add_cell(row_num + 1))
            for column_name in ItemTableColumns._member_names_:
                if column_name.lower() in row.index:
                    table.add(add_cell(row[column_name.lower()]))

        return table

    def add_sums(self, table: Table) -> Table:
        cell = lambda text, align=Alignment.CENTERED, col_span=1: TableCell(
            Paragraph(str(text), font=Font.bold, font_size=Decimal(8), text_alignment=align),
            col_span=col_span,
            border_bottom=False,
            border_top=False,
            border_left=False,
            border_right=False,
        )
        order_summary = utils.calculate_order_summary(self.invoice_info.order_df)
        for item in OrderSummaryItems:
            table.add(cell(item.value, Alignment.RIGHT, col_span=table._number_of_columns - 1))
            table.add(cell(order_summary[item.value]))
        return table

