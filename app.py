from flask import Flask, request, jsonify
from flask_cors import CORS
import sqlite3
import json
from datetime import datetime
import os

app = Flask(__name__)
CORS(app)  # Enable CORS for all routes

# Database setup
def init_db():
    conn = sqlite3.connect('freelancers.db')
    c = conn.cursor()
    
    # Create profiles table
    c.execute('''
        CREATE TABLE IF NOT EXISTS profiles (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT NOT NULL,
            profession TEXT,
            skills TEXT,
            hourly_rate REAL,
            bio TEXT,
            photo TEXT,
            github TEXT,
            instagram TEXT,
            tiktok TEXT,
            linkedin TEXT,
            whatsapp TEXT,
            portfolio1 TEXT,
            portfolio2 TEXT,
            portfolio3 TEXT,
            portfolio4 TEXT,
            portfolio5 TEXT,
            is_public BOOLEAN DEFAULT 1,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    conn.commit()
    conn.close()

# Database connection helper
def get_db_connection():
    conn = sqlite3.connect('freelancers.db')
    conn.row_factory = sqlite3.Row
    return conn

# Routes
@app.route('/api/profiles', methods=['GET'])
def get_profiles():
    try:
        search = request.args.get('search', '')
        profession = request.args.get('profession', '')
        sort = request.args.get('sort', 'newest')
        
        conn = get_db_connection()
        query = 'SELECT * FROM profiles WHERE is_public = 1'
        params = []
        
        if search:
            query += ' AND (username LIKE ? OR bio LIKE ? OR skills LIKE ? OR profession LIKE ?)'
            search_term = f'%{search}%'
            params.extend([search_term, search_term, search_term, search_term])
        
        if profession:
            query += ' AND profession = ?'
            params.append(profession)
        
        # Sorting
        if sort == 'newest':
            query += ' ORDER BY created_at DESC'
        elif sort == 'oldest':
            query += ' ORDER BY created_at ASC'
        elif sort == 'rate-high':
            query += ' ORDER BY hourly_rate DESC NULLS LAST'
        elif sort == 'rate-low':
            query += ' ORDER BY hourly_rate ASC NULLS LAST'
        
        profiles = conn.execute(query, params).fetchall()
        conn.close()
        
        # Convert to list of dicts
        profiles_list = [dict(profile) for profile in profiles]
        return jsonify(profiles_list)
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/profiles/<int:profile_id>', methods=['GET'])
def get_profile(profile_id):
    try:
        conn = get_db_connection()
        profile = conn.execute('SELECT * FROM profiles WHERE id = ?', (profile_id,)).fetchone()
        conn.close()
        
        if profile is None:
            return jsonify({'error': 'Profile not found'}), 404
        
        return jsonify(dict(profile))
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/profiles', methods=['POST'])
def create_profile():
    try:
        data = request.get_json()
        
        # Validate required fields
        if not data.get('username') or not data.get('bio'):
            return jsonify({'error': 'Username and bio are required'}), 400
        
        conn = get_db_connection()
        
        # Check if profile already exists (by username)
        existing = conn.execute(
            'SELECT id FROM profiles WHERE username = ?', 
            (data['username'],)
        ).fetchone()
        
        if existing:
            return jsonify({'error': 'Username already exists'}), 409
        
        # Insert new profile
        cursor = conn.cursor()
        cursor.execute('''
            INSERT INTO profiles (
                username, profession, skills, hourly_rate, bio, photo,
                github, instagram, tiktok, linkedin, whatsapp,
                portfolio1, portfolio2, portfolio3, portfolio4, portfolio5, is_public
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            data['username'],
            data.get('profession'),
            data.get('skills'),
            data.get('hourlyRate'),
            data['bio'],
            data.get('photo'),
            data.get('github'),
            data.get('instagram'),
            data.get('tiktok'),
            data.get('linkedin'),
            data.get('whatsapp'),
            data.get('portfolio1'),
            data.get('portfolio2'),
            data.get('portfolio3'),
            data.get('portfolio4'),
            data.get('portfolio5'),
            data.get('isPublic', True)
        ))
        
        profile_id = cursor.lastrowid
        conn.commit()
        conn.close()
        
        return jsonify({
            'id': profile_id,
            'message': 'Profile created successfully'
        }), 201
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/profiles/<int:profile_id>', methods=['PUT'])
def update_profile(profile_id):
    try:
        data = request.get_json()
        
        conn = get_db_connection()
        
        # Check if profile exists
        existing = conn.execute(
            'SELECT id FROM profiles WHERE id = ?', 
            (profile_id,)
        ).fetchone()
        
        if not existing:
            return jsonify({'error': 'Profile not found'}), 404
        
        # Update profile
        conn.execute('''
            UPDATE profiles SET
                username = ?, profession = ?, skills = ?, hourly_rate = ?, bio = ?, photo = ?,
                github = ?, instagram = ?, tiktok = ?, linkedin = ?, whatsapp = ?,
                portfolio1 = ?, portfolio2 = ?, portfolio3 = ?, portfolio4 = ?, portfolio5 = ?,
                is_public = ?, updated_at = CURRENT_TIMESTAMP
            WHERE id = ?
        ''', (
            data.get('username'),
            data.get('profession'),
            data.get('skills'),
            data.get('hourlyRate'),
            data.get('bio'),
            data.get('photo'),
            data.get('github'),
            data.get('instagram'),
            data.get('tiktok'),
            data.get('linkedin'),
            data.get('whatsapp'),
            data.get('portfolio1'),
            data.get('portfolio2'),
            data.get('portfolio3'),
            data.get('portfolio4'),
            data.get('portfolio5'),
            data.get('isPublic', True),
            profile_id
        ))
        
        conn.commit()
        conn.close()
        
        return jsonify({'message': 'Profile updated successfully'})
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/profiles/<int:profile_id>', methods=['DELETE'])
def delete_profile(profile_id):
    try:
        conn = get_db_connection()
        
        # Check if profile exists
        existing = conn.execute(
            'SELECT id FROM profiles WHERE id = ?', 
            (profile_id,)
        ).fetchone()
        
        if not existing:
            return jsonify({'error': 'Profile not found'}), 404
        
        conn.execute('DELETE FROM profiles WHERE id = ?', (profile_id,))
        conn.commit()
        conn.close()
        
        return jsonify({'message': 'Profile deleted successfully'})
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500

# Health check
@app.route('/api/health', methods=['GET'])
def health_check():
    return jsonify({'status': 'healthy', 'timestamp': datetime.now().isoformat()})

if __name__ == '__main__':
    # Initialize database
    init_db()
    
    # Run the app
    print("Starting InstaCard API server...")
    print("API available at: http://localhost:5000/api")
    app.run(debug=True, host='0.0.0.0', port=5000)