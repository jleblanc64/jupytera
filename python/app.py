import solara
import pandas as pd
from io import BytesIO
import ipywidgets as widgets
from IPython.display import display

class DynamicTable:
    def __init__(self):
        self.rows = []
        self.rows_container = widgets.VBox()

        # ---- Default value widget ----
        self.default_value_input = widgets.IntText(
            description="Default value:",
            value=0,
            layout=widgets.Layout(width="200px")
        )
        self.default_value_input.observe(self.on_default_change, names="value")

        # Add row button
        self.add_btn = widgets.Button(description="Add Row", button_style="success")
        self.add_btn.on_click(self.add_row)

        # Layout
        display(self.default_value_input)
        display(self.add_btn, self.rows_container)

        # Solara download button
        self.download_button = solara.FileDownload(
            self.generate_excel,
            filename="table.xlsx",
            label="Download Excel"
        )
        display(self.download_button)

    # ------------------------------------------------------------
    # When default value changes → update all empty cells
    # ------------------------------------------------------------
    def on_default_change(self, change):
        new_default = str(change["new"])
        for row in self.rows:
            for cell in row["widgets"]:
                if cell.value.strip() == "":
                    cell.value = new_default

    # ------------------------------------------------------------
    # Add a row with default values in empty cells
    # ------------------------------------------------------------
    def add_row(self, b=None):
        default_str = str(self.default_value_input.value)

        cells = []
        for i in range(5):
            t = widgets.Text(description=f"Col {i+1}", value=default_str)

            # When user clears input, restore default value
            def restore_default(change, text_widget=t):
                if change["new"].strip() == "":
                    text_widget.value = str(self.default_value_input.value)

            t.observe(restore_default, names="value")
            cells.append(t)

        # Remove row button
        remove_btn = widgets.Button(
            description="Remove",
            button_style="danger",
            layout=widgets.Layout(width="80px")
        )

        def remove_row(btn):
            self.rows = [r for r in self.rows if r['remove_btn'] != btn]
            self.rows_container.children = [r['hbox'] for r in self.rows]

        remove_btn.on_click(remove_row)

        hbox = widgets.HBox(cells + [remove_btn])
        self.rows.append({'widgets': cells, 'remove_btn': remove_btn, 'hbox': hbox})
        self.rows_container.children += (hbox,)

    # ------------------------------------------------------------
    # Generate Excel with default value for any empty cell
    # ------------------------------------------------------------
    def generate_excel(self):
        default_val = self.default_value_input.value

        data = []
        for row in self.rows:
            processed = []
            for cell in row['widgets']:
                val = cell.value.strip()
                processed.append(val if val != "" else default_val)
            data.append(processed)

        df = pd.DataFrame(data, columns=[f"Column {i+1}" for i in range(5)])

        buffer = BytesIO()
        with pd.ExcelWriter(buffer, engine='openpyxl') as writer:
            df.to_excel(writer, index=False, sheet_name='Data')
        buffer.seek(0)
        return buffer.read()

# Initialize dynamic table
table = DynamicTable()
