import solara
import pandas as pd
from io import BytesIO
import ipywidgets as widgets
from IPython.display import display

class DynamicTable:
    def __init__(self):
        self.rows = []
        self.default = widgets.IntText(description="Default:", value=0, layout=widgets.Layout(width="200px"))
        self.default.observe(lambda c: [cell.set_trait('value', str(c['new'])) for r in self.rows for cell in r[0] if not cell.value.strip()], 'value')
        self.container = widgets.VBox()

        add_btn = widgets.Button(description="Add Row", button_style="success")
        add_btn.on_click(lambda b: self.add_row())

        # Inject CSS for red cell
        display(widgets.HTML("""
        <style>
        .red-cell input {
            background-color: red !important;
        }
        </style>
        """))

        display(self.default, add_btn, self.container,
                solara.FileDownload(self.generate_excel, filename="table.xlsx", label="Download Excel"))

    def add_row(self):
        cells = [widgets.Text(description=f"Col {i+1}", value=str(self.default.value)) for i in range(5)]
        # Make the first cell of the first row red
        if len(self.rows) == 0:
            cells[1].add_class('red-cell')
        for c in cells:
            c.observe(lambda ch, w=c: w.set_trait('value', str(self.default.value)) if not ch['new'].strip() else None, 'value')

        rm = widgets.Button(description="Remove", button_style="danger", layout=widgets.Layout(width="80px"))
        hbox = widgets.HBox(cells + [rm])
        rm.on_click(lambda b: (self.rows.remove(next(r for r in self.rows if r[1] == b)),
                               setattr(self.container, 'children', [r[2] for r in self.rows])))

        self.rows.append((cells, rm, hbox))
        self.container.children = [r[2] for r in self.rows]

    def generate_excel(self):
        df = pd.DataFrame([[c.value.strip() or self.default.value for c in r[0]] for r in self.rows],
                          columns=[f"Col {i+1}" for i in range(5)])
        buf = BytesIO()
        df.to_excel(buf, index=False, sheet_name='Data', engine='openpyxl')
        buf.seek(0)
        return buf.read()

DynamicTable()