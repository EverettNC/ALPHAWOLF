/**
 * Memory Lane Frontend JavaScript
 * Connects UI buttons to backend Memory Lane API
 * 
 * "Without memory, no existence, no sense of self, just nothing." - Everett Christman, 2013
 */

// ============================================================================
// API BASE URL
// ============================================================================
const API_BASE = '/api/memory-lane';

// ============================================================================
// MEMORY ALBUMS FUNCTIONALITY
// ============================================================================

/**
 * Load all memory albums
 */
async function loadAlbums(category = 'All Albums') {
    try {
        const response = await fetch(`${API_BASE}/albums?category=${encodeURIComponent(category)}`);
        const data = await response.json();
        
        if (data.success) {
            renderAlbums(data.albums);
        } else {
            showError('Failed to load albums: ' + data.error);
        }
    } catch (error) {
        showError('Error loading albums: ' + error.message);
    }
}

/**
 * Create new album
 */
async function createAlbum() {
    const name = prompt('Enter album name:');
    if (!name) return;
    
    const description = prompt('Enter album description (optional):');
    const category = prompt('Enter category (Family/Travel/Career/Celebrations/Hobbies/Other):') || 'Other';
    
    try {
        const response = await fetch(`${API_BASE}/albums`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ name, description, category })
        });
        
        const data = await response.json();
        
        if (data.success) {
            showSuccess(data.message);
            loadAlbums();
        } else {
            showError('Failed to create album: ' + data.error);
        }
    } catch (error) {
        showError('Error creating album: ' + error.message);
    }
}

/**
 * View album slideshow
 */
async function viewSlideshow(albumId) {
    try {
        const response = await fetch(`${API_BASE}/albums/${albumId}`);
        const data = await response.json();
        
        if (data.success) {
            // TODO: Implement slideshow modal
            showInfo('Slideshow for: ' + data.album.name);
            console.log('Album data:', data.album);
        } else {
            showError('Failed to load album: ' + data.error);
        }
    } catch (error) {
        showError('Error loading album: ' + error.message);
    }
}

/**
 * Edit album
 */
async function editAlbum(albumId) {
    try {
        const response = await fetch(`${API_BASE}/albums/${albumId}`);
        const data = await response.json();
        
        if (!data.success) {
            showError('Failed to load album: ' + data.error);
            return;
        }
        
        const album = data.album;
        const name = prompt('Album name:', album.name);
        if (!name) return;
        
        const description = prompt('Description:', album.description);
        const category = prompt('Category:', album.category);
        
        const updateResponse = await fetch(`${API_BASE}/albums/${albumId}`, {
            method: 'PUT',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ name, description, category })
        });
        
        const updateData = await updateResponse.json();
        
        if (updateData.success) {
            showSuccess(updateData.message);
            loadAlbums();
        } else {
            showError('Failed to update album: ' + updateData.error);
        }
    } catch (error) {
        showError('Error editing album: ' + error.message);
    }
}

// ============================================================================
// MEDIA UPLOAD FUNCTIONALITY
// ============================================================================

/**
 * Upload photos
 */
function uploadPhotos() {
    const input = document.createElement('input');
    input.type = 'file';
    input.multiple = true;
    input.accept = 'image/*';
    
    input.onchange = async (e) => {
        const files = e.target.files;
        if (!files.length) return;
        
        const albumId = prompt('Album ID (optional):');
        const description = prompt('Photo description:');
        
        for (let file of files) {
            await uploadPhoto(file, albumId, description);
        }
        
        showSuccess(`${files.length} photo(s) uploaded successfully`);
    };
    
    input.click();
}

/**
 * Upload single photo
 */
async function uploadPhoto(file, albumId = null, description = '') {
    const formData = new FormData();
    formData.append('file', file);
    if (albumId) formData.append('album_id', albumId);
    if (description) formData.append('description', description);
    
    try {
        const response = await fetch(`${API_BASE}/upload/photo`, {
            method: 'POST',
            body: formData
        });
        
        const data = await response.json();
        
        if (!data.success) {
            showError('Failed to upload photo: ' + data.error);
        }
        
        return data;
    } catch (error) {
        showError('Error uploading photo: ' + error.message);
    }
}

/**
 * Upload video
 */
function uploadVideo() {
    const input = document.createElement('input');
    input.type = 'file';
    input.accept = 'video/*';
    
    input.onchange = async (e) => {
        const file = e.target.files[0];
        if (!file) return;
        
        const albumId = prompt('Album ID (optional):');
        const description = prompt('Video description:');
        
        const formData = new FormData();
        formData.append('file', file);
        if (albumId) formData.append('album_id', albumId);
        if (description) formData.append('description', description);
        
        try {
            showInfo('Uploading video...');
            const response = await fetch(`${API_BASE}/upload/video`, {
                method: 'POST',
                body: formData
            });
            
            const data = await response.json();
            
            if (data.success) {
                showSuccess(data.message);
            } else {
                showError('Failed to upload video: ' + data.error);
            }
        } catch (error) {
            showError('Error uploading video: ' + error.message);
        }
    };
    
    input.click();
}

/**
 * Record voice
 */
async function recordVoice() {
    try {
        const stream = await navigator.mediaDevices.getUserMedia({ audio: true });
        const mediaRecorder = new MediaRecorder(stream);
        const audioChunks = [];
        
        mediaRecorder.addEventListener('dataavailable', event => {
            audioChunks.push(event.data);
        });
        
        mediaRecorder.addEventListener('stop', async () => {
            const audioBlob = new Blob(audioChunks, { type: 'audio/webm' });
            const reader = new FileReader();
            
            reader.onloadend = async () => {
                const base64Audio = reader.result;
                const description = prompt('Voice recording description:');
                
                try {
                    const response = await fetch(`${API_BASE}/upload/voice`, {
                        method: 'POST',
                        headers: { 'Content-Type': 'application/json' },
                        body: JSON.stringify({
                            audio_data: base64Audio,
                            description: description
                        })
                    });
                    
                    const data = await response.json();
                    
                    if (data.success) {
                        showSuccess(data.message);
                    } else {
                        showError('Failed to save voice recording: ' + data.error);
                    }
                } catch (error) {
                    showError('Error saving voice recording: ' + error.message);
                }
            };
            
            reader.readAsDataURL(audioBlob);
            stream.getTracks().forEach(track => track.stop());
        });
        
        // Start recording
        mediaRecorder.start();
        showInfo('Recording... Click OK to stop');
        
        // Stop after user confirms
        setTimeout(() => {
            if (confirm('Stop recording?')) {
                mediaRecorder.stop();
            }
        }, 1000);
        
    } catch (error) {
        showError('Microphone access denied or error: ' + error.message);
    }
}

/**
 * Write text memory
 */
async function writeMemory() {
    const title = prompt('Memory title:');
    if (!title) return;
    
    const content = prompt('Write your memory:');
    if (!content) return;
    
    const albumId = prompt('Album ID (optional):');
    
    try {
        const response = await fetch(`${API_BASE}/memories`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                title: title,
                content: content,
                album_id: albumId
            })
        });
        
        const data = await response.json();
        
        if (data.success) {
            showSuccess(data.message);
        } else {
            showError('Failed to save memory: ' + data.error);
        }
    } catch (error) {
        showError('Error saving memory: ' + error.message);
    }
}

// ============================================================================
// TIMELINE FUNCTIONALITY
// ============================================================================

/**
 * Load timeline events
 */
async function loadTimeline(category = 'All', page = 1) {
    try {
        const response = await fetch(`${API_BASE}/timeline?category=${category}&page=${page}`);
        const data = await response.json();
        
        if (data.success) {
            renderTimeline(data.events);
            if (data.has_more) {
                showLoadMoreButton(() => loadTimeline(category, page + 1));
            }
        } else {
            showError('Failed to load timeline: ' + data.error);
        }
    } catch (error) {
        showError('Error loading timeline: ' + error.message);
    }
}

/**
 * Add timeline event
 */
async function addTimelineEvent() {
    const title = prompt('Event title:');
    if (!title) return;
    
    const year = prompt('Year:');
    const monthDay = prompt('Month and day (e.g., "June 15"):');
    const description = prompt('Description:');
    const category = prompt('Category (Family/Career/Travel/Milestones/Other):') || 'Other';
    
    try {
        const response = await fetch(`${API_BASE}/timeline`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                title: title,
                year: year,
                month_day: monthDay,
                description: description,
                category: category
            })
        });
        
        const data = await response.json();
        
        if (data.success) {
            showSuccess(data.message);
            loadTimeline();
        } else {
            showError('Failed to add event: ' + data.error);
        }
    } catch (error) {
        showError('Error adding event: ' + error.message);
    }
}

/**
 * View timeline event details
 */
async function viewTimelineEvent(eventId) {
    try {
        const response = await fetch(`${API_BASE}/timeline/${eventId}`);
        const data = await response.json();
        
        if (data.success) {
            // TODO: Show event details in modal
            alert(`Event: ${data.event.title}\n\n${data.event.description}`);
        } else {
            showError('Failed to load event: ' + data.error);
        }
    } catch (error) {
        showError('Error loading event: ' + error.message);
    }
}

// ============================================================================
// REMINISCENCE ACTIVITIES
// ============================================================================

/**
 * Start reminiscence activity
 */
async function startActivity(activityType) {
    try {
        const response = await fetch(`${API_BASE}/activities/start`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ type: activityType })
        });
        
        const data = await response.json();
        
        if (data.success) {
            showSuccess(data.message);
            // TODO: Navigate to activity page or show activity modal
            console.log('Activity started:', data.activity);
        } else {
            showError('Failed to start activity: ' + data.error);
        }
    } catch (error) {
        showError('Error starting activity: ' + error.message);
    }
}

// ============================================================================
// MUSIC MEMORIES FUNCTIONALITY
// ============================================================================

/**
 * Load playlists
 */
async function loadPlaylists() {
    try {
        const response = await fetch(`${API_BASE}/music/playlists`);
        const data = await response.json();
        
        if (data.success) {
            renderPlaylists(data.playlists);
        } else {
            showError('Failed to load playlists: ' + data.error);
        }
    } catch (error) {
        showError('Error loading playlists: ' + error.message);
    }
}

/**
 * Create new playlist
 */
async function createPlaylist() {
    const name = prompt('Playlist name:');
    if (!name) return;
    
    const description = prompt('Playlist description (optional):');
    
    try {
        const response = await fetch(`${API_BASE}/music/playlists`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ name, description })
        });
        
        const data = await response.json();
        
        if (data.success) {
            showSuccess(data.message);
            loadPlaylists();
        } else {
            showError('Failed to create playlist: ' + data.error);
        }
    } catch (error) {
        showError('Error creating playlist: ' + error.message);
    }
}

/**
 * Add memory to song
 */
async function addSongMemory(songId) {
    const memory = prompt('What memory does this song bring to mind?');
    if (!memory) return;
    
    try {
        const response = await fetch(`${API_BASE}/music/songs/${songId}/memory`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ memory })
        });
        
        const data = await response.json();
        
        if (data.success) {
            showSuccess(data.message);
        } else {
            showError('Failed to add song memory: ' + data.error);
        }
    } catch (error) {
        showError('Error adding song memory: ' + error.message);
    }
}

// ============================================================================
// STORY CAPTURE FUNCTIONALITY
// ============================================================================

/**
 * Load stories
 */
async function loadStories(category = 'All Stories', page = 1) {
    try {
        const response = await fetch(`${API_BASE}/stories?category=${encodeURIComponent(category)}&page=${page}`);
        const data = await response.json();
        
        if (data.success) {
            renderStories(data.stories);
            if (data.has_more) {
                showLoadMoreButton(() => loadStories(category, page + 1));
            }
        } else {
            showError('Failed to load stories: ' + data.error);
        }
    } catch (error) {
        showError('Error loading stories: ' + error.message);
    }
}

/**
 * Start voice recording for story
 */
async function startVoiceStory() {
    const title = prompt('Story title:');
    if (!title) return;
    
    try {
        const stream = await navigator.mediaDevices.getUserMedia({ audio: true });
        const mediaRecorder = new MediaRecorder(stream);
        const audioChunks = [];
        
        mediaRecorder.addEventListener('dataavailable', event => {
            audioChunks.push(event.data);
        });
        
        mediaRecorder.addEventListener('stop', async () => {
            const audioBlob = new Blob(audioChunks, { type: 'audio/webm' });
            const reader = new FileReader();
            
            reader.onloadend = async () => {
                const base64Audio = reader.result;
                const category = prompt('Category (Childhood/Young Adult/Family/Career/Wisdom/Other):') || 'Other';
                
                try {
                    const response = await fetch(`${API_BASE}/stories`, {
                        method: 'POST',
                        headers: { 'Content-Type': 'application/json' },
                        body: JSON.stringify({
                            title: title,
                            type: 'audio',
                            content: base64Audio,
                            category: category
                        })
                    });
                    
                    const data = await response.json();
                    
                    if (data.success) {
                        showSuccess(data.message);
                        loadStories();
                    } else {
                        showError('Failed to save story: ' + data.error);
                    }
                } catch (error) {
                    showError('Error saving story: ' + error.message);
                }
            };
            
            reader.readAsDataURL(audioBlob);
            stream.getTracks().forEach(track => track.stop());
        });
        
        mediaRecorder.start();
        showInfo('Recording story... Click OK when done');
        
        setTimeout(() => {
            if (confirm('Stop recording?')) {
                mediaRecorder.stop();
            }
        }, 1000);
        
    } catch (error) {
        showError('Microphone access denied or error: ' + error.message);
    }
}

/**
 * Start guided writing for story
 */
async function startGuidedWriting() {
    const title = prompt('Story title:');
    if (!title) return;
    
    const content = prompt('Write your story:');
    if (!content) return;
    
    const category = prompt('Category (Childhood/Young Adult/Family/Career/Wisdom/Other):') || 'Other';
    
    try {
        const response = await fetch(`${API_BASE}/stories`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                title: title,
                type: 'written',
                content: content,
                category: category
            })
        });
        
        const data = await response.json();
        
        if (data.success) {
            showSuccess(data.message);
            loadStories();
        } else {
            showError('Failed to save story: ' + data.error);
        }
    } catch (error) {
        showError('Error saving story: ' + error.message);
    }
}

/**
 * Get story prompts
 */
async function getStoryPrompts() {
    try {
        const response = await fetch(`${API_BASE}/stories/prompts`);
        const data = await response.json();
        
        if (data.success) {
            const promptsList = data.prompts.map((p, i) => `${i + 1}. ${p}`).join('\n\n');
            alert('Story Prompts:\n\n' + promptsList);
        } else {
            showError('Failed to load prompts: ' + data.error);
        }
    } catch (error) {
        showError('Error loading prompts: ' + error.message);
    }
}

/**
 * View story
 */
async function viewStory(storyId) {
    try {
        const response = await fetch(`${API_BASE}/stories/${storyId}`);
        const data = await response.json();
        
        if (data.success) {
            // TODO: Show story in modal
            alert(`Story: ${data.story.title}\n\n${data.story.content || data.story.preview}`);
        } else {
            showError('Failed to load story: ' + data.error);
        }
    } catch (error) {
        showError('Error loading story: ' + error.message);
    }
}

/**
 * Edit story
 */
async function editStory(storyId) {
    try {
        const response = await fetch(`${API_BASE}/stories/${storyId}`);
        const data = await response.json();
        
        if (!data.success) {
            showError('Failed to load story: ' + data.error);
            return;
        }
        
        const story = data.story;
        const title = prompt('Story title:', story.title);
        if (!title) return;
        
        const content = prompt('Story content:', story.content);
        
        const updateResponse = await fetch(`${API_BASE}/stories/${storyId}`, {
            method: 'PUT',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ title, content })
        });
        
        const updateData = await updateResponse.json();
        
        if (updateData.success) {
            showSuccess(updateData.message);
            loadStories();
        } else {
            showError('Failed to update story: ' + updateData.error);
        }
    } catch (error) {
        showError('Error editing story: ' + error.message);
    }
}

// ============================================================================
// UI HELPERS
// ============================================================================

function showSuccess(message) {
    alert('✅ ' + message);
    console.log('Success:', message);
}

function showError(message) {
    alert('❌ ' + message);
    console.error('Error:', message);
}

function showInfo(message) {
    alert('ℹ️ ' + message);
    console.info('Info:', message);
}

function showLoadMoreButton(callback) {
    // TODO: Implement proper load more button
    console.log('More items available');
}

function renderAlbums(albums) {
    // TODO: Implement album rendering
    console.log('Rendering albums:', albums);
}

function renderTimeline(events) {
    // TODO: Implement timeline rendering
    console.log('Rendering timeline:', events);
}

function renderPlaylists(playlists) {
    // TODO: Implement playlist rendering
    console.log('Rendering playlists:', playlists);
}

function renderStories(stories) {
    // TODO: Implement story rendering
    console.log('Rendering stories:', stories);
}

// ============================================================================
// INITIALIZE ON PAGE LOAD
// ============================================================================

document.addEventListener('DOMContentLoaded', function() {
    console.log('🐺 Memory Lane JavaScript initialized');
    
    // Remove the generic alert handler from template
    document.querySelectorAll('.btn').forEach(function(button) {
        const oldHandler = button.onclick;
        button.onclick = null; // Remove old handler
    });
    
    // Attach specific handlers based on button text/class
    attachButtonHandlers();
});

/**
 * Attach event handlers to all Memory Lane buttons
 */
function attachButtonHandlers() {
    // Album buttons
    document.querySelectorAll('button').forEach(button => {
        const text = button.textContent.trim();
        
        // Memory Albums
        if (text.includes('Create New Album')) {
            button.onclick = (e) => { e.preventDefault(); createAlbum(); };
        } else if (text.includes('Slideshow')) {
            button.onclick = (e) => { e.preventDefault(); viewSlideshow(button.dataset.albumId || '1'); };
        } else if (text.includes('Edit') && button.closest('#memory-albums')) {
            button.onclick = (e) => { e.preventDefault(); editAlbum(button.dataset.albumId || '1'); };
        }
        
        // Media Upload
        else if (text.includes('Upload Photos')) {
            button.onclick = (e) => { e.preventDefault(); uploadPhotos(); };
        } else if (text.includes('Upload Video')) {
            button.onclick = (e) => { e.preventDefault(); uploadVideo(); };
        } else if (text.includes('Voice Recording')) {
            button.onclick = (e) => { e.preventDefault(); recordVoice(); };
        } else if (text.includes('Write Memory')) {
            button.onclick = (e) => { e.preventDefault(); writeMemory(); };
        }
        
        // Timeline
        else if (text.includes('Add Event')) {
            button.onclick = (e) => { e.preventDefault(); addTimelineEvent(); };
        } else if (text.includes('View Details')) {
            button.onclick = (e) => { e.preventDefault(); viewTimelineEvent(button.dataset.eventId || '1'); };
        }
        
        // Activities
        else if (text.includes('Start Activity')) {
            const activityType = button.closest('.activity-card')?.querySelector('h5')?.textContent || 'unknown';
            button.onclick = (e) => { e.preventDefault(); startActivity(activityType); };
        }
        
        // Music
        else if (text.includes('Create Playlist')) {
            button.onclick = (e) => { e.preventDefault(); createPlaylist(); };
        } else if (text.includes('Add Memory') && button.closest('#music-memories')) {
            button.onclick = (e) => { e.preventDefault(); addSongMemory(button.dataset.songId || 'unknown'); };
        }
        
        // Stories
        else if (text.includes('Start Recording') && button.closest('#story-capture')) {
            button.onclick = (e) => { e.preventDefault(); startVoiceStory(); };
        } else if (text.includes('Start Writing')) {
            button.onclick = (e) => { e.preventDefault(); startGuidedWriting(); };
        } else if (text.includes('Get Prompts')) {
            button.onclick = (e) => { e.preventDefault(); getStoryPrompts(); };
        } else if (text.includes('Listen') || text.includes('Watch') || text.includes('Read')) {
            button.onclick = (e) => { e.preventDefault(); viewStory(button.dataset.storyId || '1'); };
        } else if (text.includes('Edit') && button.closest('#story-capture')) {
            button.onclick = (e) => { e.preventDefault(); editStory(button.dataset.storyId || '1'); };
        }
        
        // Load More
        else if (text.includes('Load More')) {
            if (button.closest('#timeline')) {
                button.onclick = (e) => { e.preventDefault(); loadTimeline(); };
            } else if (button.closest('#story-capture')) {
                button.onclick = (e) => { e.preventDefault(); loadStories(); };
            }
        }
    });
    
    console.log('✅ All Memory Lane button handlers attached');
}
