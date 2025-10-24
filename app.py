from flask import Flask, render_template, request, jsonify, session, redirect, url_for, send_from_directory
import sqlite3
import random
import string
import hashlib
import os
from datetime import datetime
import base64
from PIL import Image, ImageDraw, ImageFont
from PIL.PngImagePlugin import PngInfo
import io
import json

app = Flask(__name__)
app.secret_key = 'your-secret-key-change-this'

# Database setup
def init_db():
    conn = sqlite3.connect('messaging_app.db')
    cursor = conn.cursor()
    
    # Users table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            phone_number TEXT UNIQUE NOT NULL,
            otp TEXT,
            is_verified BOOLEAN DEFAULT FALSE,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    # Contacts table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS contacts (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER,
            contact_phone TEXT,
            contact_name TEXT,
            status TEXT DEFAULT 'pending',
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (user_id) REFERENCES users (id)
        )
    ''')
    
    # Messages table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS messages (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            sender_id INTEGER,
            receiver_phone TEXT,
            message_text TEXT,
            encrypted_image BLOB,
            decrypt_code TEXT,
            is_encrypted BOOLEAN DEFAULT FALSE,
            timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            auto_delete_time TIMESTAMP DEFAULT NULL,
            FOREIGN KEY (sender_id) REFERENCES users (id)
        )
    ''')
    
    # Check if auto_delete_time column exists, if not add it
    cursor.execute("PRAGMA table_info(messages)")
    columns = [column[1] for column in cursor.fetchall()]
    
    if 'auto_delete_time' not in columns:
        print("Adding auto_delete_time column to messages table...")
        cursor.execute('ALTER TABLE messages ADD COLUMN auto_delete_time TIMESTAMP DEFAULT NULL')
        print("Column added successfully!")
    
    conn.commit()
    conn.close()

# Utility functions
def generate_otp():
    return ''.join(random.choices(string.digits, k=6))

def generate_decrypt_code():
    return ''.join(random.choices(string.ascii_letters + string.digits, k=8))

def get_user_by_phone(phone_number):
    conn = sqlite3.connect('messaging_app.db')
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM users WHERE phone_number = ?', (phone_number,))
    user = cursor.fetchone()
    conn.close()
    return user

def create_or_update_user(phone_number, otp):
    conn = sqlite3.connect('messaging_app.db')
    cursor = conn.cursor()
    cursor.execute('''
        INSERT OR REPLACE INTO users (phone_number, otp, is_verified)
        VALUES (?, ?, FALSE)
    ''', (phone_number, otp))
    conn.commit()
    conn.close()

def verify_user(phone_number):
    conn = sqlite3.connect('messaging_app.db')
    cursor = conn.cursor()
    cursor.execute('UPDATE users SET is_verified = TRUE WHERE phone_number = ?', (phone_number,))
    conn.commit()
    conn.close()

def get_all_available_stickers():
    """Get all available sticker files from static/images folder"""
    stickers_dir = os.path.join('static', 'images')
    available_stickers = []
    
    try:
        # Get all image files from the static/images folder
        if os.path.exists(stickers_dir):
            for file in os.listdir(stickers_dir):
                if file.lower().endswith(('.png', '.jpg', '.jpeg', '.gif', '.bmp')):
                    sticker_path = os.path.join(stickers_dir, file)
                    available_stickers.append(sticker_path)
                    
        print(f"Found {len(available_stickers)} stickers in folder: {[os.path.basename(s) for s in available_stickers]}")
        
    except Exception as e:
        print(f"Error reading stickers folder: {e}")
    
    return available_stickers

def get_random_sticker():
    """Get a random sticker from available stickers in static/images folder"""
    available_stickers = get_all_available_stickers()
    
    if available_stickers:
        selected_sticker = random.choice(available_stickers)
        print(f"Selected random sticker: {os.path.basename(selected_sticker)}")
        return selected_sticker
    else:
        print("No stickers found in static/images folder!")
        # Create a fallback sticker if no stickers found
        create_fallback_sticker()
        return os.path.join('static', 'images', 'fallback_sticker.png')

def create_fallback_sticker():
    """Create a simple fallback sticker if no stickers are found"""
    stickers_dir = os.path.join('static', 'images')
    os.makedirs(stickers_dir, exist_ok=True)
    sticker_path = os.path.join(stickers_dir, 'fallback_sticker.png')
    
    # Create a simple colorful sticker
    img = Image.new('RGB', (400, 300), (255, 255, 255))
    draw = ImageDraw.Draw(img)
    
    # Draw a colorful background pattern
    colors = [(255, 182, 193), (173, 216, 230), (144, 238, 144), (255, 218, 185), (221, 160, 221)]
    for i in range(5):
        color = colors[i]
        draw.rectangle([i*80, 0, (i+1)*80, 300], fill=color)
    
    # Add some decorative elements
    draw.ellipse([50, 50, 150, 150], fill=(255, 255, 0))
    draw.ellipse([250, 150, 350, 250], fill=(255, 0, 255))
    draw.rectangle([150, 200, 250, 250], fill=(0, 255, 255))
    
    # Add text
    try:
        font = ImageFont.truetype("arial.ttf", 20)
    except:
        font = ImageFont.load_default()
    
    draw.text((160, 120), "FALLBACK", fill=(0, 0, 0), font=font)
    
    img.save(sticker_path)
    print(f"Created fallback sticker at {sticker_path}")

def text_to_image_steganography(text, decrypt_code, image_path=None):
    """Convert text to steganography image using a random sticker as base"""
    try:
        # Get a random sticker as base image
        sticker_path = get_random_sticker()
        
        base_img = Image.open(sticker_path).copy()
        print(f"Using random sticker base image: {sticker_path}")
        
        # Resize if too large
        if base_img.size[0] > 400 or base_img.size[1] > 300:
            base_img = base_img.resize((400, 300), Image.Resampling.LANCZOS)
        
        # Add some random decorative elements to make it look more natural
        draw = ImageDraw.Draw(base_img)
        
        # Add subtle random elements for camouflage
        for _ in range(random.randint(1, 3)):
            shape_type = random.choice(['circle', 'rectangle'])
            color = tuple(random.randint(200, 255) for _ in range(3))  # Light colors
            alpha = random.randint(30, 80)  # Low opacity
            
            if shape_type == 'circle':
                x, y = random.randint(0, 350), random.randint(0, 250)
                r = random.randint(5, 15)
                # Create a semi-transparent overlay
                overlay = Image.new('RGBA', base_img.size, (0, 0, 0, 0))
                overlay_draw = ImageDraw.Draw(overlay)
                overlay_draw.ellipse([x, y, x+r, y+r], fill=(*color, alpha))
                base_img = Image.alpha_composite(base_img.convert('RGBA'), overlay).convert('RGB')
        
        # Hide the actual message and decrypt code in image metadata
        message_data = {
            'message': text,
            'decrypt_code': decrypt_code,
            'timestamp': datetime.now().isoformat()
        }
        
        # Convert to base64 and hide in image
        encoded_data = base64.b64encode(json.dumps(message_data).encode()).decode()
        
        # Create PngInfo object for metadata
        pnginfo = PngInfo()
        pnginfo.add_text("hidden_message", encoded_data)
        pnginfo.add_text("sticker_type", "encrypted_sticker")
        
        # Save to bytes with proper PNG info
        img_buffer = io.BytesIO()
        base_img.save(img_buffer, format='PNG', pnginfo=pnginfo)
        img_buffer.seek(0)
        
        return img_buffer.getvalue()
        
    except Exception as e:
        print(f"Error in text_to_image_steganography: {e}")
        # Fallback: create simple image
        base_img = Image.new('RGB', (400, 300), (255, 182, 193))
        draw = ImageDraw.Draw(base_img)
        
        try:
            font = ImageFont.truetype("arial.ttf", 16)
        except:
            font = ImageFont.load_default()
            
        draw.text((50, 150), "Encrypted Sticker Message", fill=(0, 0, 0), font=font)
        
        img_buffer = io.BytesIO()
        base_img.save(img_buffer, format='PNG')
        img_buffer.seek(0)
        
        return img_buffer.getvalue()

def extract_from_steganography(image_data, provided_code):
    """Extract hidden message from steganography image"""
    try:
        img_buffer = io.BytesIO(image_data)
        img = Image.open(img_buffer)
        
        # Try to get the hidden message from text metadata
        if hasattr(img, 'text') and 'hidden_message' in img.text:
            encoded_data = img.text['hidden_message']
            decoded_data = base64.b64decode(encoded_data).decode()
            message_data = json.loads(decoded_data)
            
            # Verify decrypt code
            if message_data['decrypt_code'] == provided_code:
                return message_data['message']
            else:
                return None
                
        # Fallback: check info attribute (older method)
        elif hasattr(img, 'info') and 'hidden_message' in img.info:
            encoded_data = img.info['hidden_message']
            decoded_data = base64.b64decode(encoded_data).decode()
            message_data = json.loads(decoded_data)
            
            # Verify decrypt code
            if message_data['decrypt_code'] == provided_code:
                return message_data['message']
            else:
                return None
                
        return None
        
    except Exception as e:
        print(f"Decryption error: {e}")
        return None

def cleanup_expired_messages():
    """Delete messages that have expired auto-delete time"""
    try:
        conn = sqlite3.connect('messaging_app.db')
        cursor = conn.cursor()
        
        # Check if column exists before trying to use it
        cursor.execute("PRAGMA table_info(messages)")
        columns = [column[1] for column in cursor.fetchall()]
        
        if 'auto_delete_time' in columns:
            current_time = datetime.now().isoformat()
            cursor.execute('''
                DELETE FROM messages 
                WHERE auto_delete_time IS NOT NULL 
                AND auto_delete_time <= ?
            ''', (current_time,))
            deleted_count = cursor.rowcount
            conn.commit()
            if deleted_count > 0:
                print(f"Cleaned up {deleted_count} expired messages")
        else:
            print("auto_delete_time column not found, skipping cleanup")
            
        conn.close()
    except Exception as e:
        print(f"Error in cleanup_expired_messages: {e}")

# Routes
@app.route('/')
def index():
    if 'user_phone' in session:
        return redirect(url_for('dashboard'))
    return render_template('login.html')

@app.route('/send_otp', methods=['POST'])
def send_otp():
    try:
        data = request.get_json()
        if not data:
            return jsonify({'success': False, 'message': 'Invalid request format'})
            
        phone_number = data.get('phone_number')
        if not phone_number:
            return jsonify({'success': False, 'message': 'Phone number required'})
        
        otp = generate_otp()
        create_or_update_user(phone_number, otp)
        
        # In real app, send OTP via SMS API
        # For demo, we'll return the OTP (remove in production)
        return jsonify({
            'success': True, 
            'message': f'OTP sent to {phone_number}',
            'otp': otp  # Remove this in production
        })
        
    except Exception as e:
        print(f"Error in send_otp: {e}")
        return jsonify({'success': False, 'message': 'Server error occurred'})

@app.route('/verify_otp', methods=['POST'])
def verify_otp():
    try:
        data = request.get_json()
        if not data:
            return jsonify({'success': False, 'message': 'Invalid request format'})
            
        phone_number = data.get('phone_number')
        otp = data.get('otp')
        
        if not phone_number or not otp:
            return jsonify({'success': False, 'message': 'Phone number and OTP required'})
        
        user = get_user_by_phone(phone_number)
        if user and user[2] == otp:  # user[2] is otp column
            verify_user(phone_number)
            session['user_phone'] = phone_number
            session['user_id'] = user[0]
            return jsonify({'success': True, 'message': 'Login successful'})
        
        return jsonify({'success': False, 'message': 'Invalid OTP'})
        
    except Exception as e:
        print(f"Error in verify_otp: {e}")
        return jsonify({'success': False, 'message': 'Server error occurred'})

@app.route('/dashboard')
def dashboard():
    if 'user_phone' not in session:
        return redirect(url_for('index'))
    return render_template('dashboard.html')

@app.route('/add_contact', methods=['POST'])
def add_contact():
    try:
        if 'user_id' not in session:
            return jsonify({'success': False, 'message': 'Not logged in'})
        
        data = request.get_json()
        if not data:
            return jsonify({'success': False, 'message': 'Invalid request format'})
            
        contact_phone = data.get('contact_phone')
        contact_name = data.get('contact_name', contact_phone)
        
        if not contact_phone:
            return jsonify({'success': False, 'message': 'Contact phone required'})
        
        conn = sqlite3.connect('messaging_app.db')
        cursor = conn.cursor()
        cursor.execute('''
            INSERT INTO contacts (user_id, contact_phone, contact_name)
            VALUES (?, ?, ?)
        ''', (session['user_id'], contact_phone, contact_name))
        conn.commit()
        conn.close()
        
        return jsonify({'success': True, 'message': 'Contact added successfully'})
        
    except Exception as e:
        print(f"Error in add_contact: {e}")
        return jsonify({'success': False, 'message': 'Server error occurred'})

@app.route('/get_contacts')
def get_contacts():
    try:
        if 'user_id' not in session:
            return jsonify([])
        
        conn = sqlite3.connect('messaging_app.db')
        cursor = conn.cursor()
        cursor.execute('''
            SELECT contact_phone, contact_name FROM contacts 
            WHERE user_id = ?
        ''', (session['user_id'],))
        contacts = cursor.fetchall()
        conn.close()
        
        return jsonify([{'phone': c[0], 'name': c[1]} for c in contacts])
        
    except Exception as e:
        print(f"Error in get_contacts: {e}")
        return jsonify([])

@app.route('/send_message', methods=['POST'])
def send_message():
    try:
        if 'user_id' not in session:
            return jsonify({'success': False, 'message': 'Not logged in'})
        
        data = request.get_json()
        if not data:
            return jsonify({'success': False, 'message': 'Invalid request format'})
            
        receiver_phone = data.get('receiver_phone')
        message_text = data.get('message_text')
        is_encrypted = data.get('is_encrypted', False)
        
        if not receiver_phone or not message_text:
            return jsonify({'success': False, 'message': 'Receiver phone and message text required'})
        
        encrypted_image = None
        decrypt_code = None
        
        if is_encrypted:
            decrypt_code = generate_decrypt_code()
            # Create steganography image using a random sticker as base
            encrypted_image = text_to_image_steganography(message_text, decrypt_code)
            message_text = "🎨 [Encrypted Sticker Message]"
        
        conn = sqlite3.connect('messaging_app.db')
        cursor = conn.cursor()
        cursor.execute('''
            INSERT INTO messages (sender_id, receiver_phone, message_text, encrypted_image, decrypt_code, is_encrypted)
            VALUES (?, ?, ?, ?, ?, ?)
        ''', (session['user_id'], receiver_phone, message_text, encrypted_image, decrypt_code, is_encrypted))
        conn.commit()
        conn.close()
        
        response = {'success': True, 'message': 'Message sent successfully'}
        if is_encrypted:
            response['decrypt_code'] = decrypt_code
            response['message'] = 'Encrypted sticker message sent! Share the decrypt code with recipient.'
        
        return jsonify(response)
        
    except Exception as e:
        print(f"Error in send_message: {e}")
        return jsonify({'success': False, 'message': 'Server error occurred'})

@app.route('/get_messages')
def get_messages():
    try:
        if 'user_phone' not in session:
            return jsonify([])
        
        # Clean up expired messages first
        cleanup_expired_messages()
        
        conn = sqlite3.connect('messaging_app.db')
        cursor = conn.cursor()
        
        # Check if auto_delete_time column exists
        cursor.execute("PRAGMA table_info(messages)")
        columns = [column[1] for column in cursor.fetchall()]
        
        if 'auto_delete_time' in columns:
            # Get messages where user is sender or receiver (with auto_delete_time)
            cursor.execute('''
                SELECT m.id, u.phone_number as sender_phone, m.receiver_phone, 
                       m.message_text, m.is_encrypted, m.timestamp, m.decrypt_code, m.auto_delete_time
                FROM messages m
                JOIN users u ON m.sender_id = u.id
                WHERE m.receiver_phone = ? OR u.phone_number = ?
                ORDER BY m.timestamp DESC
            ''', (session['user_phone'], session['user_phone']))
        else:
            # Get messages where user is sender or receiver (without auto_delete_time)
            cursor.execute('''
                SELECT m.id, u.phone_number as sender_phone, m.receiver_phone, 
                       m.message_text, m.is_encrypted, m.timestamp, m.decrypt_code, NULL
                FROM messages m
                JOIN users u ON m.sender_id = u.id
                WHERE m.receiver_phone = ? OR u.phone_number = ?
                ORDER BY m.timestamp DESC
            ''', (session['user_phone'], session['user_phone']))
        
        messages = cursor.fetchall()
        conn.close()
        
        return jsonify([{
            'id': m[0],
            'sender': m[1],
            'receiver': m[2],
            'message': m[3],
            'is_encrypted': m[4],
            'timestamp': m[5],
            'decrypt_code': m[6] if m[1] == session['user_phone'] else None,  # Only show decrypt code to sender
            'auto_delete_time': m[7] if len(m) > 7 else None
        } for m in messages])
        
    except Exception as e:
        print(f"Error in get_messages: {e}")
        return jsonify([])

@app.route('/get_encrypted_image/<int:message_id>')
def get_encrypted_image(message_id):
    try:
        if 'user_id' not in session:
            return "Unauthorized", 401
        
        conn = sqlite3.connect('messaging_app.db')
        cursor = conn.cursor()
        cursor.execute('SELECT encrypted_image FROM messages WHERE id = ?', (message_id,))
        result = cursor.fetchone()
        conn.close()
        
        if result and result[0]:
            return result[0], 200, {'Content-Type': 'image/png'}
        
        return "Image not found", 404
        
    except Exception as e:
        print(f"Error in get_encrypted_image: {e}")
        return "Server error", 500

@app.route('/decrypt_message', methods=['POST'])
def decrypt_message():
    try:
        if 'user_id' not in session:
            return jsonify({'success': False, 'message': 'Not logged in'})
        
        data = request.get_json()
        if not data:
            return jsonify({'success': False, 'message': 'Invalid request format'})
            
        message_id = data.get('message_id')
        decrypt_code = data.get('decrypt_code')
        
        if not message_id or not decrypt_code:
            return jsonify({'success': False, 'message': 'Message ID and decrypt code required'})
        
        conn = sqlite3.connect('messaging_app.db')
        cursor = conn.cursor()
        cursor.execute('SELECT encrypted_image FROM messages WHERE id = ?', (message_id,))
        result = cursor.fetchone()
        conn.close()
        
        if result and result[0]:
            decrypted_message = extract_from_steganography(result[0], decrypt_code)
            if decrypted_message:
                return jsonify({
                    'success': True, 
                    'message': decrypted_message,
                    'show_auto_delete': True  # Show auto-delete option after successful decrypt
                })
            else:
                return jsonify({'success': False, 'message': 'Invalid decrypt code'})
        
        return jsonify({'success': False, 'message': 'Message not found'})
        
    except Exception as e:
        print(f"Error in decrypt_message: {e}")
        return jsonify({'success': False, 'message': 'Server error occurred'})

@app.route('/set_auto_delete', methods=['POST'])
def set_auto_delete():
    """Set auto-delete timer for a message (15 seconds from now)"""
    try:
        if 'user_id' not in session:
            return jsonify({'success': False, 'message': 'Not logged in'})
        
        data = request.get_json()
        if not data:
            return jsonify({'success': False, 'message': 'Invalid request format'})
            
        message_id = data.get('message_id')
        
        if not message_id:
            return jsonify({'success': False, 'message': 'Message ID required'})
        
        conn = sqlite3.connect('messaging_app.db')
        cursor = conn.cursor()
        
        # Check if auto_delete_time column exists
        cursor.execute("PRAGMA table_info(messages)")
        columns = [column[1] for column in cursor.fetchall()]
        
        if 'auto_delete_time' not in columns:
            conn.close()
            return jsonify({'success': False, 'message': 'Auto-delete feature not available'})
        
        # Set auto-delete time to 15 seconds from now
        from datetime import timedelta
        delete_time = (datetime.now() + timedelta(seconds=15)).isoformat()
        
        cursor.execute('''
            UPDATE messages 
            SET auto_delete_time = ? 
            WHERE id = ?
        ''', (delete_time, message_id))
        conn.commit()
        conn.close()
        
        return jsonify({
            'success': True, 
            'message': 'Message will be auto-deleted in 15 seconds',
            'delete_time': delete_time
        })
        
    except Exception as e:
        print(f"Error in set_auto_delete: {e}")
        return jsonify({'success': False, 'message': 'Server error occurred'})

@app.route('/copy_decrypt_code/<decrypt_code>')
def copy_decrypt_code(decrypt_code):
    """Endpoint to help with copying decrypt code"""
    return jsonify({
        'success': True, 
        'decrypt_code': decrypt_code,
        'message': 'Decrypt code ready to copy'
    })

@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('index'))

if __name__ == '__main__':
    # Create directories
    os.makedirs('static/images', exist_ok=True)
    os.makedirs('templates', exist_ok=True)
    
    # Check available stickers
    available_stickers = get_all_available_stickers()
    print(f"Found {len(available_stickers)} stickers ready for random selection")
    
    # Initialize database (this will add the missing column)
    init_db()
    
    print("Starting Flask app...")
    print("Open http://localhost:5000 in your browser")
    print("App will randomly select from your stickers in static/images/ folder")
    app.run(host='0.0.0.0',debug=True, port=5000)