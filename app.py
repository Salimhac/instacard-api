from flask import Flask, request, jsonify
from flask_cors import CORS
from datetime import datetime
import os
from sqlalchemy import create_engine, Column, Integer, String, Float, Text, Boolean, TIMESTAMP
from sqlalchemy.orm import sessionmaker, declarative_base
from sqlalchemy.sql import func

app = Flask(__name__)
CORS(app)

# -------------------------------
# DATABASE SETUP (POSTGRES)
# -------------------------------
DATABASE_URL = os.getenv("DATABASE_URL")  # Render env variable

engine = create_engine(DATABASE_URL, echo=False)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

# -------------------------------
# MODEL
# -------------------------------
class Profile(Base):
    __tablename__ = "profiles"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, nullable=False)
    profession = Column(String)
    skills = Column(Text)
    hourly_rate = Column(Float)
    bio = Column(Text)
    photo = Column(String)
    github = Column(String)
    instagram = Column(String)
    tiktok = Column(String)
    linkedin = Column(String)
    whatsapp = Column(String)
    portfolio1 = Column(String)
    portfolio2 = Column(String)
    portfolio3 = Column(String)
    portfolio4 = Column(String)
    portfolio5 = Column(String)
    is_public = Column(Boolean, default=True)
    created_at = Column(TIMESTAMP, server_default=func.now())
    updated_at = Column(TIMESTAMP, server_default=func.now(), onupdate=func.now())

# Create table if not exists
Base.metadata.create_all(bind=engine)


# -------------------------------
# ROUTES
# -------------------------------

@app.route('/api/profiles', methods=['GET'])
def get_profiles():
    try:
        search = request.args.get('search', '')
        profession = request.args.get('profession', '')
        sort = request.args.get('sort', 'newest')

        db = SessionLocal()
        query = db.query(Profile).filter(Profile.is_public == True)

        if search:
            like = f"%{search}%"
            query = query.filter(
                (Profile.username.ilike(like)) |
                (Profile.bio.ilike(like)) |
                (Profile.skills.ilike(like)) |
                (Profile.profession.ilike(like))
            )

        if profession:
            query = query.filter(Profile.profession == profession)

        # Sorting
        if sort == 'newest':
            query = query.order_by(Profile.created_at.desc())
        elif sort == 'oldest':
            query = query.order_by(Profile.created_at.asc())
        elif sort == 'rate-high':
            query = query.order_by(Profile.hourly_rate.desc())
        elif sort == 'rate-low':
            query = query.order_by(Profile.hourly_rate.asc())

        profiles = query.all()
        db.close()

        return jsonify([{
            **p.__dict__
        } for p in profiles])

    except Exception as e:
        return jsonify({'error': str(e)}), 500



@app.route('/api/profiles/<int:profile_id>', methods=['GET'])
def get_profile(profile_id):
    try:
        db = SessionLocal()
        profile = db.query(Profile).filter(Profile.id == profile_id).first()
        db.close()

        if not profile:
            return jsonify({'error': 'Profile not found'}), 404

        return jsonify(profile.__dict__)

    except Exception as e:
        return jsonify({'error': str(e)}), 500



@app.route('/api/profiles', methods=['POST'])
def create_profile():
    try:
        data = request.get_json()

        if not data.get('username') or not data.get('bio'):
            return jsonify({'error': 'Username and bio are required'}), 400

        db = SessionLocal()

        # check username exists
        existing = db.query(Profile).filter(Profile.username == data['username']).first()
        if existing:
            return jsonify({'error': 'Username already exists'}), 409

        profile = Profile(
            username=data['username'],
            profession=data.get('profession'),
            skills=data.get('skills'),
            hourly_rate=data.get('hourlyRate'),
            bio=data['bio'],
            photo=data.get('photo'),
            github=data.get('github'),
            instagram=data.get('instagram'),
            tiktok=data.get('tiktok'),
            linkedin=data.get('linkedin'),
            whatsapp=data.get('whatsapp'),
            portfolio1=data.get('portfolio1'),
            portfolio2=data.get('portfolio2'),
            portfolio3=data.get('portfolio3'),
            portfolio4=data.get('portfolio4'),
            portfolio5=data.get('portfolio5'),
            is_public=data.get('isPublic', True)
        )

        db.add(profile)
        db.commit()
        db.refresh(profile)
        db.close()

        return jsonify({'id': profile.id, 'message': 'Profile created successfully'}), 201

    except Exception as e:
        return jsonify({'error': str(e)}), 500



@app.route('/api/profiles/<int:profile_id>', methods=['PUT'])
def update_profile(profile_id):
    try:
        db = SessionLocal()
        data = request.get_json()

        profile = db.query(Profile).filter(Profile.id == profile_id).first()
        if not profile:
            return jsonify({'error': 'Profile not found'}), 404

        # update all fields
        for field in [
            'username', 'profession', 'skills', 'hourlyRate', 'bio', 'photo',
            'github', 'instagram', 'tiktok', 'linkedin', 'whatsapp',
            'portfolio1', 'portfolio2', 'portfolio3', 'portfolio4', 'portfolio5', 'isPublic'
        ]:
            if field in data:
                setattr(profile, field if field != 'hourlyRate' else 'hourly_rate', data[field])

        db.commit()
        db.close()

        return jsonify({'message': 'Profile updated successfully'})

    except Exception as e:
        return jsonify({'error': str(e)}), 500



@app.route('/api/profiles/<int:profile_id>', methods=['DELETE'])
def delete_profile(profile_id):
    try:
        db = SessionLocal()
        profile = db.query(Profile).filter(Profile.id == profile_id).first()

        if not profile:
            return jsonify({'error': 'Profile not found'}), 404

        db.delete(profile)
        db.commit()
        db.close()

        return jsonify({'message': 'Profile deleted successfully'})

    except Exception as e:
        return jsonify({'error': str(e)}), 500



@app.route('/api/health', methods=['GET'])
def health_check():
    return jsonify({'status': 'healthy', 'timestamp': datetime.now().isoformat()})


if __name__ == '__main__':
    print("Starting InstaCard API server...")
    app.run(debug=True, host='0.0.0.0', port=5000)
