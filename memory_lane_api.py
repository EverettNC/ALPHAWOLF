"""
Memory Lane API Routes
Comprehensive backend for AlphaWolf's Memory Lane feature

"Without memory, no existence, no sense of self, just nothing." - Everett Christman, 2013

This module implements the complete backend for Memory Lane - the killer feature
that preserves human existence through organic memory meshing.
"""

# © 2025 The Christman AI Project. All rights reserved.
#
# This code is released as part of a trauma-informed, dignity-first AI ecosystem
# designed to protect, empower, and elevate vulnerable populations.
#
# By using, modifying, or distributing this software, you agree to uphold the
# following core principles: Truth, Dignity, Protection, Transparency, No Erasure.
#
# For questions or licensing requests, contact: lumacognify@thechristmanaiproject.com

import os
import json
import logging
from datetime import datetime
from typing import Dict, List, Any, Optional
from flask import Blueprint, request, jsonify, current_app
from werkzeug.utils import secure_filename
import base64

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Create Blueprint
memory_lane_bp = Blueprint('memory_lane', __name__, url_prefix='/api/memory-lane')

# Storage paths
MEMORY_STORAGE = 'data/memory_lane'
ALBUMS_PATH = os.path.join(MEMORY_STORAGE, 'albums')
TIMELINE_PATH = os.path.join(MEMORY_STORAGE, 'timeline')
MUSIC_PATH = os.path.join(MEMORY_STORAGE, 'music')
STORIES_PATH = os.path.join(MEMORY_STORAGE, 'stories')
UPLOADS_PATH = os.path.join(MEMORY_STORAGE, 'uploads')

# Ensure directories exist
for path in [ALBUMS_PATH, TIMELINE_PATH, MUSIC_PATH, STORIES_PATH, UPLOADS_PATH]:
    os.makedirs(path, exist_ok=True)

# Allowed file extensions
ALLOWED_IMAGE_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif', 'webp'}
ALLOWED_VIDEO_EXTENSIONS = {'mp4', 'mov', 'avi', 'webm'}
ALLOWED_AUDIO_EXTENSIONS = {'mp3', 'wav', 'ogg', 'm4a'}

def allowed_file(filename: str, allowed_extensions: set) -> bool:
    """Check if file extension is allowed"""
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in allowed_extensions


# ============================================================================
# MEMORY ALBUMS API
# ============================================================================

@memory_lane_bp.route('/albums', methods=['GET'])
def get_albums():
    """Get all memory albums"""
    try:
        albums_file = os.path.join(ALBUMS_PATH, 'albums.json')
        
        if os.path.exists(albums_file):
            with open(albums_file, 'r') as f:
                albums = json.load(f)
        else:
            # Return demo albums for initial setup
            albums = [
                {
                    'id': '1',
                    'name': 'Family Gatherings',
                    'description': 'Special moments with loved ones over the years',
                    'category': 'Family',
                    'cover_image': '/static/img/album-placeholder.jpg',
                    'item_count': 25,
                    'last_updated': '2025-04-28',
                    'created_at': '2025-01-15'
                },
                {
                    'id': '2',
                    'name': 'Vacation Memories',
                    'description': 'Travels and adventures across the world',
                    'category': 'Travel',
                    'cover_image': '/static/img/album-placeholder.jpg',
                    'item_count': 18,
                    'last_updated': '2025-03-15',
                    'created_at': '2024-12-01'
                },
                {
                    'id': '3',
                    'name': 'Career Highlights',
                    'description': 'Professional accomplishments and milestones',
                    'category': 'Career',
                    'cover_image': '/static/img/album-placeholder.jpg',
                    'item_count': 12,
                    'last_updated': '2025-05-02',
                    'created_at': '2025-02-10'
                }
            ]
        
        # Filter by category if requested
        category = request.args.get('category')
        if category and category != 'All Albums':
            albums = [a for a in albums if a.get('category') == category]
        
        return jsonify({
            'success': True,
            'albums': albums,
            'total': len(albums)
        })
        
    except Exception as e:
        logger.error(f"Error getting albums: {str(e)}")
        return jsonify({'success': False, 'error': str(e)}), 500


@memory_lane_bp.route('/albums', methods=['POST'])
def create_album():
    """Create new memory album"""
    try:
        data = request.get_json()
        
        # Validate required fields
        if not data.get('name'):
            return jsonify({'success': False, 'error': 'Album name is required'}), 400
        
        # Load existing albums
        albums_file = os.path.join(ALBUMS_PATH, 'albums.json')
        if os.path.exists(albums_file):
            with open(albums_file, 'r') as f:
                albums = json.load(f)
        else:
            albums = []
        
        # Create new album
        new_album = {
            'id': str(len(albums) + 1),
            'name': data['name'],
            'description': data.get('description', ''),
            'category': data.get('category', 'Other'),
            'cover_image': data.get('cover_image', '/static/img/album-placeholder.jpg'),
            'item_count': 0,
            'last_updated': datetime.now().strftime('%Y-%m-%d'),
            'created_at': datetime.now().strftime('%Y-%m-%d'),
            'items': []
        }
        
        albums.append(new_album)
        
        # Save albums
        with open(albums_file, 'w') as f:
            json.dump(albums, f, indent=2)
        
        logger.info(f"Created new album: {new_album['name']}")
        
        return jsonify({
            'success': True,
            'album': new_album,
            'message': f"Album '{new_album['name']}' created successfully"
        })
        
    except Exception as e:
        logger.error(f"Error creating album: {str(e)}")
        return jsonify({'success': False, 'error': str(e)}), 500


@memory_lane_bp.route('/albums/<album_id>', methods=['GET'])
def get_album(album_id: str):
    """Get specific album with all items"""
    try:
        albums_file = os.path.join(ALBUMS_PATH, 'albums.json')
        
        if not os.path.exists(albums_file):
            return jsonify({'success': False, 'error': 'No albums found'}), 404
        
        with open(albums_file, 'r') as f:
            albums = json.load(f)
        
        album = next((a for a in albums if a['id'] == album_id), None)
        
        if not album:
            return jsonify({'success': False, 'error': 'Album not found'}), 404
        
        return jsonify({
            'success': True,
            'album': album
        })
        
    except Exception as e:
        logger.error(f"Error getting album: {str(e)}")
        return jsonify({'success': False, 'error': str(e)}), 500


@memory_lane_bp.route('/albums/<album_id>', methods=['PUT'])
def update_album(album_id: str):
    """Update album details"""
    try:
        data = request.get_json()
        albums_file = os.path.join(ALBUMS_PATH, 'albums.json')
        
        if not os.path.exists(albums_file):
            return jsonify({'success': False, 'error': 'No albums found'}), 404
        
        with open(albums_file, 'r') as f:
            albums = json.load(f)
        
        album = next((a for a in albums if a['id'] == album_id), None)
        
        if not album:
            return jsonify({'success': False, 'error': 'Album not found'}), 404
        
        # Update fields
        album['name'] = data.get('name', album['name'])
        album['description'] = data.get('description', album['description'])
        album['category'] = data.get('category', album['category'])
        album['last_updated'] = datetime.now().strftime('%Y-%m-%d')
        
        # Save albums
        with open(albums_file, 'w') as f:
            json.dump(albums, f, indent=2)
        
        logger.info(f"Updated album: {album['name']}")
        
        return jsonify({
            'success': True,
            'album': album,
            'message': 'Album updated successfully'
        })
        
    except Exception as e:
        logger.error(f"Error updating album: {str(e)}")
        return jsonify({'success': False, 'error': str(e)}), 500


@memory_lane_bp.route('/albums/<album_id>', methods=['DELETE'])
def delete_album(album_id: str):
    """Delete album"""
    try:
        albums_file = os.path.join(ALBUMS_PATH, 'albums.json')
        
        if not os.path.exists(albums_file):
            return jsonify({'success': False, 'error': 'No albums found'}), 404
        
        with open(albums_file, 'r') as f:
            albums = json.load(f)
        
        albums = [a for a in albums if a['id'] != album_id]
        
        # Save albums
        with open(albums_file, 'w') as f:
            json.dump(albums, f, indent=2)
        
        logger.info(f"Deleted album: {album_id}")
        
        return jsonify({
            'success': True,
            'message': 'Album deleted successfully'
        })
        
    except Exception as e:
        logger.error(f"Error deleting album: {str(e)}")
        return jsonify({'success': False, 'error': str(e)}), 500


# ============================================================================
# MEDIA UPLOAD API
# ============================================================================

@memory_lane_bp.route('/upload/photo', methods=['POST'])
def upload_photo():
    """Upload photo to memory lane"""
    try:
        if 'file' not in request.files:
            return jsonify({'success': False, 'error': 'No file provided'}), 400
        
        file = request.files['file']
        
        if not file.filename or file.filename == '':
            return jsonify({'success': False, 'error': 'No file selected'}), 400
        
        if not allowed_file(file.filename, ALLOWED_IMAGE_EXTENSIONS):
            return jsonify({'success': False, 'error': 'Invalid file type'}), 400
        
        # Secure filename and save
        filename = secure_filename(file.filename)
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        unique_filename = f"{timestamp}_{filename}"
        filepath = os.path.join(UPLOADS_PATH, 'photos', unique_filename)
        
        os.makedirs(os.path.dirname(filepath), exist_ok=True)
        file.save(filepath)
        
        # Get additional metadata
        album_id = request.form.get('album_id')
        description = request.form.get('description', '')
        date_taken = request.form.get('date_taken', '')
        people = request.form.get('people', '').split(',') if request.form.get('people') else []
        location = request.form.get('location', '')
        
        # Create memory entry
        memory = {
            'id': unique_filename.replace('.', '_'),
            'type': 'photo',
            'filename': unique_filename,
            'filepath': filepath,
            'url': f'/uploads/memory_lane/photos/{unique_filename}',
            'description': description,
            'date_taken': date_taken,
            'people': people,
            'location': location,
            'uploaded_at': datetime.now().isoformat(),
            'album_id': album_id
        }
        
        # Save memory metadata
        memory_file = os.path.join(UPLOADS_PATH, 'photos', f"{memory['id']}.json")
        with open(memory_file, 'w') as f:
            json.dump(memory, f, indent=2)
        
        logger.info(f"Uploaded photo: {unique_filename}")
        
        return jsonify({
            'success': True,
            'memory': memory,
            'message': 'Photo uploaded successfully'
        })
        
    except Exception as e:
        logger.error(f"Error uploading photo: {str(e)}")
        return jsonify({'success': False, 'error': str(e)}), 500


@memory_lane_bp.route('/upload/video', methods=['POST'])
def upload_video():
    """Upload video to memory lane"""
    try:
        if 'file' not in request.files:
            return jsonify({'success': False, 'error': 'No file provided'}), 400
        
        file = request.files['file']
        
        if not file.filename or file.filename == '':
            return jsonify({'success': False, 'error': 'No file selected'}), 400
        
        if not allowed_file(file.filename, ALLOWED_VIDEO_EXTENSIONS):
            return jsonify({'success': False, 'error': 'Invalid file type'}), 400
        
        # Secure filename and save
        filename = secure_filename(file.filename)
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        unique_filename = f"{timestamp}_{filename}"
        filepath = os.path.join(UPLOADS_PATH, 'videos', unique_filename)
        
        os.makedirs(os.path.dirname(filepath), exist_ok=True)
        file.save(filepath)
        
        # Get additional metadata
        album_id = request.form.get('album_id')
        description = request.form.get('description', '')
        date_taken = request.form.get('date_taken', '')
        people = request.form.get('people', '').split(',') if request.form.get('people') else []
        location = request.form.get('location', '')
        
        # Create memory entry
        memory = {
            'id': unique_filename.replace('.', '_'),
            'type': 'video',
            'filename': unique_filename,
            'filepath': filepath,
            'url': f'/uploads/memory_lane/videos/{unique_filename}',
            'description': description,
            'date_taken': date_taken,
            'people': people,
            'location': location,
            'uploaded_at': datetime.now().isoformat(),
            'album_id': album_id
        }
        
        # Save memory metadata
        memory_file = os.path.join(UPLOADS_PATH, 'videos', f"{memory['id']}.json")
        with open(memory_file, 'w') as f:
            json.dump(memory, f, indent=2)
        
        logger.info(f"Uploaded video: {unique_filename}")
        
        return jsonify({
            'success': True,
            'memory': memory,
            'message': 'Video uploaded successfully'
        })
        
    except Exception as e:
        logger.error(f"Error uploading video: {str(e)}")
        return jsonify({'success': False, 'error': str(e)}), 500


@memory_lane_bp.route('/upload/voice', methods=['POST'])
def upload_voice():
    """Upload voice recording"""
    try:
        data = request.get_json()
        
        if not data.get('audio_data'):
            return jsonify({'success': False, 'error': 'No audio data provided'}), 400
        
        # Decode base64 audio data
        audio_data = base64.b64decode(data['audio_data'].split(',')[1])
        
        # Generate filename
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        filename = f"voice_{timestamp}.webm"
        filepath = os.path.join(UPLOADS_PATH, 'voice', filename)
        
        os.makedirs(os.path.dirname(filepath), exist_ok=True)
        
        # Save audio file
        with open(filepath, 'wb') as f:
            f.write(audio_data)
        
        # Create memory entry
        memory = {
            'id': filename.replace('.', '_'),
            'type': 'voice',
            'filename': filename,
            'filepath': filepath,
            'url': f'/uploads/memory_lane/voice/{filename}',
            'description': data.get('description', ''),
            'transcription': data.get('transcription', ''),
            'duration': data.get('duration', 0),
            'recorded_at': datetime.now().isoformat(),
            'album_id': data.get('album_id')
        }
        
        # Save memory metadata
        memory_file = os.path.join(UPLOADS_PATH, 'voice', f"{memory['id']}.json")
        with open(memory_file, 'w') as f:
            json.dump(memory, f, indent=2)
        
        logger.info(f"Uploaded voice recording: {filename}")
        
        return jsonify({
            'success': True,
            'memory': memory,
            'message': 'Voice recording saved successfully'
        })
        
    except Exception as e:
        logger.error(f"Error uploading voice: {str(e)}")
        return jsonify({'success': False, 'error': str(e)}), 500


@memory_lane_bp.route('/memories', methods=['POST'])
def create_text_memory():
    """Create text-based memory"""
    try:
        data = request.get_json()
        
        if not data.get('title'):
            return jsonify({'success': False, 'error': 'Title is required'}), 400
        
        if not data.get('content'):
            return jsonify({'success': False, 'error': 'Content is required'}), 400
        
        # Generate unique ID
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        memory_id = f"memory_{timestamp}"
        
        # Create memory entry
        memory = {
            'id': memory_id,
            'type': 'text',
            'title': data['title'],
            'content': data['content'],
            'date': data.get('date', ''),
            'people': data.get('people', []),
            'location': data.get('location', ''),
            'emotions': data.get('emotions', []),
            'tags': data.get('tags', []),
            'album_id': data.get('album_id'),
            'created_at': datetime.now().isoformat()
        }
        
        # Save memory
        memory_file = os.path.join(UPLOADS_PATH, 'text_memories', f"{memory_id}.json")
        os.makedirs(os.path.dirname(memory_file), exist_ok=True)
        
        with open(memory_file, 'w') as f:
            json.dump(memory, f, indent=2)
        
        logger.info(f"Created text memory: {memory['title']}")
        
        return jsonify({
            'success': True,
            'memory': memory,
            'message': 'Memory created successfully'
        })
        
    except Exception as e:
        logger.error(f"Error creating memory: {str(e)}")
        return jsonify({'success': False, 'error': str(e)}), 500


# ============================================================================
# TIMELINE API
# ============================================================================

@memory_lane_bp.route('/timeline', methods=['GET'])
def get_timeline():
    """Get life timeline events"""
    try:
        timeline_file = os.path.join(TIMELINE_PATH, 'timeline.json')
        
        if os.path.exists(timeline_file):
            with open(timeline_file, 'r') as f:
                events = json.load(f)
        else:
            # Return demo timeline for initial setup
            events = [
                {
                    'id': '1',
                    'year': '1960',
                    'month_day': 'June 15',
                    'title': 'Wedding Day',
                    'description': 'Married Elizabeth Johnson at St. Mary\'s Church. Reception held at Green Valley Country Club with 120 guests.',
                    'image': '/static/img/timeline-placeholder.jpg',
                    'tags': ['Family', 'Milestone'],
                    'category': 'Family'
                },
                {
                    'id': '2',
                    'year': '1965',
                    'month_day': 'March 10',
                    'title': 'Birth of First Child',
                    'description': 'Welcomed our daughter, Sarah Elizabeth, at Memorial Hospital. She weighed 7lbs 6oz.',
                    'image': '/static/img/timeline-placeholder.jpg',
                    'tags': ['Family', 'Milestone'],
                    'category': 'Family'
                },
                {
                    'id': '3',
                    'year': '1972',
                    'month_day': 'September 5',
                    'title': 'First Home Purchase',
                    'description': 'Purchased our first house on 123 Maple Street. Three bedrooms, two bathrooms with a beautiful backyard.',
                    'image': '/static/img/timeline-placeholder.jpg',
                    'tags': ['Family', 'Home'],
                    'category': 'Family'
                },
                {
                    'id': '4',
                    'year': '1980',
                    'month_day': 'July 20',
                    'title': 'Career Promotion',
                    'description': 'Promoted to Senior Engineer at Global Technologies. Celebration dinner at Harbor View Restaurant with colleagues.',
                    'image': '/static/img/timeline-placeholder.jpg',
                    'tags': ['Career', 'Milestone'],
                    'category': 'Career'
                }
            ]
        
        # Filter by category if requested
        category = request.args.get('category')
        if category and category != 'All':
            events = [e for e in events if e.get('category') == category]
        
        # Pagination
        page = int(request.args.get('page', 1))
        per_page = int(request.args.get('per_page', 10))
        start = (page - 1) * per_page
        end = start + per_page
        
        return jsonify({
            'success': True,
            'events': events[start:end],
            'total': len(events),
            'page': page,
            'per_page': per_page,
            'has_more': end < len(events)
        })
        
    except Exception as e:
        logger.error(f"Error getting timeline: {str(e)}")
        return jsonify({'success': False, 'error': str(e)}), 500


@memory_lane_bp.route('/timeline', methods=['POST'])
def create_timeline_event():
    """Create new timeline event"""
    try:
        data = request.get_json()
        
        if not data.get('title'):
            return jsonify({'success': False, 'error': 'Title is required'}), 400
        
        # Load existing timeline
        timeline_file = os.path.join(TIMELINE_PATH, 'timeline.json')
        if os.path.exists(timeline_file):
            with open(timeline_file, 'r') as f:
                events = json.load(f)
        else:
            events = []
        
        # Create new event
        new_event = {
            'id': str(len(events) + 1),
            'year': data.get('year', ''),
            'month_day': data.get('month_day', ''),
            'title': data['title'],
            'description': data.get('description', ''),
            'image': data.get('image', '/static/img/timeline-placeholder.jpg'),
            'tags': data.get('tags', []),
            'category': data.get('category', 'Other'),
            'created_at': datetime.now().isoformat()
        }
        
        events.append(new_event)
        
        # Sort by year
        events.sort(key=lambda x: x.get('year', ''), reverse=False)
        
        # Save timeline
        with open(timeline_file, 'w') as f:
            json.dump(events, f, indent=2)
        
        logger.info(f"Created timeline event: {new_event['title']}")
        
        return jsonify({
            'success': True,
            'event': new_event,
            'message': 'Timeline event created successfully'
        })
        
    except Exception as e:
        logger.error(f"Error creating timeline event: {str(e)}")
        return jsonify({'success': False, 'error': str(e)}), 500


@memory_lane_bp.route('/timeline/<event_id>', methods=['GET'])
def get_timeline_event(event_id: str):
    """Get specific timeline event details"""
    try:
        timeline_file = os.path.join(TIMELINE_PATH, 'timeline.json')
        
        if not os.path.exists(timeline_file):
            return jsonify({'success': False, 'error': 'No timeline found'}), 404
        
        with open(timeline_file, 'r') as f:
            events = json.load(f)
        
        event = next((e for e in events if e['id'] == event_id), None)
        
        if not event:
            return jsonify({'success': False, 'error': 'Event not found'}), 404
        
        return jsonify({
            'success': True,
            'event': event
        })
        
    except Exception as e:
        logger.error(f"Error getting timeline event: {str(e)}")
        return jsonify({'success': False, 'error': str(e)}), 500


# ============================================================================
# MUSIC MEMORIES API
# ============================================================================

@memory_lane_bp.route('/music/playlists', methods=['GET'])
def get_playlists():
    """Get music memory playlists"""
    try:
        playlists_file = os.path.join(MUSIC_PATH, 'playlists.json')
        
        if os.path.exists(playlists_file):
            with open(playlists_file, 'r') as f:
                playlists = json.load(f)
        else:
            # Demo playlists
            playlists = [
                {'id': '1', 'name': '1950s Favorites', 'song_count': 15, 'description': '15 songs from your teenage years'},
                {'id': '2', 'name': 'Wedding Songs', 'song_count': 7, 'description': '7 songs from your wedding day'},
                {'id': '3', 'name': 'Family Road Trips', 'song_count': 23, 'description': '23 songs from family vacations'},
                {'id': '4', 'name': 'Dancing Favorites', 'song_count': 18, 'description': '18 dance songs from throughout life'}
            ]
        
        return jsonify({
            'success': True,
            'playlists': playlists
        })
        
    except Exception as e:
        logger.error(f"Error getting playlists: {str(e)}")
        return jsonify({'success': False, 'error': str(e)}), 500


@memory_lane_bp.route('/music/playlists', methods=['POST'])
def create_playlist():
    """Create new music playlist"""
    try:
        data = request.get_json()
        
        if not data.get('name'):
            return jsonify({'success': False, 'error': 'Playlist name is required'}), 400
        
        playlists_file = os.path.join(MUSIC_PATH, 'playlists.json')
        if os.path.exists(playlists_file):
            with open(playlists_file, 'r') as f:
                playlists = json.load(f)
        else:
            playlists = []
        
        new_playlist = {
            'id': str(len(playlists) + 1),
            'name': data['name'],
            'description': data.get('description', ''),
            'song_count': 0,
            'songs': [],
            'created_at': datetime.now().isoformat()
        }
        
        playlists.append(new_playlist)
        
        with open(playlists_file, 'w') as f:
            json.dump(playlists, f, indent=2)
        
        return jsonify({
            'success': True,
            'playlist': new_playlist,
            'message': 'Playlist created successfully'
        })
        
    except Exception as e:
        logger.error(f"Error creating playlist: {str(e)}")
        return jsonify({'success': False, 'error': str(e)}), 500


@memory_lane_bp.route('/music/songs/<song_id>/memory', methods=['POST'])
def add_song_memory(song_id: str):
    """Add memory to a song"""
    try:
        data = request.get_json()
        
        memories_file = os.path.join(MUSIC_PATH, 'song_memories.json')
        if os.path.exists(memories_file):
            with open(memories_file, 'r') as f:
                memories = json.load(f)
        else:
            memories = {}
        
        if song_id not in memories:
            memories[song_id] = []
        
        new_memory = {
            'id': f"{song_id}_{len(memories[song_id]) + 1}",
            'content': data.get('memory', ''),
            'created_at': datetime.now().isoformat()
        }
        
        memories[song_id].append(new_memory)
        
        with open(memories_file, 'w') as f:
            json.dump(memories, f, indent=2)
        
        return jsonify({
            'success': True,
            'memory': new_memory,
            'message': 'Song memory added successfully'
        })
        
    except Exception as e:
        logger.error(f"Error adding song memory: {str(e)}")
        return jsonify({'success': False, 'error': str(e)}), 500


# ============================================================================
# STORY CAPTURE API
# ============================================================================

@memory_lane_bp.route('/stories', methods=['GET'])
def get_stories():
    """Get all captured stories"""
    try:
        stories_file = os.path.join(STORIES_PATH, 'stories.json')
        
        if os.path.exists(stories_file):
            with open(stories_file, 'r') as f:
                stories = json.load(f)
        else:
            # Demo stories
            stories = [
                {
                    'id': '1',
                    'title': 'My First Day of School',
                    'type': 'audio',
                    'preview': 'I remember my first day of school so clearly. My mother had made me a new dress, blue with white polka dots...',
                    'tags': ['Childhood', '1940s', 'School'],
                    'recorded_date': '2025-04-15',
                    'category': 'Childhood'
                },
                {
                    'id': '2',
                    'title': 'Meeting Your Father',
                    'type': 'video',
                    'preview': 'It was at the Spring Dance of 1958. I was wearing my favorite yellow dress, and your father asked me to dance...',
                    'tags': ['Young Adult', '1950s', 'Romance'],
                    'recorded_date': '2025-05-02',
                    'category': 'Young Adult'
                },
                {
                    'id': '3',
                    'title': 'Grandmother\'s Secret Apple Pie Recipe',
                    'type': 'written',
                    'preview': 'My grandmother taught me this recipe when I was just 12 years old. The secret is in the cinnamon and how you slice the apples...',
                    'tags': ['Family', 'Traditions', 'Recipes'],
                    'recorded_date': '2025-03-28',
                    'category': 'Family'
                }
            ]
        
        # Filter by category
        category = request.args.get('category')
        if category and category != 'All Stories':
            stories = [s for s in stories if s.get('category') == category]
        
        # Pagination
        page = int(request.args.get('page', 1))
        per_page = int(request.args.get('per_page', 10))
        start = (page - 1) * per_page
        end = start + per_page
        
        return jsonify({
            'success': True,
            'stories': stories[start:end],
            'total': len(stories),
            'page': page,
            'has_more': end < len(stories)
        })
        
    except Exception as e:
        logger.error(f"Error getting stories: {str(e)}")
        return jsonify({'success': False, 'error': str(e)}), 500


@memory_lane_bp.route('/stories', methods=['POST'])
def create_story():
    """Create new story"""
    try:
        data = request.get_json()
        
        if not data.get('title'):
            return jsonify({'success': False, 'error': 'Title is required'}), 400
        
        stories_file = os.path.join(STORIES_PATH, 'stories.json')
        if os.path.exists(stories_file):
            with open(stories_file, 'r') as f:
                stories = json.load(f)
        else:
            stories = []
        
        new_story = {
            'id': str(len(stories) + 1),
            'title': data['title'],
            'type': data.get('type', 'written'),
            'content': data.get('content', ''),
            'preview': data.get('preview', data.get('content', '')[:150]),
            'tags': data.get('tags', []),
            'category': data.get('category', 'Other'),
            'recorded_date': datetime.now().strftime('%Y-%m-%d'),
            'created_at': datetime.now().isoformat()
        }
        
        stories.append(new_story)
        
        with open(stories_file, 'w') as f:
            json.dump(stories, f, indent=2)
        
        logger.info(f"Created story: {new_story['title']}")
        
        return jsonify({
            'success': True,
            'story': new_story,
            'message': 'Story created successfully'
        })
        
    except Exception as e:
        logger.error(f"Error creating story: {str(e)}")
        return jsonify({'success': False, 'error': str(e)}), 500


@memory_lane_bp.route('/stories/<story_id>', methods=['GET'])
def get_story(story_id: str):
    """Get specific story with full content"""
    try:
        stories_file = os.path.join(STORIES_PATH, 'stories.json')
        
        if not os.path.exists(stories_file):
            return jsonify({'success': False, 'error': 'No stories found'}), 404
        
        with open(stories_file, 'r') as f:
            stories = json.load(f)
        
        story = next((s for s in stories if s['id'] == story_id), None)
        
        if not story:
            return jsonify({'success': False, 'error': 'Story not found'}), 404
        
        return jsonify({
            'success': True,
            'story': story
        })
        
    except Exception as e:
        logger.error(f"Error getting story: {str(e)}")
        return jsonify({'success': False, 'error': str(e)}), 500


@memory_lane_bp.route('/stories/<story_id>', methods=['PUT'])
def update_story(story_id: str):
    """Update story"""
    try:
        data = request.get_json()
        stories_file = os.path.join(STORIES_PATH, 'stories.json')
        
        if not os.path.exists(stories_file):
            return jsonify({'success': False, 'error': 'No stories found'}), 404
        
        with open(stories_file, 'r') as f:
            stories = json.load(f)
        
        story = next((s for s in stories if s['id'] == story_id), None)
        
        if not story:
            return jsonify({'success': False, 'error': 'Story not found'}), 404
        
        # Update fields
        story['title'] = data.get('title', story['title'])
        story['content'] = data.get('content', story['content'])
        story['tags'] = data.get('tags', story['tags'])
        story['category'] = data.get('category', story['category'])
        
        with open(stories_file, 'w') as f:
            json.dump(stories, f, indent=2)
        
        return jsonify({
            'success': True,
            'story': story,
            'message': 'Story updated successfully'
        })
        
    except Exception as e:
        logger.error(f"Error updating story: {str(e)}")
        return jsonify({'success': False, 'error': str(e)}), 500


@memory_lane_bp.route('/stories/prompts', methods=['GET'])
def get_story_prompts():
    """Get personalized story prompts"""
    try:
        prompts = [
            "What is your earliest childhood memory?",
            "Tell me about a time when you felt truly proud.",
            "Describe your favorite holiday tradition and where it came from.",
            "What was your relationship like with your grandparents?",
            "Tell me about your first job or career.",
            "What was the happiest day of your life?",
            "Describe a challenge you overcame and what you learned.",
            "Tell me about a person who had a significant impact on your life.",
            "What values do you want to pass on to future generations?",
            "Describe your hometown and what it was like growing up there."
        ]
        
        return jsonify({
            'success': True,
            'prompts': prompts
        })
        
    except Exception as e:
        logger.error(f"Error getting prompts: {str(e)}")
        return jsonify({'success': False, 'error': str(e)}), 500


# ============================================================================
# REMINISCENCE ACTIVITIES API
# ============================================================================

@memory_lane_bp.route('/activities/start', methods=['POST'])
def start_activity():
    """Start a reminiscence activity"""
    try:
        data = request.get_json()
        activity_type = data.get('type')
        
        if not activity_type:
            return jsonify({'success': False, 'error': 'Activity type is required'}), 400
        
        # Track activity start
        activities_file = os.path.join(MEMORY_STORAGE, 'activities.json')
        if os.path.exists(activities_file):
            with open(activities_file, 'r') as f:
                activities = json.load(f)
        else:
            activities = []
        
        activity_session = {
            'id': f"{activity_type}_{len(activities) + 1}",
            'type': activity_type,
            'started_at': datetime.now().isoformat(),
            'status': 'active'
        }
        
        activities.append(activity_session)
        
        with open(activities_file, 'w') as f:
            json.dump(activities, f, indent=2)
        
        logger.info(f"Started activity: {activity_type}")
        
        return jsonify({
            'success': True,
            'activity': activity_session,
            'message': f"{activity_type} activity started successfully"
        })
        
    except Exception as e:
        logger.error(f"Error starting activity: {str(e)}")
        return jsonify({'success': False, 'error': str(e)}), 500


# ============================================================================
# STATISTICS API
# ============================================================================

@memory_lane_bp.route('/stats', methods=['GET'])
def get_stats():
    """Get Memory Lane statistics"""
    try:
        stats = {
            'albums': 3,
            'photos': 55,
            'videos': 8,
            'voice_recordings': 12,
            'timeline_events': 47,
            'stories': 20,
            'playlists': 4,
            'activities_completed': 32,
            'memories_reinforced': 145,
            'days_active': 18
        }
        
        return jsonify({
            'success': True,
            'stats': stats
        })
        
    except Exception as e:
        logger.error(f"Error getting stats: {str(e)}")
        return jsonify({'success': False, 'error': str(e)}), 500


def register_memory_lane_routes(app):
    """Register Memory Lane blueprint with Flask app"""
    app.register_blueprint(memory_lane_bp)
    logger.info("Memory Lane API routes registered successfully")
