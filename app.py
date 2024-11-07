from flask import Flask, request, jsonify, render_template
import qrcode
import base64
from io import BytesIO
from cryptography.fernet import Fernet
import socket

app = Flask(__name__)

key = Fernet.generate_key()
cipher_suite = Fernet(key)

messages = {}

host_name = socket.gethostbyname(socket.gethostname())

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/generate', methods=['POST'])
def generate_qr():
    data = request.json.get('message')
    if not data:
        return jsonify({"error": "No message provided"}), 400

    encrypted_message = cipher_suite.encrypt(data.encode())
    
    message_id = len(messages) + 1  
    messages[message_id] = encrypted_message

    link = f"http://{host_name}:5000/decrypt/{message_id}"  
    qr = qrcode.QRCode(version=1, box_size=10, border=5)
    qr.add_data(link)
    qr.make(fit=True)

    img = qr.make_image(fill='black', back_color='white')
    buffer = BytesIO()
    img.save(buffer, format="PNG")
    buffer.seek(0)
    img_str = base64.b64encode(buffer.getvalue()).decode()
    return jsonify({"qr_code": img_str})

@app.route('/decrypt/<int:message_id>', methods=['GET'])
def decrypt(message_id):
    encrypted_message = messages.get(message_id)
    if not encrypted_message:
        return "Message not found!", 404

    decrypted_message = cipher_suite.decrypt(encrypted_message).decode()
    
    return render_template('decrypted_message.html', message=decrypted_message)

if __name__ == '__main__':
    app.run(host='0.0.0.0',port=5000,debug=True)
