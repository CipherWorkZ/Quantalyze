import sys
import psycopg2
import logging
from dotenv import load_dotenv
import os
from PyQt6.QtWidgets import (QApplication, QMessageBox, QDateEdit, QFileDialog, QTabWidget, QMainWindow, QVBoxLayout, QPushButton, QTableWidget, QTableWidgetItem, QWidget, QLineEdit, QLabel, QDialog, QFormLayout, QTextEdit, QComboBox, QHBoxLayout)
from PyQt6.QtCore import Qt, QDate
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter
from reportlab.lib import colors
from reportlab.lib.units import inch
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
from reportlab.lib.styles import getSampleStyleSheet


load_dotenv()

# Configuration Class
class Config:
    """Application Configuration - Loads settings from .env file"""

    # Database
    DB_NAME = os.getenv("DB_NAME", "osint")
    DB_USER = os.getenv("DB_USER", "postgres")
    DB_PASSWORD = os.getenv("DB_PASSWORD", "yourpassword")
    DB_HOST = os.getenv("DB_HOST", "localhost")
    DB_PORT = os.getenv("DB_PORT", "5432")

    # Logging
    LOG_LEVEL = os.getenv("LOG_LEVEL", "DEBUG").upper()
    LOG_FILE_PATH = os.getenv("LOG_FILE_PATH", "logs/user_activity.log")

    # Reports
    REPORT_FONT = os.getenv("REPORT_FONT", "Helvetica")
    REPORT_TITLE = os.getenv("REPORT_TITLE", "OSINT Case Report")
    REPORT_SAVE_PATH = os.getenv("REPORT_SAVE_PATH", "reports/")

    # UI Settings
    THEME_MODE = os.getenv("THEME_MODE", "Dark")

    @classmethod
    def update_setting(cls, key, value):
        """Updates a setting in .env file and reloads configuration"""
        env_file = ".env"
        new_lines = []
        with open(env_file, "r") as file:
            lines = file.readlines()
            for line in lines:
                if line.startswith(f"{key}="):
                    new_lines.append(f"{key}={value}\n")
                else:
                    new_lines.append(line)

        with open(env_file, "w") as file:
            file.writelines(new_lines)

        os.environ[key] = value  # Update environment variable dynamically

# Database Connection
DB_CONN = f"dbname={os.getenv('DB_NAME')} user={os.getenv('DB_USER')} password={os.getenv('DB_PASSWORD')} host={os.getenv('DB_HOST')} port={os.getenv('DB_PORT')}"
# ----------------------LOGS------------------------------
LOG_DIR = "logs"
LOG_FILE = os.path.join(LOG_DIR, "user_activity.log")

if not os.path.exists(os.path.dirname(Config.LOG_FILE_PATH)):
    os.makedirs(os.path.dirname(Config.LOG_FILE_PATH))

# ✅ Now setup logging AFTER `Config` is defined
log_level = getattr(logging, Config.LOG_LEVEL, logging.DEBUG)  # Convert string to log level
logging.basicConfig(
    filename=Config.LOG_FILE_PATH,
    level=log_level,
    format="%(asctime)s - %(levelname)s - %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)

# Logging Functions
def log_info(action, details=""):
    """Log general user actions."""
    message = f"INFO: {action} | Details: {details}"
    logging.info(message)

def log_warning(action, details=""):
    """Log potential issues (e.g., missing user input)."""
    message = f"WARNING: {action} | Details: {details}"
    logging.warning(message)

def log_error(action, error_message):
    """Log errors and exceptions."""
    message = f"ERROR: {action} | Details: {error_message}"
    logging.error(message)
# ----------------------------------------------------

def generate_report(self):
    """Generate a PDF report for the case."""
    options = QFileDialog.Option(0)

    file_path, _ = QFileDialog.getSaveFileName(self, "Save Report", "", "PDF Files (*.pdf)", options=options)

    if not file_path:
        return  # User canceled

    if not file_path.endswith(".pdf"):
        file_path += ".pdf"

    # Create a PDF file
    c = canvas.Canvas(file_path, pagesize=letter)
    width, height = letter

    # Title
    c.setFont("Helvetica-Bold", 16)
    c.drawString(100, height - 50, f"Case Report: {self.case_data[0]}")

    # Case Summary
    c.setFont("Helvetica", 12)
    y_position = height - 80
    c.drawString(100, y_position, f"Subject: {self.case_data[1]}")
    c.drawString(100, y_position - 20, f"Username: {self.case_data[2]}")
    c.drawString(100, y_position - 40, f"Description: {self.case_data[3]}")
    c.drawString(100, y_position - 60, f"Created At: {self.case_data[4]}")
    c.drawString(100, y_position - 80, f"Last Updated: {self.case_data[5]}")

    y_position -= 120  # Move further down

    # IP Addresses
    if self.case_ips:
        c.setFont("Helvetica-Bold", 14)
        c.drawString(100, y_position, "IP Addresses")
        y_position -= 20
        c.setFont("Helvetica", 12)
        for ip in self.case_ips:
            c.drawString(100, y_position, f"{ip[0]} - {ip[1]} ({ip[2]}) Last Seen: {ip[3]}")
            y_position -= 20

    # Domains
    if self.case_domains:
        c.setFont("Helvetica-Bold", 14)
        c.drawString(100, y_position, "Domains")
        y_position -= 20
        c.setFont("Helvetica", 12)
        for domain in self.case_domains:
            c.drawString(100, y_position, f"{domain[0]} Last Seen: {domain[1]}")
            y_position -= 20

    # Social Profiles
    if self.case_social_profiles:
        c.setFont("Helvetica-Bold", 14)
        c.drawString(100, y_position, "Social Profiles")
        y_position -= 20
        c.setFont("Helvetica", 12)
        for profile in self.case_social_profiles:
            c.drawString(100, y_position, f"{profile[0]} - {profile[1]}")
            y_position -= 20

    # Metadata
    if self.case_metadata:
        c.setFont("Helvetica-Bold", 14)
        c.drawString(100, y_position, "Metadata")
        y_position -= 20
        c.setFont("Helvetica", 12)
        for meta in self.case_metadata:
            c.drawString(100, y_position, f"{meta[0]} (Source: {meta[1]}, Found: {meta[2]})")
            y_position -= 20

    # Notes
    if self.case_notes:
        c.setFont("Helvetica-Bold", 14)
        c.drawString(100, y_position, "Notes")
        y_position -= 20
        c.setFont("Helvetica", 12)
        for note in self.case_notes:
            c.drawString(100, y_position, f"{note[0]} (Created: {note[1]})")
            y_position -= 20

    # Save PDF
    c.save()

    print(f"Report saved: {file_path}")

def get_osint_cases():
    conn = psycopg2.connect(DB_CONN)
    cur = conn.cursor()
    cur.execute("SELECT id, case_name, subject_name, username FROM cases")
    data = cur.fetchall()
    cur.close()
    conn.close()
    return data

def add_case_info(case_id, category, value):
    conn = psycopg2.connect(DB_CONN)
    cur = conn.cursor()
    
    if category == "IP Address":
        cur.execute("INSERT INTO ips (ip_address) VALUES (%s) RETURNING id", (value,))
        item_id = cur.fetchone()[0]
        cur.execute("INSERT INTO case_ips (case_id, ip_id) VALUES (%s, %s)", (case_id, item_id))
    elif category == "Domain":
        cur.execute("INSERT INTO domains (domain) VALUES (%s) RETURNING id", (value,))
        item_id = cur.fetchone()[0]
        cur.execute("INSERT INTO case_domains (case_id, domain_id) VALUES (%s, %s)", (case_id, item_id))
    elif category == "Social Profile":
        cur.execute("INSERT INTO social_profiles (profile_url) VALUES (%s) RETURNING id", (value,))
        item_id = cur.fetchone()[0]
        cur.execute("INSERT INTO case_social_profiles (case_id, social_profile_id) VALUES (%s, %s)", (case_id, item_id))
    elif category == "Note":
        cur.execute("INSERT INTO notes (case_id, note) VALUES (%s, %s) RETURNING id", (case_id, value))
        note_id = cur.fetchone()[0]
        cur.execute("INSERT INTO case_notes (case_id, note_id) VALUES (%s, %s)", (case_id, note_id))
    
    conn.commit()
    cur.close()
    conn.close()

def get_case_details(case_id):
    conn = psycopg2.connect(DB_CONN)
    cur = conn.cursor()

    # Fetch main case details (Fix: Use NULL-safe approach for timestamps)
    cur.execute("""
        SELECT c.case_name, c.subject_name, c.username, c.description, 
               COALESCE(TO_CHAR(c.created_at, 'YYYY-MM-DD HH24:MI:SS'), 'Unknown'),
               COALESCE(TO_CHAR(c.last_updated, 'YYYY-MM-DD HH24:MI:SS'), 'Unknown')
        FROM cases c
        WHERE c.id = %s;
    """, (case_id,))
    case_info = cur.fetchone()

    if not case_info:
        print(f"Error: No case found for ID {case_id}")
        cur.close()
        conn.close()
        return None

    # Fetch related IPs
    cur.execute("""
        SELECT COALESCE(ip.ip_address, 'N/A'), 
               COALESCE(ip.location, 'N/A'), 
               COALESCE(ip.isp, 'N/A'), 
               COALESCE(TO_CHAR(ip.last_seen, 'YYYY-MM-DD HH24:MI:SS'), 'Unknown')
        FROM case_ips cip
        LEFT JOIN ips ip ON cip.ip_id = ip.id
        WHERE cip.case_id = %s;
    """, (case_id,))
    ips = cur.fetchall()

    # Fetch related Domains
    cur.execute("""
        SELECT COALESCE(d.domain, 'N/A'), 
               COALESCE(TO_CHAR(d.last_seen, 'YYYY-MM-DD HH24:MI:SS'), 'Unknown')
        FROM case_domains cd
        LEFT JOIN domains d ON cd.domain_id = d.id
        WHERE cd.case_id = %s;
    """, (case_id,))
    domains = cur.fetchall()

    # Fetch related Social Profiles
    cur.execute("""
        SELECT COALESCE(sp.platform, 'N/A'), 
               COALESCE(sp.profile_url, 'N/A')
        FROM case_social_profiles csp
        LEFT JOIN social_profiles sp ON csp.social_profile_id = sp.id
        WHERE csp.case_id = %s;
    """, (case_id,))
    social_profiles = cur.fetchall()

    # Fetch Metadata
    cur.execute("""
        SELECT COALESCE(m.info, 'N/A'), 
               COALESCE(m.source, 'N/A'), 
               COALESCE(TO_CHAR(m.date_found, 'YYYY-MM-DD HH24:MI:SS'), 'Unknown')
        FROM case_metadata cm
        LEFT JOIN metadata m ON cm.metadata_id = m.id
        WHERE cm.case_id = %s;
    """, (case_id,))
    metadata = cur.fetchall()

    # Fetch Notes
    cur.execute("""
        SELECT COALESCE(n.note, 'N/A'), 
               COALESCE(TO_CHAR(n.created_at, 'YYYY-MM-DD HH24:MI:SS'), 'Unknown')
        FROM case_notes cn
        LEFT JOIN notes n ON cn.note_id = n.id
        WHERE cn.case_id = %s;
    """, (case_id,))
    notes = cur.fetchall()

    cur.close()
    conn.close()

    return {
        "case_info": case_info,
        "ips": ips,
        "domains": domains,
        "social_profiles": social_profiles,
        "metadata": metadata,
        "notes": notes
    }



def add_case(case_name, subject_name, username, description):
    conn = psycopg2.connect(DB_CONN)
    cur = conn.cursor()

    # Check if the username exists in persons table
    cur.execute("SELECT username FROM persons WHERE username = %s", (username,))
    result = cur.fetchone()

    if not result:
        # If the username does not exist, insert it into persons table
        cur.execute("INSERT INTO persons (full_name, username) VALUES (%s, %s)", (subject_name, username))
        conn.commit()  # Commit to ensure username exists before inserting case

    # Now insert the case
    cur.execute("INSERT INTO cases (case_name, subject_name, username, description) VALUES (%s, %s, %s, %s) RETURNING id",
                (case_name, subject_name, username, description))
    case_id = cur.fetchone()[0]

    conn.commit()
    cur.close()
    conn.close()
    return case_id





class AddCaseDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Create New Case")
        self.setGeometry(300, 300, 400, 300)
        layout = QFormLayout()

        self.case_name_input = QLineEdit()
        self.subject_name_input = QLineEdit()
        self.username_input = QLineEdit()
        self.description_input = QTextEdit()
        self.save_button = QPushButton("Save Case")
        self.save_button.clicked.connect(self.save_case)

        layout.addRow("Case Name:", self.case_name_input)
        layout.addRow("Subject Name:", self.subject_name_input)
        layout.addRow("Username:", self.username_input)
        layout.addRow("Description:", self.description_input)
        layout.addWidget(self.save_button)

        self.setLayout(layout)
        log_info("Opened Add Case Dialog")


    def save_case(self):
        """Saves a new case and logs errors if something goes wrong."""
        try:
            case_name = self.case_name_input.text().strip()
            subject_name = self.subject_name_input.text().strip()
            username = self.username_input.text().strip()
            description = self.description_input.toPlainText().strip()

            if not case_name or not subject_name or not username:
                log_warning("Failed Case Creation", "Missing required fields: Case Name, Subject Name, or Username")
                return

            case_id = add_case(case_name, subject_name, username, description)
            log_info("Created New Case", f"Case ID: {case_id}, Name: {case_name}, Subject: {subject_name}, Username: {username}")
            self.accept()

        except Exception as e:
            log_error("Error Creating Case", str(e))



class AddInfoDialog(QDialog):
    def __init__(self, case_id, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Add Information to Case")
        self.setGeometry(300, 300, 400, 250)
        self.case_id = case_id
        self.parent_dialog = parent  # Store reference to CaseDetailsDialog
        layout = QFormLayout()

        # Dropdown for category selection
        self.category_input = QComboBox()
        self.category_input.addItems(["IP Address", "Domain", "Social Profile", "Note"])

        self.value_input = QTextEdit()
        self.save_button = QPushButton("Save")
        self.save_button.clicked.connect(self.save_info)

        layout.addRow("Category:", self.category_input)
        layout.addRow("Value:", self.value_input)
        layout.addWidget(self.save_button)

        self.setLayout(layout)

    def save_info(self):
        category = self.category_input.currentText().strip()  # Use currentText() to get selected category
        value = self.value_input.toPlainText().strip()
        if category and value:
            add_case_info(self.case_id, category, value)  # Save to database
            self.accept()
            if self.parent_dialog:  # Refresh parent CaseDetailsDialog if exists
                self.parent_dialog.refresh_data()


class CaseDetailsDialog(QDialog):
    def __init__(self, case_id, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Case Details - OSINT Profiler")
        self.setGeometry(300, 300, 800, 600)
        self.setStyleSheet("background-color: #2E2E2E; color: white; font-size: 12pt;")
        self.case_id = case_id

        # Fetch case data from DB
        case_details = get_case_details(self.case_id)
        self.case_data = case_details["case_info"]
        self.case_ips = case_details["ips"]
        self.case_domains = case_details["domains"]
        self.case_social_profiles = case_details["social_profiles"]
        self.case_metadata = case_details["metadata"]
        self.case_notes = case_details["notes"]


        if not self.case_data:
            self.close()
            return

        # Main Layout
        self.main_layout = QVBoxLayout()

        # Add Information Button
        self.add_info_button = QPushButton("Add Information")
        self.add_info_button.clicked.connect(self.open_add_info_dialog)
        self.main_layout.addWidget(self.add_info_button)

        # Case Summary
        case_info = self.case_data[0]
        self.case_summary = QLabel(f"<b>Case Name:</b> {case_info[0]}<br>"
                                   f"<b>Subject Name:</b> {case_info[1]}<br>"
                                   f"<b>Username:</b> {case_info[2]}<br>"
                                   f"<b>Description:</b> {case_info[3]}")
        self.case_summary.setStyleSheet("background-color: #3A3A3A; padding: 10px; border-radius: 5px;")
        self.case_summary.setWordWrap(True)
        self.main_layout.addWidget(self.case_summary)

        # Tabs for Sections
        self.tabs = QTabWidget()
        self.tabs.setStyleSheet("""
            QTabWidget::pane { border: 1px solid #555; background: #1E1E1E; }
            QTabBar::tab { background: #3A3A3A; color: white; padding: 10px; border: 1px solid #555; border-radius: 5px; font-size: 12pt; }
            QTabBar::tab:selected { background: #007ACC; color: white; font-weight: bold; }
            QTabBar::tab:hover { background: #444; color: #FFD700; }
        """)
        self.main_layout.addWidget(self.tabs)

        self.setLayout(self.main_layout)

        # Load Data
        self.refresh_data()

    def refresh_data(self):
        """Reloads the case details dynamically when new data is added."""
        case_details = get_case_details(self.case_id)

        # Assign data to corresponding attributes
        self.case_data = case_details["case_info"]
        self.case_ips = case_details["ips"]
        self.case_domains = case_details["domains"]
        self.case_social_profiles = case_details["social_profiles"]
        self.case_metadata = case_details["metadata"]
        self.case_notes = case_details["notes"]

        # Clear old tabs before reloading
        while self.tabs.count():
            self.tabs.removeTab(0)

        if not self.case_data:
            return
        log_info("Opened Case File", f"Case ID: {self.case_id} - {self.case_data[0]}")

        # Extract Data
        case_info = self.case_data  # This is now a tuple, not a list of tuples

        # Fix incorrect indexing
        social_profiles = [[row[0], row[1]] for row in self.case_social_profiles if row[0] is not None]
        domains = [[row[0]] for row in self.case_domains]
        ips = [[row[0], row[1], row[2], row[3]] for row in self.case_ips]  # IP Address, Location, ISP, Last Seen

        # Update Summary
        self.case_summary.setText(f"<b>Case Name:</b> {case_info[0]}<br>"
                                f"<b>Subject Name:</b> {case_info[1]}<br>"
                                f"<b>Username:</b> {case_info[2]}<br>"
                                f"<b>Description:</b> {case_info[3]}<br>"
                                f"<b>Created At:</b> {case_info[4]}<br>"
                                f"<b>Last Updated:</b> {case_info[5]}")

        # Notes Tab
        self.notes_table = self.create_editable_table(["Notes"], [[n[0]] for n in self.case_notes], "notes", "note")
        self.tabs.addTab(self.notes_table, "Notes")

        # Other Tabs
        self.social_table = self.create_editable_table(["Platform", "Profile URL"], social_profiles, "social_profiles", "profile_url")
        self.tabs.addTab(self.social_table, "Social Profiles")

        self.domains_table = self.create_editable_table(["Domain"], domains, "domains", "domain")
        self.tabs.addTab(self.domains_table, "Domains")

        self.ips_table = self.create_editable_table(["IP Address", "Location", "ISP", "Last Seen"], ips, "ips", "ip_address")
        self.tabs.addTab(self.ips_table, "IP Addresses")


    def create_editable_table(self, headers, data, table_name, column_name):
        """Creates an editable table with checkmark, cancel, and delete buttons."""
        table = QTableWidget()
        table.setColumnCount(len(headers) + 2)  # +2 for action buttons
        table.setHorizontalHeaderLabels(headers + ["Actions", "Delete"])
        table.setRowCount(len(data))

        for row_idx, row_data in enumerate(data):
            for col_idx, value in enumerate(row_data):
                item = QTableWidgetItem(str(value))
                item.setFlags(item.flags() | Qt.ItemFlag.ItemIsEditable)  # Make editable
                table.setItem(row_idx, col_idx, item)

            # Add buttons for save (✔), cancel (❌), and delete (🗑️)
            button_widget = QWidget()
            button_layout = QHBoxLayout()

            save_button = QPushButton("✔")
            save_button.setStyleSheet("background-color: green; color: white; font-size: 12px; padding: 5px;")
            save_button.clicked.connect(lambda _, r=row_idx: self.update_database(table, r, table_name))

            cancel_button = QPushButton("❌")
            cancel_button.setStyleSheet("background-color: red; color: white; font-size: 12px; padding: 5px;")
            cancel_button.clicked.connect(lambda _, r=row_idx: self.cancel_edit(table, r, row_data))

            delete_button = QPushButton("🗑️")
            delete_button.setStyleSheet("background-color: darkred; color: white; font-size: 12px; padding: 5px;")
            delete_button.clicked.connect(lambda _, r=row_idx: self.delete_entry(table, r, table_name, column_name))

            button_layout.addWidget(save_button)
            button_layout.addWidget(cancel_button)
            button_widget.setLayout(button_layout)

            delete_widget = QWidget()
            delete_layout = QHBoxLayout()
            delete_layout.addWidget(delete_button)
            delete_layout.setContentsMargins(0, 0, 0, 0)
            delete_widget.setLayout(delete_layout)

            table.setCellWidget(row_idx, len(headers), button_widget)
            table.setCellWidget(row_idx, len(headers) + 1, delete_widget)

        table.setStyleSheet("""
            QTableWidget { background-color: #3A3A3A; border: 1px solid #555; }
            QHeaderView::section { background-color: #007ACC; color: white; font-weight: bold; border: 1px solid #555; }
        """)

        table.setEditTriggers(QTableWidget.EditTrigger.DoubleClicked)
        table.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        return table

    def delete_entry(self, table, row, table_name, column_name):
        """Deletes a row from the database and updates the UI."""
        conn = psycopg2.connect(DB_CONN)
        cur = conn.cursor()

        # Identify the entry to delete using the first column (primary key or unique value)
        entry_value = table.item(row, 0).text() if table.item(row, 0) else None
        if not entry_value:
            print("Error: No value found to delete.")
            cur.close()
            conn.close()
            return

        # Execute delete query
        delete_query = f"DELETE FROM {table_name} WHERE {column_name} = %s"
        cur.execute(delete_query, (entry_value,))
        conn.commit()

        print(f"Deleted {table_name}: {column_name} = {entry_value}")

        cur.close()
        conn.close()

        # Refresh UI after deletion
        current_tab = self.tabs.currentIndex()
        log_info("Deleted Entry", f"Table: {table_name}, Value: {entry_value}")
        self.refresh_data()
        self.tabs.setCurrentIndex(current_tab)  # Restore the active tab


    def update_database(self, table, row, table_name):
        """Updates only entries linked to the specific case."""
        conn = psycopg2.connect(DB_CONN)
        cur = conn.cursor()

        # Mapping of main tables to their linking tables and correct identifier columns
        link_table_map = {
            "ips": ("case_ips", "ip_id", "ip_address"),  # Match by ip_address
            "domains": ("case_domains", "domain_id", "domain"),  # Match by domain
            "social_profiles": ("case_social_profiles", "social_profile_id", "profile_url"),  # Match by profile_url
            "metadata": ("case_metadata", "metadata_id", "info"),  # Match by info (data field)
            "notes": ("case_notes", "note_id", "note")  # Match by note content
        }

        if table_name not in link_table_map:
            log_info("Update Database Failed", f"Invalid Table: {table_name}")
            cur.close()
            conn.close()
            return

        link_table, link_column, identifier_column = link_table_map[table_name]

        # Get the row's unique identifier based on the correct column name
        identifier_value = table.item(row, 0).text() if table.item(row, 0) else None
        if not identifier_value or identifier_value == "N/A":
            log_info("Update Database Failed", f"Invalid Identifier: {identifier_value} for {table_name}")
            cur.close()
            conn.close()
            return

        # Retrieve the correct ID from the primary table
        cur.execute(f"SELECT id FROM {table_name} WHERE {identifier_column} = %s", (identifier_value,))
        entry = cur.fetchone()

        if not entry:
            log_info("Update Database Failed", f"No Matching Entry for {identifier_value} in {table_name}")
            cur.close()
            conn.close()
            return

        entry_id = entry[0]

        # Check if the record is linked to this case
        cur.execute(f"SELECT 1 FROM {link_table} WHERE case_id = %s AND {link_column} = %s", (self.case_id, entry_id))
        link_check = cur.fetchone()

        if not link_check:
            log_info("Update Database Failed", f"Entry {identifier_value} not linked to Case {self.case_id}")
            cur.close()
            conn.close()
            return

        # Get column names dynamically (excluding action buttons)
        column_names = [table.horizontalHeaderItem(i).text().lower().replace(" ", "_") for i in range(table.columnCount() - 2)]

        # Update only changed values
        for col_idx, column_name in enumerate(column_names):
            table_item = table.item(row, col_idx)
            if table_item is None:
                continue  # Skip empty cells

            new_value = table_item.text()

            # Skip if the value hasn't changed
            cur.execute(f"SELECT {column_name} FROM {table_name} WHERE id = %s", (entry_id,))
            existing_value = cur.fetchone()[0]
            if new_value == str(existing_value):
                continue

            # Execute the update query
            update_query = f"UPDATE {table_name} SET {column_name} = %s WHERE id = %s"
            cur.execute(update_query, (new_value, entry_id))
            conn.commit()

            log_info("Updated Database", f"Table: {table_name}, Column: {column_name}, New Value: {new_value}")

        cur.close()
        conn.close()

        # Preserve the active tab before refreshing
        current_tab = self.tabs.currentIndex()
        self.refresh_data()
        self.tabs.setCurrentIndex(current_tab)  # Restore the active tab after refreshing







    def cancel_edit(self, table, row, original_data):
        """Cancels edit and restores old value when ❌ is clicked."""
        for col_idx, value in enumerate(original_data):
            table.setItem(row, col_idx, QTableWidgetItem(str(value)))

    def open_add_info_dialog(self):
        """Opens a dialog to add new information to the case."""
        dialog = AddInfoDialog(self.case_id, self)
        if dialog.exec():
            self.refresh_data()  # Refresh the case file dialog after adding new info
            log_info("Added Information", f"Case ID: {self.case_id}")

class OSINTManager(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("OSINT Case Manager")
        self.setGeometry(100, 100, 800, 600)
        
        layout = QVBoxLayout()

        self.search_input = QLineEdit(self)
        self.search_input.setPlaceholderText("Enter case name...")
        self.search_btn = QPushButton("Search")
        self.search_btn.clicked.connect(self.search_case)
        
        self.add_case_btn = QPushButton("Create New Case")
        self.add_case_btn.clicked.connect(self.open_add_case_dialog)

        self.view_logs_btn = QPushButton("View Logs")
        self.view_logs_btn.clicked.connect(self.open_log_viewer)

        self.settings_btn = QPushButton("⚙️ Settings")
        self.settings_btn.clicked.connect(self.open_settings_dialog)

        layout.addWidget(QLabel("OSINT Case Search:"))
        layout.addWidget(self.search_input)
        layout.addWidget(self.search_btn)
        layout.addWidget(self.add_case_btn)
        layout.addWidget(self.view_logs_btn)
        layout.addWidget(self.settings_btn)

        self.result_table = QTableWidget()
        self.result_table.setColumnCount(4)
        self.result_table.setHorizontalHeaderLabels(["ID", "Case Name", "Subject Name", "Username"])
        self.result_table.cellDoubleClicked.connect(self.view_case_details)

        layout.addWidget(self.result_table)

        container = QWidget()
        container.setLayout(layout)
        self.setCentralWidget(container)

        self.load_data()
    def open_log_viewer(self):
        """Opens the log viewer dialog."""
        dialog = LogViewer(self)
        dialog.exec()    

    def open_settings_dialog(self):
        """Opens the settings dialog."""
        dialog = SettingsDialog(self)
        if dialog.exec():
            log_info("Settings opened", "User attempting to update the application settings.")

    def load_data(self):
        data = get_osint_cases()
        self.result_table.setColumnCount(5)  # Add an extra column for the "Generate Report" button
        self.result_table.setHorizontalHeaderLabels(["ID", "Case Name", "Subject Name", "Username", "Report"])

        self.result_table.setRowCount(len(data))
        for row, case in enumerate(data):
            for col, value in enumerate(case):
                self.result_table.setItem(row, col, QTableWidgetItem(str(value)))

            # Add "Generate Report" button
            button = QPushButton("📄 Generate Report")
            button.setStyleSheet("background-color: #007ACC; color: white; font-size: 12px; padding: 5px;")
            button.clicked.connect(lambda _, case_id=case[0]: self.generate_report(case_id))

            # Create a widget to hold the button
            button_widget = QWidget()
            button_layout = QHBoxLayout()
            button_layout.addWidget(button)
            button_layout.setContentsMargins(0, 0, 0, 0)
            button_widget.setLayout(button_layout)

            self.result_table.setCellWidget(row, 4, button_widget)  # Insert button into the last column
            log_info("Loaded Cases", f"{len(data)} cases loaded.")


    def generate_report(self, case_id):
        """Generate a professionally styled case report PDF using settings from Config."""
        case_details = get_case_details(case_id)

        if not case_details:
            log_error("Generate Report", f"No case details found for Case ID {case_id}")
            QMessageBox.critical(self, "Report Generation Failed", "No case details found!")
            return

        # **Sanitize the case name for filename usage**
        case_name_clean = case_details["case_info"][0].replace(" ", "_").replace("/", "_")

        # **Generate report filename using settings**
        default_filename = f"{Config.REPORT_TITLE.replace(' ', '_')}_{case_name_clean}.pdf"
        default_save_path = os.path.join(Config.REPORT_SAVE_PATH, default_filename)

        # **Ask user where to save**
        file_path, _ = QFileDialog.getSaveFileName(
            self, "Save Report", default_save_path, "PDF Files (*.pdf)"
        )

        if not file_path:
            return  # User canceled

        if not file_path.endswith(".pdf"):
            file_path += ".pdf"

        # **Ensure report directory exists**
        os.makedirs(Config.REPORT_SAVE_PATH, exist_ok=True)

        # **Create the PDF document**
        doc = SimpleDocTemplate(file_path, pagesize=letter)
        styles = getSampleStyleSheet()
        elements = []

        # **Use the configured font**
        title_style = styles["Title"]
        title_style.fontName = Config.REPORT_FONT

        # **Report Title Section**
        elements.append(Paragraph(f"<b>{Config.REPORT_TITLE}</b>", title_style))
        elements.append(Spacer(1, 0.3 * inch))

        # **Case Header Section**
        case_info = [
            ["Case ID:", case_id],
            ["Person of Interest:", case_details["case_info"][1]],
            ["Username:", case_details["case_info"][2]],
            ["Created At:", case_details["case_info"][4]],
            ["Last Updated:", case_details["case_info"][5]],
        ]
        elements.append(self.create_styled_table(case_info))
        elements.append(Spacer(1, 0.3 * inch))

        # **IP Addresses Section**
        if case_details["ips"]:
            elements.append(Paragraph("<b>IP ADDRESSES</b>", styles["Heading2"]))
            ip_table_data = [["IP Address", "Location", "ISP", "Last Seen"]] + case_details["ips"]
            elements.append(self.create_styled_table(ip_table_data))
            elements.append(Spacer(1, 0.3 * inch))

        # **Domains Section**
        if case_details["domains"]:
            elements.append(Paragraph("<b>DOMAINS</b>", styles["Heading2"]))
            domain_table_data = [["Domain", "Last Seen"]] + case_details["domains"]
            elements.append(self.create_styled_table(domain_table_data))
            elements.append(Spacer(1, 0.3 * inch))

        # **Social Profiles Section**
        if case_details["social_profiles"]:
            elements.append(Paragraph("<b>SOCIAL PROFILES</b>", styles["Heading2"]))
            social_table_data = [["Platform", "Profile URL"]] + case_details["social_profiles"]
            elements.append(self.create_styled_table(social_table_data))
            elements.append(Spacer(1, 0.3 * inch))

        # **Metadata Section**
        if case_details["metadata"]:
            elements.append(Paragraph("<b>METADATA</b>", styles["Heading2"]))
            meta_table_data = [["Info", "Source", "Date Found"]] + case_details["metadata"]
            elements.append(self.create_styled_table(meta_table_data))
            elements.append(Spacer(1, 0.3 * inch))

        # **Case Notes Section**
        if case_details["notes"]:
            elements.append(Paragraph("<b>CASE NOTES</b>", styles["Heading2"]))
            for note in case_details["notes"]:
                elements.append(Paragraph(f"📝 <i>{note[0]}</i> (Created: {note[1]})", styles["Normal"]))
                elements.append(Spacer(1, 0.1 * inch))

        # **Build and Save PDF**
        doc.build(elements)
        log_info("Generate Report", f"Case ID {case_id} report saved at {file_path}")
        QMessageBox.information(self, "Report Generated", f"Report saved successfully:\n{file_path}")

    def create_styled_table(self, data):
        """Creates a professional-style table for the report using Config settings."""
        if not data:
            return Paragraph("<i>No data available</i>", getSampleStyleSheet()["Normal"])

        table = Table(data, colWidths=[120] * len(data[0]))  # Auto column width
        table.setStyle(TableStyle([
            ("BACKGROUND", (0, 0), (-1, 0), colors.darkblue),
            ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
            ("ALIGN", (0, 0), (-1, -1), "CENTER"),
            ("FONTNAME", (0, 0), (-1, 0), Config.REPORT_FONT),  # **Use Config Font**
            ("BOTTOMPADDING", (0, 0), (-1, 0), 8),
            ("BACKGROUND", (0, 1), (-1, -1), colors.whitesmoke),
            ("GRID", (0, 0), (-1, -1), 1, colors.black),
        ]))

        return table



    
    def search_case(self):
        query = self.search_input.text()
        conn = psycopg2.connect(DB_CONN)
        cur = conn.cursor()
        cur.execute("SELECT id, case_name, subject_name, username FROM cases WHERE case_name ILIKE %s", (f"%{query}%",))
        data = cur.fetchall()
        cur.close()
        conn.close()
        
        self.result_table.setRowCount(len(data))
        for row, case in enumerate(data):
            for col, value in enumerate(case):
                self.result_table.setItem(row, col, QTableWidgetItem(str(value)))
                log_info("Search Case", f"Query: {query}, Results: {len(data)}")
    
    def open_add_case_dialog(self):
        dialog = AddCaseDialog(self)
        if dialog.exec():
            self.load_data()
            log_info("Add Case", "A new case was added.")
    
    def view_case_details(self, row, column):
        case_id = self.result_table.item(row, 0).text()
        log_info("View Case Details", f"Case ID {case_id} opened.")
        dialog = CaseDetailsDialog(case_id, self)
        dialog.exec()
LOG_FILE = "logs/user_activity.log"  # Ensure this path is correct


class LogViewer(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Application Logs")
        self.setGeometry(300, 300, 700, 500)
        layout = QVBoxLayout()

        # **Time Range Filters**
        filter_layout = QHBoxLayout()
        self.start_date = QDateEdit(self)
        self.start_date.setCalendarPopup(True)
        self.start_date.setDate(QDate.currentDate().addDays(-7))  # Default: Last 7 days

        self.end_date = QDateEdit(self)
        self.end_date.setCalendarPopup(True)
        self.end_date.setDate(QDate.currentDate())  # Default: Today

        filter_layout.addWidget(QLabel("Start Date:"))
        filter_layout.addWidget(self.start_date)
        filter_layout.addWidget(QLabel("End Date:"))
        filter_layout.addWidget(self.end_date)

        # **Log Level Filter**
        self.level_filter = QComboBox(self)
        self.level_filter.addItems(["ALL", "INFO", "WARNING", "ERROR"])
        filter_layout.addWidget(QLabel("Log Level:"))
        filter_layout.addWidget(self.level_filter)

        # **Apply Filter Button**
        self.filter_button = QPushButton("Apply Filter")
        self.filter_button.clicked.connect(self.apply_filters)

        layout.addLayout(filter_layout)
        layout.addWidget(self.filter_button)

        # **Log Display**
        self.log_text = QTextEdit()
        self.log_text.setReadOnly(True)
        layout.addWidget(self.log_text)

        self.setLayout(layout)
        self.load_logs()  # Initial log load

    def load_logs(self):
        """Loads logs from file and applies filters."""
        if not os.path.exists(LOG_FILE):
            self.log_text.setPlainText("No logs found.")
            return

        with open(LOG_FILE, "r") as f:
            logs = f.readlines()

        filtered_logs = self.filter_logs(logs)
        self.log_text.setPlainText("\n".join(filtered_logs))

    def filter_logs(self, logs):
        """Filters logs based on selected date range and log level."""
        start_date = self.start_date.date().toString("yyyy-MM-dd")
        end_date = self.end_date.date().toString("yyyy-MM-dd")
        selected_level = self.level_filter.currentText()

        filtered = []
        for log in logs:
            parts = log.split(" - ")  # Expected format: "2025-03-05 10:30:00 - INFO - Action..."
            if len(parts) < 3:
                continue  # Skip malformed logs

            log_date, log_level, log_message = parts[0][:10], parts[1], parts[2]

            # **Date Filtering**
            if not (start_date <= log_date <= end_date):
                continue

            # **Log Level Filtering**
            if selected_level != "ALL" and log_level != selected_level:
                continue

            filtered.append(log)

        return filtered

    def apply_filters(self):
        """Refresh logs when filters are applied."""
        self.load_logs()


class SettingsDialog(QDialog):
    """Settings Window to Modify Application Configuration"""
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Settings")
        self.setGeometry(300, 300, 450, 350)
        
        layout = QFormLayout()

        # Database Fields
        self.db_name_input = QLineEdit(Config.DB_NAME)
        self.db_user_input = QLineEdit(Config.DB_USER)
        self.db_password_input = QLineEdit(Config.DB_PASSWORD)
        self.db_host_input = QLineEdit(Config.DB_HOST)
        self.db_port_input = QLineEdit(Config.DB_PORT)

        # Logging
        self.log_level_input = QComboBox()
        self.log_level_input.addItems(["DEBUG", "INFO", "WARNING", "ERROR"])
        self.log_level_input.setCurrentText(Config.LOG_LEVEL)

        # Report Settings
        self.report_font_input = QLineEdit(Config.REPORT_FONT)
        self.report_title_input = QLineEdit(Config.REPORT_TITLE)
        
        # **Report Save Path with Folder Selection**
        self.report_save_path_input = QLineEdit(Config.REPORT_SAVE_PATH)
        self.choose_folder_btn = QPushButton("Choose Folder")
        self.choose_folder_btn.clicked.connect(self.select_report_folder)

        report_path_layout = QHBoxLayout()
        report_path_layout.addWidget(self.report_save_path_input)
        report_path_layout.addWidget(self.choose_folder_btn)

        # Save Button
        self.save_button = QPushButton("Save Settings")
        self.save_button.clicked.connect(self.save_settings)

        # Add Fields to Layout
        layout.addRow("Database Name:", self.db_name_input)
        layout.addRow("Database User:", self.db_user_input)
        layout.addRow("Database Password:", self.db_password_input)
        layout.addRow("Database Host:", self.db_host_input)
        layout.addRow("Database Port:", self.db_port_input)
        layout.addRow("Log Level:", self.log_level_input)
        layout.addRow("Report Font:", self.report_font_input)
        layout.addRow("Report Title:", self.report_title_input)
        layout.addRow("Report Save Path:", report_path_layout)  # Folder selection button

        layout.addWidget(self.save_button)

        self.setLayout(layout)

    def select_report_folder(self):
        """Opens a folder selection dialog for choosing the report save directory."""
        folder = QFileDialog.getExistingDirectory(self, "Select Report Save Folder", self.report_save_path_input.text())
        if folder:
            self.report_save_path_input.setText(folder)

    def save_settings(self):
        """Save new settings, restart app automatically"""
        Config.update_setting("DB_NAME", self.db_name_input.text())
        Config.update_setting("DB_USER", self.db_user_input.text())
        Config.update_setting("DB_PASSWORD", self.db_password_input.text())
        Config.update_setting("DB_HOST", self.db_host_input.text())
        Config.update_setting("DB_PORT", self.db_port_input.text())
        Config.update_setting("LOG_LEVEL", self.log_level_input.currentText())
        Config.update_setting("REPORT_FONT", self.report_font_input.text())
        Config.update_setting("REPORT_TITLE", self.report_title_input.text())
        Config.update_setting("REPORT_SAVE_PATH", self.report_save_path_input.text())

        QMessageBox.information(self, "Settings Updated", "Settings saved! The application will now restart.")

        self.restart_application()

    def restart_application(self):
        """Restarts the application"""
        python = sys.executable  # Path to current Python executable
        os.execl(python, python, *sys.argv)  # Re-run the script with the same arguments



if __name__ == "__main__":
    try:
        app = QApplication(sys.argv)
        window = OSINTManager()
        window.show()
        sys.exit(app.exec())
    except Exception as e:
        log_error("Application Crash", str(e))

