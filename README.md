# Quantalyze

## Overview
Quantalyze is a powerful open-source intelligence (OSINT) case management tool designed for investigators, cybersecurity professionals, and researchers. It provides an efficient way to organize, analyze, and generate reports for OSINT investigations.

## Features
- **Case Management**: Create and manage case files for OSINT investigations.
- **Integrated OSINT Data Storage**: Store IP addresses, social media profiles, domains, and metadata.
- **Report Generation**: Generate professionally styled PDF reports.
- **User-Friendly Interface**: PyQt-based GUI for easy navigation and data entry.
- **Logging & Auditing**: Tracks user activities and case modifications.
- **Configurable Settings**: Customize database, logging, report settings, and themes.

## Installation

### Prerequisites
Ensure you have the following installed:
- Python 3.8+
- PostgreSQL
- Required Python packages (see `requirements.txt`)

### Setup

1. Clone this repository:
   ```bash
   git clone https://github.com/CipherWorkZ/Quantalyze.git
   cd Quantalyze
   ```

2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

3. Configure the `.env` file with database and logging settings.

4. Run the application:
   ```bash
   python app.py
   ```
![Demo Screenshot]((https://i.imgur.com/NLtrFVX.png)

## Usage
1. Open the Quantalyze application.
2. Create a new case and add relevant OSINT data.
3. Generate detailed reports for your investigations.
4. View logs and track case updates.

## License
Quantalyze is released under an open-source license but is not open for public contributions. See the LICENSE file for details.

## Contributions
Currently, this project does not accept external contributions, but suggestions and bug reports are welcome.

## Contact
For inquiries or support, please open an issue on the repository.
