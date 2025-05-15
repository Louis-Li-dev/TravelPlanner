import sqlite3
import json
from datetime import datetime

def init_db():
    conn = sqlite3.connect('itineraries.db')
    cursor = conn.cursor()
    
    # Create table if it doesn't exist
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS itineraries (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        destination TEXT NOT NULL,
        duration TEXT NOT NULL,
        budget TEXT NOT NULL,
        interests TEXT,
        itinerary_data TEXT NOT NULL,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )
    ''')
    
    conn.commit()
    conn.close()

def save_itinerary(destination, duration, budget, interests, itinerary_data):
    conn = sqlite3.connect('itineraries.db')
    cursor = conn.cursor()
    
    cursor.execute('''
    INSERT INTO itineraries (destination, duration, budget, interests, itinerary_data, created_at)
    VALUES (?, ?, ?, ?, ?, ?)
    ''', (
        destination, 
        duration, 
        budget, 
        interests, 
        json.dumps(itinerary_data),
        datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    ))
    
    itinerary_id = cursor.lastrowid
    
    conn.commit()
    conn.close()
    
    return itinerary_id

def get_user_history():
    conn = sqlite3.connect('itineraries.db')
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    
    cursor.execute('SELECT id, destination, duration, budget, created_at FROM itineraries ORDER BY created_at DESC')
    history = [dict(row) for row in cursor.fetchall()]
    
    conn.close()
    
    return history
