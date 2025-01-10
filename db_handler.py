import sqlite3
import pandas as pd
from datetime import datetime
import logging

class DBHandler:
    def __init__(self, db_path: str = 'data/price_data.db'):
        self.db_path = db_path
        self.setup_database()

    def setup_database(self):
        """Create database and tables if they don't exist"""
        conn = sqlite3.connect(self.db_path)
        try:
            conn.execute('''
                CREATE TABLE IF NOT EXISTS price_data (
                    datetime TEXT,
                    symbol TEXT,
                    open REAL,
                    high REAL,
                    low REAL,
                    close REAL,
                    volume REAL,
                    PRIMARY KEY (datetime, symbol)
                )
            ''')
            conn.execute('CREATE INDEX IF NOT EXISTS idx_symbol_datetime ON price_data(symbol, datetime)')
        finally:
            conn.close()

    def save_tick(self, symbol: str, data: dict):
        """Save tick data to SQLite"""
        conn = sqlite3.connect(self.db_path)
        try:
            conn.execute('''
                INSERT OR REPLACE INTO price_data 
                (datetime, symbol, open, high, low, close, volume)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            ''', (
                data['datetime'],
                symbol,
                data['open'],
                data['high'],
                data['low'],
                data['close'],
                data['volume']
            ))
            conn.commit()
        finally:
            conn.close()

    def export_to_csv(self, symbol: str, start_date: str, end_date: str, output_file: str):
        """Export data range to CSV"""
        conn = sqlite3.connect(self.db_path)
        try:
            query = '''
                SELECT * FROM price_data 
                WHERE symbol = ? 
                AND datetime BETWEEN ? AND ?
                ORDER BY datetime
            '''
            df = pd.read_sql_query(query, conn, params=(symbol, start_date, end_date))
            df.to_csv(output_file, index=False)
            return output_file
        finally:
            conn.close() 