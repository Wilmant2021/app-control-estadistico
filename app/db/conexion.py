"""
Database connection module for SQLite database.
Provides functions to establish connection and initialize the database schema.
"""

import sqlite3
import os


def get_connection():
    """
    Establishes and returns a connection to the SQLite database.
    
    Returns:
        sqlite3.Connection: Database connection object
    """
    # Path to the database file in the data directory
    db_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'data', 'calidad_agricola.db')
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    return conn


def init_db():
    """
    Initializes the database by creating all tables defined in schema.sql.
    Reads the schema file and executes it to create the database structure.
    """
    conn = get_connection()
    cursor = conn.cursor()
    
    # Read and execute schema.sql
    schema_path = os.path.join(os.path.dirname(__file__), 'schema.sql')
    with open(schema_path, 'r', encoding='utf-8') as f:
        schema = f.read()
        cursor.executescript(schema)
    
    conn.commit()
    conn.close()
