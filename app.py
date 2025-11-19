from flask import Flask, request, jsonify
from flask_cors import CORS
from datetime import datetime
import os
import uuid
from sqlalchemy import create_engine, Column, Integer, String, Float, Text, Boolean, TIMESTAMP
from sqlalchemy.orm import sessionmaker, declarative_base
from sqlalchemy.sql import func
from imagekitio import ImageKit
from imagekitio.models.UploadFileRequestOptions import UploadFileRequestOptions

app = Flask(__name__)
CORS(app)

# -------------------------------
# IMAGEKIT CONFIGURATION
# -------------------------------
imagekit = ImageKit(
    private_key=os.getenv('IMAGEKIT_PRIVATE_KEY'),
    public_key=os.getenv('IMAGEKIT_PUBLIC_KEY'),
    url_endpoint=os.getenv('IMAGEKIT_URL_ENDPOINT')
)

# -------------------------------
# DATABASE SETUP (POSTGRES)
# -------------------------------
DATABASE_URL = os.getenv("DATABASE_URL")  # Render env variable
if not DATABASE_URL:
    raise ValueError("DATABASE_URL environment variable is not set!")

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
    delete_code = Column(String, unique=True, nullable=False)
    created_at = Column(TIMESTAMP, server_default=func.now())
    updated_at = Column(TIMESTAMP, server_default=func.now(), onupdate=func.now())

# Create table if not exists
Base.metadata.create_all(bind=engine)

# -------------------------------
# HELPER: serialize profile to JSON
# -------------------------------
def profile_to_dict(profile):
    return {
        "id": profile.id,
        "username": profile.username,
        "profession": profile.profession,
        "skills": profile.skills,
        "hourly_rate": profile.hourly_rate,
        "bio": profile.bio,
        "photo": profile.photo,
        "github": profile.github,
        "instagram": profile.instagram,
        "tiktok": profile.tiktok,
        "linkedin": profile.linkedin,
        "whatsapp": profile.whatsapp,
        "portfolio1": profile.portfolio1,
        "portfolio2": profile.portfolio2,
        "portfolio3": profile.portfolio3,
        "portfolio4": profile.portfolio4,
        "portfolio5": profile.portfolio5,
        "is_public": profile.is_public,
        "delete_code": profile.delete_code,
        "created_at": profile.created_at.isoformat() if profile.created_at else None,
        "updated_at": profile.updated_at.isoformat() if profile.updated_at else None,
    }

# -------------------------------
# IMAGE UPLOAD ENDPOINT
# -------------------------------
@app.route('/api/upload', methods=['POST'])
def upload_image():
    try:
        if 'image' not in request.files:
            return jsonify({'error': 'No file uploaded'}), 400

        file = request.files['image']
        
        if file.filename == '':
            return jsonify({'error': 'No file selected'}), 400

        # Validate file type
        allowed_extensions = {'png', 'jpg', 'jpeg', 'gif', 'webp', 'bmp'}
        if not ('.' in file.filename and 
                file.filename.rsplit('.', 1)[1].lower() in allowed_extensions):
            return jsonify({'error': 'Invalid file type. Allowed: PNG, JPG, JPEG, GIF, WEBP, BMP'}), 400

        # Validate file size (5MB max)
        file.seek(0, os.SEEK_END)
        file_length = file.tell()
        file.seek(0)
        
        if file_length > 5 * 1024 * 1024:  # 5MB
            return jsonify({'error': 'File size too large. Maximum 5MB allowed.'}), 400

        # Generate unique filename
        file_extension = file.filename.rsplit('.', 1)[1].lower()
        unique_filename = f"profile_{uuid.uuid4().hex[:8]}.{file_extension}"

        # Upload to ImageKit
        upload_options = UploadFileRequestOptions(
            use_unique_file_name=False,
            folder="/instacard-profiles",
            tags=["profile", "user-upload"]
        )

        result = imagekit.upload_file(
            file=file.read(),
            file_name=unique_filename,
            options=upload_options
        )

        return jsonify({
            'url': result.response.url,
            'fileId': result.response.file_id,
            'message': 'Image uploaded successfully'
        })

    except Exception as e:
        print(f"Upload error: {str(e)}")
        return jsonify({'error': 'Failed to upload image'}), 500

# -------------------------------
# PROFILE ROUTES
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

        return jsonify([profile_to_dict(p) for p in profiles])

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

        return jsonify(profile_to_dict(profile))

    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/profiles', methods=['POST'])
def create_profile():
    try:
        data = request.get_json()

        if not data.get('username') or not data.get('bio'):
            return jsonify({'error': 'Username and bio are required'}), 400

        db = SessionLocal()

        # Check if username exists
        existing = db.query(Profile).filter(Profile.username == data['username']).first()
        if existing:
            return jsonify({'error': 'Username already exists'}), 409

        # Generate unique delete code
        delete_code = str(uuid.uuid4())

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
            is_public=data.get('isPublic', True),
            delete_code=delete_code
        )

        db.add(profile)
        db.commit()
        db.refresh(profile)
        db.close()

        return jsonify({
            'id': profile.id, 
            'delete_code': delete_code,
            'message': 'Profile created successfully'
        }), 201

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

        # Update all fields (excluding delete_code for security)
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
        data = request.get_json()
        
        if not data or 'delete_code' not in data:
            return jsonify({'error': 'Deletion code is required'}), 400

        delete_code = data['delete_code']

        db = SessionLocal()
        profile = db.query(Profile).filter(Profile.id == profile_id).first()

        if not profile:
            return jsonify({'error': 'Profile not found'}), 404

        # Verify deletion code
        if profile.delete_code != delete_code:
            return jsonify({'error': 'Invalid deletion code'}), 403

        db.delete(profile)
        db.commit()
        db.close()

        return jsonify({'message': 'Profile deleted successfully'})

    except Exception as e:
        return jsonify({'error': str(e)}), 500

# -------------------------------
# UTILITY ROUTES
# -------------------------------
@app.route('/api/health', methods=['GET'])
def health_check():
    return jsonify({'status': 'healthy', 'timestamp': datetime.now().isoformat()})

@app.route('/api/imagekit/auth', methods=['GET'])
def imagekit_auth():
    """Optional: For client-side ImageKit uploads"""
    try:
        auth_params = imagekit.get_authentication_parameters()
        return jsonify(auth_params)
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/')
def root():
    return jsonify({'message': 'Welcome to InstaCard API', 'status': 'running'})

if __name__ == '__main__':
    print("Starting InstaCard API server...")
    app.run(debug=True, host='0.0.0.0', port=5000)