from flask import Flask, render_template_string, request, jsonify
import sqlite3
import random
import string

app = Flask(__name__)
app.secret_key = 'debug-secret-key'

# Simple login template for debugging
LOGIN_TEMPLATE = """
<!DOCTYPE html>
<html>
<head>
    <title>Debug SecureChat</title>
    <style>
        body { font-family: Arial; padding: 20px; background: #667eea; }
        .container { max-width: 400px; margin: 0 auto; background: white; padding: 20px; border-radius: 10px; }
        input { width: 100%; padding: 10px; margin: 10px 0; border: 1px solid #ddd; border-radius: 5px; }
        button { width: 100%; padding: 10px; background: #667eea; color: white; border: none; border-radius: 5px; cursor: pointer; }
        .message { padding: 10px; margin: 10px 0; border-radius: 5px; }
        .success { background: #d4edda; color: #155724; }
        .error { background: #f8d7da; color: #721c24; }
        .hidden { display: none; }
    </style>
</head>
<body>
    <div class="container">
        <h2>🔐 SecureChat Debug</h2>
        
        <div id="step1">
            <div id="message1"></div>
            <input type="tel" id="phone" placeholder="Enter phone number" value="2581473692">
            <button onclick="sendOTP()">Send OTP</button>
        </div>
        
        <div id="step2" class="hidden">
            <div id="message2"></div>
            <input type="text" id="otp" placeholder="Enter OTP">
            <button onclick="verifyOTP()">Verify OTP</button>
        </div>
    </div>

    <script>
        let currentPhone = '';
        
        function showMessage(elementId, message, type) {
            document.getElementById(elementId).innerHTML = `<div class="message ${type}">${message}</div>`;
        }
        
        async function sendOTP() {
            const phone = document.getElementById('phone').value.trim();
            console.log('Sending OTP request for:', phone);
            
            if (!phone) {
                showMessage('message1', 'Please enter phone number', 'error');
                return;
            }
            
            try {
                const response = await fetch('/send_otp', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ phone_number: phone })
                });
                
                console.log('Response status:', response.status);
                const data = await response.json();
                console.log('Response data:', data);
                
                if (data.success) {
                    currentPhone = phone;
                    showMessage('message1', `OTP sent! Demo OTP: ${data.otp}`, 'success');
                    document.getElementById('step1').classList.add('hidden');
                    document.getElementById('step2').classList.remove('hidden');
                } else {
                    showMessage('message1', data.message, 'error');
                }
            } catch (error) {
                console.error('Error:', error);
                showMessage('message1', 'Network error: ' + error.message, 'error');
            }
        }
        
        async function verifyOTP() {
            const otp = document.getElementById('otp').value.trim();
            console.log('Verifying OTP:', otp, 'for phone:', currentPhone);
            
            if (!otp) {
                showMessage('message2', 'Please enter OTP', 'error');
                return;
            }
            
            try {
                const response = await fetch('/verify_otp', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ phone_number: currentPhone, otp: otp })
                });
                
                const data = await response.json();
                console.log('Verify response:', data);
                
                if (data.success) {
                    showMessage('message2', 'Login successful!', 'success');
                    setTimeout(() => alert('Login successful! You can now implement the dashboard.'), 1000);
                } else {
                    showMessage('message2', data.message, 'error');
                }
            } catch (error) {
                console.error('Error:', error);
                showMessage('message2', 'Network error: ' + error.message, 'error');
            }
        }
    </script>
</body>
</html>
"""

def init_db():
    conn = sqlite3.connect('debug_app.db')
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            phone_number TEXT UNIQUE NOT NULL,
            otp TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    conn.commit()
    conn.close()
    print("Database initialized")

def generate_otp():
    return ''.join(random.choices(string.digits, k=6))

@app.route('/')
def index():
    return render_template_string(LOGIN_TEMPLATE)

@app.route('/send_otp', methods=['POST'])
def send_otp():
    print("=== SEND OTP REQUEST ===")
    try:
        data = request.get_json()
        print(f"Received data: {data}")
        
        if not data:
            print("No JSON data received")
            return jsonify({'success': False, 'message': 'No data received'}), 400
            
        phone_number = data.get('phone_number')
        print(f"Phone number: {phone_number}")
        
        if not phone_number:
            print("Phone number missing")
            return jsonify({'success': False, 'message': 'Phone number required'}), 400
        
        otp = generate_otp()
        print(f"Generated OTP: {otp}")
        
        # Store in database
        conn = sqlite3.connect('debug_app.db')
        cursor = conn.cursor()
        cursor.execute('''
            INSERT OR REPLACE INTO users (phone_number, otp)
            VALUES (?, ?)
        ''', (phone_number, otp))
        conn.commit()
        conn.close()
        print("OTP stored in database")
        
        response_data = {
            'success': True, 
            'message': f'OTP sent to {phone_number}',
            'otp': otp
        }
        print(f"Sending response: {response_data}")
        return jsonify(response_data), 200
        
    except Exception as e:
        print(f"ERROR in send_otp: {str(e)}")
        import traceback
        traceback.print_exc()
        return jsonify({'success': False, 'message': f'Server error: {str(e)}'}), 500

@app.route('/verify_otp', methods=['POST'])
def verify_otp():
    print("=== VERIFY OTP REQUEST ===")
    try:
        data = request.get_json()
        print(f"Received data: {data}")
        
        phone_number = data.get('phone_number')
        otp = data.get('otp')
        print(f"Phone: {phone_number}, OTP: {otp}")
        
        # Check database
        conn = sqlite3.connect('debug_app.db')
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM users WHERE phone_number = ?', (phone_number,))
        user = cursor.fetchone()
        conn.close()
        
        print(f"User from DB: {user}")
        
        if user and user[2] == otp:  # user[2] is otp column
            print("OTP verified successfully")
            return jsonify({'success': True, 'message': 'Login successful'}), 200
        else:
            print("OTP verification failed")
            return jsonify({'success': False, 'message': 'Invalid OTP'}), 400
            
    except Exception as e:
        print(f"ERROR in verify_otp: {str(e)}")
        import traceback
        traceback.print_exc()
        return jsonify({'success': False, 'message': f'Server error: {str(e)}'}), 500

if __name__ == '__main__':
    init_db()
    print("Starting debug Flask app...")
    print("Open http://localhost:5000 in your browser")
    app.run(debug=True, port=5000)