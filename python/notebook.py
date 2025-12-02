def run(): pass

import solara
import pandas as pd
from io import BytesIO
import ipywidgets as widgets
from IPython.display import display

class DynamicTable:
    def __init__(self):
        self.rows = []
        self.rows_container = widgets.VBox()

        # Add row button
        self.add_btn = widgets.Button(description="Add Row", button_style="success")
        self.add_btn.on_click(self.add_row)

        # Display table controls
        display(self.add_btn, self.rows_container)

        # Display Solara download button (click triggers Excel generation)
        self.download_button = solara.FileDownload(self.generate_excel, filename="table.xlsx", label="Download Excel")
        display(self.download_button)

    def add_row(self, b=None):
        # Create 5 text inputs
        cells = [widgets.Text(description=f"Col {i+1}") for i in range(5)]

        # Remove row button
        remove_btn = widgets.Button(description="Remove", button_style="danger", layout=widgets.Layout(width="80px"))

        def remove_row(btn):
            self.rows_container.children = [r['hbox'] for r in self.rows if r['remove_btn'] != btn]
            self.rows = [r for r in self.rows if r['remove_btn'] != btn]

        remove_btn.on_click(remove_row)

        hbox = widgets.HBox(cells + [remove_btn])
        self.rows.append({'widgets': cells, 'remove_btn': remove_btn, 'hbox': hbox})
        self.rows_container.children += (hbox,)

    def generate_excel(self):
        """Generate Excel only when user clicks download button"""
        data = [[cell.value for cell in row['widgets']] for row in self.rows]
        df = pd.DataFrame(data, columns=[f"Column {i+1}" for i in range(5)])
        buffer = BytesIO()
        with pd.ExcelWriter(buffer, engine='openpyxl') as writer:
            df.to_excel(writer, index=False, sheet_name='Data')
        buffer.seek(0)
        return buffer.read()

# Initialize dynamic table
table = DynamicTable()







