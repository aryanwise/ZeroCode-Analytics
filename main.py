import tkinter as tk
from tkinter import ttk, filedialog, messagebox, simpledialog
import pandas as pd
import math
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg


class DatasetVisualizerApp(tk.Tk):
    """
    A full-featured GUI application for loading, analyzing, cleaning,
    and visualizing CSV datasets using pandas and tkinter.
    Includes pagination for efficient large dataset display.
    """

    def __init__(self):
        super().__init__()
        self.df = None
        self.df_display = None  # DataFrame currently being shown in the treeview
        self.title("Dataset Visualizer")
        self.geometry("1200x800")

        # --- Pagination State ---
        self.current_page = 1
        self.rows_per_page = 500
        self.total_pages = 1

        # Apply a modern theme
        self.style = ttk.Style(self)
        self.style.theme_use("clam")

        # Configure styles for widgets
        self.style.configure("TButton", padding=6, relief="flat", background="#cceeff")
        self.style.configure(
            "TNotebook.Tab", padding=[10, 5], font=("Helvetica", 10, "bold")
        )
        self.style.configure("Treeview.Heading", font=("Helvetica", 10, "bold"))
        self.style.configure("Pagination.TButton", padding=4, relief="flat")

        self._create_menu()
        self._create_widgets()

    def _create_menu(self):
        """Creates the main menu bar for the application."""
        menu_bar = tk.Menu(self)
        self.config(menu=menu_bar)

        file_menu = tk.Menu(menu_bar, tearoff=0)
        menu_bar.add_cascade(label="File", menu=file_menu)
        file_menu.add_command(label="Load CSV", command=self.load_csv)
        file_menu.add_command(label="Export to CSV", command=self.export_csv)
        file_menu.add_separator()
        file_menu.add_command(label="Exit", command=self.quit)

    def _create_widgets(self):
        """Creates the main layout and widgets of the application."""
        main_frame = ttk.Frame(self, padding="10")
        main_frame.pack(fill=tk.BOTH, expand=True)

        paned_window = ttk.PanedWindow(main_frame, orient=tk.HORIZONTAL)
        paned_window.pack(fill=tk.BOTH, expand=True)

        control_panel = ttk.Notebook(paned_window, width=350)
        paned_window.add(control_panel, weight=1)

        data_frame = ttk.Frame(paned_window)
        paned_window.add(data_frame, weight=3)

        self._create_info_tab(control_panel)
        self._create_cleaning_tab(control_panel)
        self._create_manipulation_tab(control_panel)
        self._create_viz_tab(control_panel)

        # Data display treeview
        self.tree = ttk.Treeview(data_frame, show="headings")
        vsb = ttk.Scrollbar(data_frame, orient="vertical", command=self.tree.yview)
        hsb = ttk.Scrollbar(data_frame, orient="horizontal", command=self.tree.xview)
        self.tree.configure(yscrollcommand=vsb.set, xscrollcommand=hsb.set)

        vsb.pack(side="right", fill="y")
        hsb.pack(side="bottom", fill="x")
        self.tree.pack(fill="both", expand=True)

        # --- NEW: Pagination Controls Frame ---
        self.pagination_frame = ttk.Frame(data_frame, padding=(0, 5))
        # This frame will be packed later when data is loaded

        self.prev_button = ttk.Button(
            self.pagination_frame,
            text="<< Previous",
            command=self.prev_page,
            style="Pagination.TButton",
        )
        self.prev_button.pack(side="left", padx=5)

        self.page_label = ttk.Label(self.pagination_frame, text="Page 1 of 1")
        self.page_label.pack(side="left", padx=10)

        self.next_button = ttk.Button(
            self.pagination_frame,
            text="Next >>",
            command=self.next_page,
            style="Pagination.TButton",
        )
        self.next_button.pack(side="left", padx=5)

        # Status Bar
        self.status_bar = ttk.Label(
            self,
            text="Welcome! Please load a CSV file to begin.",
            relief=tk.SUNKEN,
            anchor=tk.W,
            padding=5,
        )
        self.status_bar.pack(side=tk.BOTTOM, fill=tk.X)

    def _create_info_tab(self, parent):
        """Creates the 'Info' tab with buttons for basic dataset information."""
        tab = ttk.Frame(parent, padding=10)
        parent.add(tab, text="Info")

        ttk.Button(
            tab, text="Dataset Head", command=lambda: self.show_df_info(self.df.head())
        ).pack(fill="x", pady=5)
        ttk.Button(
            tab, text="Dataset Tail", command=lambda: self.show_df_info(self.df.tail())
        ).pack(fill="x", pady=5)
        # --- MODIFIED: Button now sets up pagination ---
        ttk.Button(
            tab,
            text="Show Full Dataset",
            command=lambda: self.setup_pagination(self.df),
        ).pack(fill="x", pady=5)
        ttk.Button(
            tab,
            text="Shape",
            command=lambda: self.show_message(
                "Dataset Shape",
                f"Rows: {self.df.shape[0]}, Columns: {self.df.shape[1]}",
            ),
        ).pack(fill="x", pady=5)
        ttk.Button(
            tab,
            text="Data Types",
            command=lambda: self.show_df_info(self.df.dtypes, "Data Types"),
        ).pack(fill="x", pady=5)
        ttk.Button(
            tab,
            text="Null Value Count",
            command=lambda: self.show_df_info(self.df.isnull().sum(), "Null Values"),
        ).pack(fill="x", pady=5)
        ttk.Button(
            tab,
            text="Summary Statistics",
            command=lambda: self.show_df_info(self.df.describe(), "Summary Statistics"),
        ).pack(fill="x", pady=5)

    # ... (other _create_*_tab methods remain the same) ...
    def _create_cleaning_tab(self, parent):
        """Creates the 'Data Cleaning' tab."""
        tab = ttk.Frame(parent, padding=10)
        parent.add(tab, text="Cleaning")
        ttk.Label(tab, text="Drop Column:").pack(fill="x", pady=(10, 0))
        self.drop_col_var = tk.StringVar()
        self.drop_col_combo = ttk.Combobox(tab, textvariable=self.drop_col_var)
        self.drop_col_combo.pack(fill="x", pady=5)
        ttk.Button(tab, text="Drop Selected Column", command=self.drop_column).pack(
            fill="x", pady=5
        )
        ttk.Button(tab, text="Drop Duplicate Rows", command=self.drop_duplicates).pack(
            fill="x", pady=(15, 5)
        )
        ttk.Label(tab, text="Handle Missing Data:").pack(fill="x", pady=(15, 0))
        self.na_col_var = tk.StringVar()
        self.na_col_combo = ttk.Combobox(tab, textvariable=self.na_col_var)
        self.na_col_combo.pack(fill="x", pady=5)
        self.na_method_var = tk.StringVar(value="drop")
        ttk.Radiobutton(
            tab, text="Drop Rows with NA", variable=self.na_method_var, value="drop"
        ).pack(anchor="w")
        ttk.Radiobutton(
            tab,
            text="Fill with Mean (numeric only)",
            variable=self.na_method_var,
            value="mean",
        ).pack(anchor="w")
        ttk.Radiobutton(
            tab,
            text="Fill with Custom Value",
            variable=self.na_method_var,
            value="value",
        ).pack(anchor="w")
        self.na_fill_value_entry = ttk.Entry(tab)
        self.na_fill_value_entry.pack(fill="x", padx=20, pady=2)
        ttk.Button(tab, text="Apply NA Action", command=self.handle_missing_data).pack(
            fill="x", pady=5
        )

    def _create_manipulation_tab(self, parent):
        """Creates the 'Manipulation' tab for sorting, grouping, etc."""
        tab = ttk.Frame(parent, padding=10)
        parent.add(tab, text="Manipulation")
        ttk.Label(tab, text="Sort Data:").pack(fill="x", pady=(10, 0))
        self.sort_col_var = tk.StringVar()
        self.sort_col_combo = ttk.Combobox(tab, textvariable=self.sort_col_var)
        self.sort_col_combo.pack(fill="x", pady=5)
        self.sort_order_var = tk.StringVar(value="asc")
        ttk.Radiobutton(
            tab, text="Ascending", variable=self.sort_order_var, value="asc"
        ).pack(anchor="w")
        ttk.Radiobutton(
            tab, text="Descending", variable=self.sort_order_var, value="desc"
        ).pack(anchor="w")
        ttk.Button(tab, text="Sort", command=self.sort_data).pack(fill="x", pady=5)
        ttk.Label(tab, text="Group & Aggregate:").pack(fill="x", pady=(15, 0))
        ttk.Label(tab, text="Group by Column:").pack(fill="x")
        self.group_col_var = tk.StringVar()
        self.group_col_combo = ttk.Combobox(tab, textvariable=self.group_col_var)
        self.group_col_combo.pack(fill="x", pady=2)
        ttk.Label(tab, text="Aggregate Column:").pack(fill="x")
        self.agg_col_var = tk.StringVar()
        self.agg_col_combo = ttk.Combobox(tab, textvariable=self.agg_col_var)
        self.agg_col_combo.pack(fill="x", pady=2)
        ttk.Label(tab, text="Function:").pack(fill="x")
        self.agg_func_var = tk.StringVar()
        self.agg_func_combo = ttk.Combobox(
            tab,
            textvariable=self.agg_func_var,
            values=["mean", "sum", "count", "min", "max"],
        )
        self.agg_func_combo.pack(fill="x", pady=2)
        self.agg_func_combo.set("mean")
        ttk.Button(
            tab, text="Group and Aggregate", command=self.group_and_aggregate
        ).pack(fill="x", pady=5)

    def _create_viz_tab(self, parent):
        """Creates the 'Visualization' tab for plotting data."""
        tab = ttk.Frame(parent, padding=10)
        parent.add(tab, text="Visualization")
        self.plot_window = None
        ttk.Label(tab, text="Plot Type:").pack(fill="x", pady=5)
        self.plot_type_var = tk.StringVar()
        self.plot_type_combo = ttk.Combobox(
            tab,
            textvariable=self.plot_type_var,
            values=["Bar", "Histogram", "Line", "Scatter"],
        )
        self.plot_type_combo.pack(fill="x", pady=5)
        self.plot_type_combo.set("Bar")
        self.plot_type_combo.bind("<<ComboboxSelected>>", self.update_plot_options)
        self.plot_x_label = ttk.Label(tab, text="X-Axis Column:")
        self.plot_x_label.pack(fill="x", pady=5)
        self.plot_x_var = tk.StringVar()
        self.plot_x_combo = ttk.Combobox(tab, textvariable=self.plot_x_var)
        self.plot_x_combo.pack(fill="x", pady=5)
        self.plot_y_label = ttk.Label(tab, text="Y-Axis Column (for Scatter/Line):")
        self.plot_y_label.pack(fill="x", pady=5)
        self.plot_y_var = tk.StringVar()
        self.plot_y_combo = ttk.Combobox(tab, textvariable=self.plot_y_var)
        self.plot_y_combo.pack(fill="x", pady=5)
        ttk.Button(tab, text="Generate Plot", command=self.generate_plot).pack(
            fill="x", pady=15
        )
        self.update_plot_options()

    def update_plot_options(self, event=None):
        plot_type = self.plot_type_var.get()
        if plot_type in ["Scatter", "Line"]:
            self.plot_y_label.pack(fill="x", pady=5)
            self.plot_y_combo.pack(fill="x", pady=5)
        else:
            self.plot_y_label.pack_forget()
            self.plot_y_combo.pack_forget()

    def update_status(self, text):
        """Updates the text in the status bar."""
        self.status_bar.config(text=text)
        self.update_idletasks()

    def load_csv(self):
        """Opens a file dialog to load a CSV and displays it using pagination."""
        file_path = filedialog.askopenfilename(
            filetypes=[("CSV Files", "*.csv"), ("All files", "*.*")]
        )
        if not file_path:
            return
        try:
            self.df = pd.read_csv(file_path)
            self.update_all_comboboxes()
            # --- MODIFIED: Use pagination to show the first page on load ---
            self.setup_pagination(self.df)
            self.update_status(
                f"Loaded {file_path} successfully. Shape: {self.df.shape}"
            )
        except Exception as e:
            messagebox.showerror("Error", f"Failed to load file: {e}")
            self.update_status(f"Error loading {file_path}")

    def export_csv(self):
        if self.df is None:
            messagebox.showwarning("Warning", "No data to export.")
            return
        file_path = filedialog.asksaveasfilename(
            defaultextension=".csv", filetypes=[("CSV Files", "*.csv")]
        )
        if not file_path:
            return
        try:
            self.df.to_csv(file_path, index=False)
            messagebox.showinfo("Success", f"Data exported to {file_path}")
            self.update_status(f"Exported data to {file_path}")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to export file: {e}")
            self.update_status(f"Error exporting file.")

    def _populate_treeview(self, df):
        """Internal method to clear and populate the treeview with a DataFrame."""
        self.tree.delete(*self.tree.get_children())
        if df is None or df.empty:
            return

        self.tree["columns"] = list(df.columns)
        for col in df.columns:
            self.tree.heading(col, text=col)
            self.tree.column(col, anchor="w", width=120)

        for index, row in df.iterrows():
            self.tree.insert("", "end", values=list(row))

    # --- NEW & MODIFIED: Pagination Logic ---

    def setup_pagination(self, df):
        """Initializes pagination for a given DataFrame."""
        if df is None:
            messagebox.showwarning("Warning", "No data to display.")
            return

        self.df_display = df
        self.current_page = 1
        self.total_pages = math.ceil(len(self.df_display) / self.rows_per_page)

        self.pagination_frame.pack(side="bottom", fill="x")  # Show the controls
        self.display_page()

    def display_page(self):
        """Calculates the slice of data for the current page and displays it."""
        if self.df_display is None:
            return

        start_row = (self.current_page - 1) * self.rows_per_page
        end_row = start_row + self.rows_per_page
        page_df = self.df_display.iloc[start_row:end_row]

        self._populate_treeview(page_df)
        self.update_pagination_controls()
        self.update_status(
            f"Displaying rows {start_row+1}-{min(end_row, len(self.df_display))} of {len(self.df_display)}"
        )

    def update_pagination_controls(self):
        """Updates the state of pagination buttons and label."""
        self.page_label.config(text=f"Page {self.current_page} of {self.total_pages}")

        self.prev_button.config(state="normal" if self.current_page > 1 else "disabled")
        self.next_button.config(
            state="normal" if self.current_page < self.total_pages else "disabled"
        )

    def next_page(self):
        if self.current_page < self.total_pages:
            self.current_page += 1
            self.display_page()

    def prev_page(self):
        if self.current_page > 1:
            self.current_page -= 1
            self.display_page()

    # --- Other Methods ---

    def update_all_comboboxes(self):
        if self.df is None:
            return
        columns = list(self.df.columns)
        self.drop_col_combo["values"] = columns
        self.na_col_combo["values"] = columns
        self.sort_col_combo["values"] = columns
        self.group_col_combo["values"] = columns
        self.agg_col_combo["values"] = columns
        self.plot_x_combo["values"] = columns
        self.plot_y_combo["values"] = columns

    def show_df_info(self, content, title="Information"):
        if self.df is None:
            messagebox.showwarning("Warning", "Please load a dataset first.")
            return
        info_window = tk.Toplevel(self)
        info_window.title(title)
        info_window.geometry("600x400")
        text_area = tk.Text(info_window, wrap="word", font=("Courier New", 10))
        text_area.pack(padx=10, pady=10, fill="both", expand=True)
        text_area.insert("1.0", str(content))
        text_area.config(state="disabled")

    def show_message(self, title, message):
        if self.df is None:
            messagebox.showwarning("Warning", "Please load a dataset first.")
            return
        messagebox.showinfo(title, message)

    # --- MODIFIED: Analysis Functions to use Pagination ---

    def drop_column(self):
        col_to_drop = self.drop_col_var.get()
        if not col_to_drop:
            return
        self.df.drop(columns=[col_to_drop], inplace=True)
        self.update_all_comboboxes()
        self.setup_pagination(self.df)  # Refresh view
        self.update_status(f"Dropped column: {col_to_drop}")

    def drop_duplicates(self):
        if self.df is None:
            return
        initial_rows = len(self.df)
        self.df.drop_duplicates(inplace=True)
        rows_dropped = initial_rows - len(self.df)
        self.setup_pagination(self.df)  # Refresh view
        self.update_status(f"Dropped {rows_dropped} duplicate rows.")

    def handle_missing_data(self):
        # This function now also refreshes the view using pagination
        if self.df is None:
            return
        col = self.na_col_var.get()
        method = self.na_method_var.get()
        if not col:
            return
        try:
            if method == "drop":
                self.df.dropna(subset=[col], inplace=True)
            elif method == "mean":
                if pd.api.types.is_numeric_dtype(self.df[col]):
                    self.df[col].fillna(self.df[col].mean(), inplace=True)
                else:
                    messagebox.showerror(
                        "Error", "Mean can only be calculated for numeric columns."
                    )
                    return
            elif method == "value":
                fill_val = self.na_fill_value_entry.get()
                if not fill_val:
                    messagebox.showerror("Error", "Please enter a value to fill.")
                    return
                self.df[col].fillna(fill_val, inplace=True)
            self.setup_pagination(self.df)  # Refresh view
        except Exception as e:
            messagebox.showerror("Error", f"An error occurred: {e}")

    def sort_data(self):
        if self.df is None:
            return
        col = self.sort_col_var.get()
        order = self.sort_order_var.get() == "asc"
        if not col:
            return
        self.df.sort_values(by=col, ascending=order, inplace=True)
        self.setup_pagination(self.df)  # Refresh view
        self.update_status(f"Sorted data by '{col}' ({self.sort_order_var.get()}).")

    def group_and_aggregate(self):
        # MODIFIED: Now shows the result in the main paginated view
        if self.df is None:
            return
        group_col = self.group_col_var.get()
        agg_col = self.agg_col_var.get()
        func = self.agg_func_var.get()
        if not all([group_col, agg_col, func]):
            return
        try:
            result_df = self.df.groupby(group_col)[agg_col].agg(func).reset_index()
            self.setup_pagination(result_df)  # Display the aggregated result
            self.update_status(f"Aggregation complete. Displaying result.")
        except Exception as e:
            messagebox.showerror("Error", f"Aggregation failed: {e}")

    def generate_plot(self):
        if self.df is None:
            return
        plot_type = self.plot_type_var.get()
        x_col = self.plot_x_var.get()
        y_col = self.plot_y_var.get()
        if not x_col or (plot_type in ["Scatter", "Line"] and not y_col):
            messagebox.showerror(
                "Error", "Please select the required column(s) for the plot."
            )
            return
        if self.plot_window is None or not self.plot_window.winfo_exists():
            self.plot_window = tk.Toplevel(self)
            self.plot_window.geometry("800x600")
            self.fig, self.ax = plt.subplots(figsize=(7, 5))
            self.canvas = FigureCanvasTkAgg(self.fig, master=self.plot_window)
            self.canvas.get_tk_widget().pack(fill="both", expand=True)
        self.ax.clear()
        try:
            if plot_type == "Bar":
                self.df[x_col].value_counts().nlargest(20).plot(kind="bar", ax=self.ax)
            elif plot_type == "Histogram":
                self.df[x_col].plot(kind="hist", bins=30, ax=self.ax)
            elif plot_type == "Line":
                self.df.plot(kind="line", x=x_col, y=y_col, ax=self.ax)
            elif plot_type == "Scatter":
                self.df.plot(kind="scatter", x=x_col, y=y_col, ax=self.ax)
            self.ax.set_title(f"{plot_type} Plot")
            self.ax.tick_params(axis="x", rotation=45)
            self.fig.tight_layout()
            self.canvas.draw()
        except Exception as e:
            messagebox.showerror("Plotting Error", f"Could not generate plot: {e}")


if __name__ == "__main__":
    app = DatasetVisualizerApp()
    app.mainloop()
