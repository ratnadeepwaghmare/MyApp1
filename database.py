import sqlite3
import json
from datetime import datetime, timedelta
from android_compat import get_android_database_path, is_android
import os


class DatabaseManager:
    def __init__(self, db_path='gym_management.db'):
        self.db_path = get_android_database_path()
        self.initialize_database()
        self.db_path = db_path
        self.initialize_database()

    def initialize_database(self):
        db_dir = os.path.dirname(self.db_path)
        if db_dir and not os.path.exists(db_dir):
            os.makedirs(db_dir, exist_ok=True)
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        # Users table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS users (
                user_id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                aadhar_number TEXT UNIQUE NOT NULL,
                mobile_number TEXT NOT NULL,
                gender TEXT NOT NULL,
                joining_date TEXT NOT NULL,
                address TEXT NOT NULL,
                seat_number INTEGER UNIQUE,
                monthly_fees INTEGER NOT NULL,
                image_path TEXT,
                status TEXT DEFAULT 'Active',
                created_at TEXT DEFAULT CURRENT_TIMESTAMP
            )
        ''')

        # Payments table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS payments (
                payment_id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL,
                amount_paid INTEGER NOT NULL,
                month TEXT NOT NULL,
                year INTEGER NOT NULL,
                payment_date TEXT NOT NULL,
                receipt_number TEXT UNIQUE NOT NULL,
                balance_amount INTEGER NOT NULL,
                created_at TEXT DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (user_id) REFERENCES users (user_id),
                UNIQUE(user_id, month, year)
            )
        ''')

        # Defaulters table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS defaulters (
                defaulter_id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL,
                month TEXT NOT NULL,
                year INTEGER NOT NULL,
                balance_amount INTEGER NOT NULL,
                created_at TEXT DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (user_id) REFERENCES users (user_id),
                UNIQUE(user_id, month, year)
            )
        ''')

        # Backup metadata table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS backup_metadata (
                backup_id INTEGER PRIMARY KEY AUTOINCREMENT,
                backup_name TEXT UNIQUE NOT NULL,
                backup_date TEXT NOT NULL,
                file_path TEXT NOT NULL
            )
        ''')

        conn.commit()
        conn.close()

    def add_user(self, user_data):
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()

            # Check if aadhar already exists
            cursor.execute('SELECT user_id FROM users WHERE aadhar_number = ?', (user_data['aadhar'],))
            if cursor.fetchone():
                return False, "Aadhar number already exists"

            # Check if seat is already taken
            if user_data.get('seat_number'):
                cursor.execute('SELECT user_id FROM users WHERE seat_number = ?', (user_data['seat_number'],))
                if cursor.fetchone():
                    return False, "Seat number already taken"

            cursor.execute('''
                INSERT INTO users 
                (name, aadhar_number, mobile_number, gender, joining_date, address, seat_number, monthly_fees, image_path, status)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                user_data['name'],
                user_data['aadhar'],
                user_data['mobile'],
                user_data['gender'],
                user_data['joining_date'],
                user_data['address'],
                user_data.get('seat_number'),
                user_data['monthly_fees'],
                user_data.get('image_path', ''),
                user_data.get('status', 'Active')
            ))

            user_id = cursor.lastrowid
            conn.commit()
            conn.close()

            return True, user_id
        except sqlite3.IntegrityError as e:
            return False, f"Database integrity error: {str(e)}"
        except Exception as e:
            return False, f"Error adding user: {str(e)}"

    def get_all_users(self):
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        cursor.execute('''
            SELECT user_id, name, aadhar_number, mobile_number, gender, 
                   joining_date, address, seat_number, monthly_fees, image_path, status
            FROM users
            ORDER BY user_id
        ''')

        users = []
        for row in cursor.fetchall():
            users.append({
                'user_id': row[0],
                'name': row[1],
                'aadhar_number': row[2],
                'mobile_number': row[3],
                'gender': row[4],
                'joining_date': row[5],
                'address': row[6],
                'seat_number': row[7],
                'monthly_fees': row[8],
                'image_path': row[9],
                'status': row[10]
            })

        conn.close()
        return users

    def search_users(self, search_term):
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        cursor.execute('''
            SELECT user_id, name, aadhar_number, mobile_number, gender, 
                   joining_date, address, seat_number, monthly_fees, image_path, status
            FROM users
            WHERE user_id LIKE ? OR name LIKE ? OR aadhar_number LIKE ?
        ''', (f'%{search_term}%', f'%{search_term}%', f'%{search_term}%'))

        users = []
        for row in cursor.fetchall():
            users.append({
                'user_id': row[0],
                'name': row[1],
                'aadhar_number': row[2],
                'mobile_number': row[3],
                'gender': row[4],
                'joining_date': row[5],
                'address': row[6],
                'seat_number': row[7],
                'monthly_fees': row[8],
                'image_path': row[9],
                'status': row[10]
            })

        conn.close()
        return users

    def get_user_by_id(self, user_id):
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        cursor.execute('''
            SELECT user_id, name, aadhar_number, mobile_number, gender, 
                   joining_date, address, seat_number, monthly_fees, image_path, status
            FROM users
            WHERE user_id = ?
        ''', (user_id,))

        row = cursor.fetchone()
        conn.close()

        if row:
            return {
                'user_id': row[0],
                'name': row[1],
                'aadhar_number': row[2],
                'mobile_number': row[3],
                'gender': row[4],
                'joining_date': row[5],
                'address': row[6],
                'seat_number': row[7],
                'monthly_fees': row[8],
                'image_path': row[9],
                'status': row[10]
            }
        return None

    def update_user(self, user_data):
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()

            cursor.execute('''
                UPDATE users 
                SET name = ?, mobile_number = ?, monthly_fees = ?, address = ?, status = ?
                WHERE user_id = ?
            ''', (
                user_data['name'],
                user_data['mobile_number'],
                user_data['monthly_fees'],
                user_data['address'],
                user_data['status'],
                user_data['user_id']
            ))

            conn.commit()
            conn.close()
            return True
        except Exception as e:
            print(f"Error updating user: {e}")
            return False

    def delete_user(self, user_id):
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()

            # Delete user
            cursor.execute('DELETE FROM users WHERE user_id = ?', (user_id,))

            conn.commit()
            conn.close()
            return True
        except Exception as e:
            print(f"Error deleting user: {e}")
            return False

    def update_user_status(self, user_id, new_status):
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()

            cursor.execute('''
                UPDATE users 
                SET status = ?
                WHERE user_id = ?
            ''', (new_status, user_id))

            conn.commit()
            conn.close()
            return True
        except Exception as e:
            print(f"Error updating status: {e}")
            return False

    def is_user_defaulter(self, user_id):
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        cursor.execute('''
            SELECT COUNT(*) FROM defaulters 
            WHERE user_id = ? AND balance_amount > 0
        ''', (user_id,))

        count = cursor.fetchone()[0]
        conn.close()
        return count > 0

    def add_payment(self, payment_data):
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()

            # Generate receipt number
            receipt_number = f"RCP{datetime.now().strftime('%Y%m%d%H%M%S')}"

            cursor.execute('''
                INSERT INTO payments 
                (user_id, amount_paid, month, year, payment_date, receipt_number, balance_amount)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            ''', (
                payment_data['user_id'],
                payment_data['amount_paid'],
                payment_data['month'],
                payment_data['year'],
                payment_data['payment_date'],
                receipt_number,
                payment_data['balance_amount']
            ))

            # Update defaulter status
            if payment_data['balance_amount'] > 0:
                cursor.execute('''
                    INSERT OR REPLACE INTO defaulters 
                    (user_id, month, year, balance_amount)
                    VALUES (?, ?, ?, ?)
                ''', (
                    payment_data['user_id'],
                    payment_data['month'],
                    payment_data['year'],
                    payment_data['balance_amount']
                ))
            else:
                cursor.execute('''
                    DELETE FROM defaulters 
                    WHERE user_id = ? AND month = ? AND year = ?
                ''', (
                    payment_data['user_id'],
                    payment_data['month'],
                    payment_data['year']
                ))

            conn.commit()
            conn.close()
            return True, receipt_number
        except sqlite3.IntegrityError:
            return False, "Payment already exists for this user, month, and year"
        except Exception as e:
            return False, str(e)

    def get_payment_by_user_month_year(self, user_id, month, year):
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        cursor.execute('''
            SELECT * FROM payments 
            WHERE user_id = ? AND month = ? AND year = ?
        ''', (user_id, month, year))

        row = cursor.fetchone()
        conn.close()

        if row:
            return {
                'payment_id': row[0],
                'user_id': row[1],
                'amount_paid': row[2],
                'month': row[3],
                'year': row[4],
                'payment_date': row[5],
                'receipt_number': row[6],
                'balance_amount': row[7]
            }
        return None

    def update_payment(self, payment_data):
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()

            cursor.execute('''
                UPDATE payments 
                SET amount_paid = ?, balance_amount = ?
                WHERE payment_id = ?
            ''', (
                payment_data['amount_paid'],
                payment_data['balance_amount'],
                payment_data['payment_id']
            ))

            # Update defaulter status
            if payment_data['balance_amount'] > 0:
                cursor.execute('''
                    INSERT OR REPLACE INTO defaulters 
                    (user_id, month, year, balance_amount)
                    SELECT user_id, month, year, balance_amount 
                    FROM payments 
                    WHERE payment_id = ?
                ''', (payment_data['payment_id'],))
            else:
                cursor.execute('''
                    DELETE FROM defaulters 
                    WHERE user_id = (SELECT user_id FROM payments WHERE payment_id = ?)
                    AND month = (SELECT month FROM payments WHERE payment_id = ?)
                    AND year = (SELECT year FROM payments WHERE payment_id = ?)
                ''', (payment_data['payment_id'], payment_data['payment_id'], payment_data['payment_id']))

            conn.commit()
            conn.close()
            return True
        except Exception as e:
            print(f"Error updating payment: {e}")
            return False

    def delete_payment(self, payment_id):
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()

            cursor.execute('DELETE FROM payments WHERE payment_id = ?', (payment_id,))

            conn.commit()
            conn.close()
            return True
        except Exception as e:
            print(f"Error deleting payment: {e}")
            return False

    def get_defaulters(self):
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        cursor.execute('''
            SELECT u.user_id, u.name, d.month, d.year, d.balance_amount
            FROM defaulters d
            JOIN users u ON d.user_id = u.user_id
            WHERE u.status = 'Active' AND d.balance_amount > 0
            ORDER BY d.year DESC, 
                     CASE d.month 
                         WHEN 'Jan' THEN 1
                         WHEN 'Feb' THEN 2
                         WHEN 'Mar' THEN 3
                         WHEN 'Apr' THEN 4
                         WHEN 'May' THEN 5
                         WHEN 'Jun' THEN 6
                         WHEN 'Jul' THEN 7
                         WHEN 'Aug' THEN 8
                         WHEN 'Sep' THEN 9
                         WHEN 'Oct' THEN 10
                         WHEN 'Nov' THEN 11
                         WHEN 'Dec' THEN 12
                     END DESC
        ''')

        defaulters = []
        for row in cursor.fetchall():
            defaulters.append({
                'user_id': row[0],
                'name': row[1],
                'month': row[2],
                'year': row[3],
                'balance_amount': row[4]
            })

        conn.close()
        return defaulters

    def get_payments_by_user(self, user_id):
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        cursor.execute('''
            SELECT payment_id, user_id, amount_paid, month, year, 
                   payment_date, receipt_number, balance_amount
            FROM payments
            WHERE user_id = ?
            ORDER BY payment_date DESC
        ''', (user_id,))

        payments = []
        for row in cursor.fetchall():
            payments.append({
                'payment_id': row[0],
                'user_id': row[1],
                'amount_paid': row[2],
                'month': row[3],
                'year': row[4],
                'payment_date': row[5],
                'receipt_number': row[6],
                'balance_amount': row[7]
            })

        conn.close()
        return payments

    def export_data(self, table_name):
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        cursor.execute(f'SELECT * FROM {table_name}')
        data = cursor.fetchall()
        columns = [description[0] for description in cursor.description]

        conn.close()
        return {'columns': columns, 'data': data}

    def import_data(self, table_name, data):
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()

            # Clear existing data
            cursor.execute(f'DELETE FROM {table_name}')

            # Insert new data
            placeholders = ', '.join(['?' for _ in data['columns']])
            columns = ', '.join(data['columns'])

            for row in data['data']:
                cursor.execute(f'INSERT INTO {table_name} ({columns}) VALUES ({placeholders})', row)

            conn.commit()
            conn.close()
            return True
        except Exception as e:
            return False