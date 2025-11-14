import sqlite3
import json
from datetime import datetime
import os

class BackupService:
    def __init__(self, db_path='gym_management.db'):
        self.db_path = db_path
        self.backup_dir = 'backups'

        # Create backup directory if it doesn't exist
        if not os.path.exists(self.backup_dir):
            os.makedirs(self.backup_dir)

    def create_backup(self):
        try:
            # Generate backup filename
            timestamp = datetime.now().strftime('%d%m%Y_%H%M%S')
            backup_filename = f"gym_backup_{timestamp}.db"
            backup_path = os.path.join(self.backup_dir, backup_filename)

            # For Android, we'll use a simple file copy approach
            import shutil
            shutil.copy2(self.db_path, backup_path)

            # Save backup metadata
            self._save_backup_metadata(backup_filename, backup_path)

            return True
        except Exception as e:
            print(f"Backup error: {e}")
            return False

    def _save_backup_metadata(self, backup_name, file_path):
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        cursor.execute('''
            INSERT OR REPLACE INTO backup_metadata (backup_name, backup_date, file_path)
            VALUES (?, ?, ?)
        ''', (backup_name, datetime.now().isoformat(), file_path))

        conn.commit()
        conn.close()

    def restore_backup(self, backup_path=None):
        try:
            if backup_path is None:
                # Get latest backup
                backup_path = self._get_latest_backup()
                if not backup_path:
                    return False

            # Create backup of current database
            self.create_backup()

            # Restore from backup
            import shutil
            shutil.copy2(backup_path, self.db_path)

            return True
        except Exception as e:
            print(f"Restore error: {e}")
            return False

    def _get_latest_backup(self):
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        cursor.execute('''
            SELECT file_path FROM backup_metadata 
            ORDER BY backup_date DESC LIMIT 1
        ''')

        result = cursor.fetchone()
        conn.close()

        return result[0] if result else None

    def schedule_automatic_backup(self):
        # This would be called on app startup to check if automatic backup is needed
        today = datetime.now()
        if today.day == 28:  # 28th of the month
            self.create_backup()