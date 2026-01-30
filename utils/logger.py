import csv
import os
from datetime import datetime
from utils.helpers import get_project_root

def log_to_csv(data, file_name="arbitrage_log.csv"):
    """Saves the found opportunity to a CSV file."""
    root = get_project_root()
    full_path = os.path.join(root, file_name)

    file_exists = os.path.isfile(full_path)

    try:
        with open(full_path, mode='a', newline='', encoding='utf-8') as f:
            writer = csv.writer(f)

            if not file_exists:
                writer.writerow(['Timestamp', 'Pairs', 'Diff USD', 'Diff %', 'Direction'])
            
            writer.writerow([
                datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                data['pair'],
                data['diff_usd'],
                data['diff_percent'],
                data['direction']
            ])
    except Exception as e:
        print(f"Failed to write to log: {e}")