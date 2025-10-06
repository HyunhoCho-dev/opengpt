from flask import Flask, render_template, request, jsonify, Response, stream_with_context, redirect, url_for, session
import requests
import json
import os
from urllib.parse import urlencode

app = Flask(__name__)
app.secret_key = os.urandom(24)

# HuggingFace OAuth 설정
HF_CLIENT_ID = os.getenv('HF_CLIENT_ID', 'YOUR_CLIENT_ID_HERE')
HF_CLIENT_SECRET = os.getenv('HF_CLIENT_SECRET', 'YOUR_CLIENT_SECRET_HERE')
HF_REDIRECT_URI = os.getenv('HF_REDIRECT_URI', 'http://127.0.0.1:5000/callback')
HF_AUTHORIZE_URL = "https://huggingface.co/oauth/authorize"
HF_TOKEN_URL = "https://huggingface.co/oauth/token"
HF_USER_URL = "https://huggingface.co/api/whoami-v2"
HF_SUBSCRIPTION_URL = "https://huggingface.co/api/subscription"

API_URL = "https://router.huggingface.co/v1/chat/completions"

# 사용 가능한 모델 목록
AVAILABLE_MODELS = {
    'gpt-oss-120b': {
        'name': 'GPT-OSS 120B',
        'id': 'openai/gpt-oss-120b:nscale',
        'input_price': 0.1,
        'output_price': 0.4
    },
    'gpt-oss-20b': {
        'name': 'GPT-OSS 20B',
        'id': 'openai/gpt-oss-20b:nscale',
        'input_price': 0.05,
        'output_price': 0.2
    }
}

@app.route('/')
def index():
    if 'access_token' not in session:
        return redirect(url_for('login_page'))
    return render_template('index.html', user=session.get('user'), models=AVAILABLE_MODELS)

@app.route('/login-page')
def login_page():
    return render_template('login.html')

@app.route('/login')
def login():
    params = {
        'client_id': HF_CLIENT_ID,
        'redirect_uri': HF_REDIRECT_URI,
        'response_type': 'code',
        'scope': 'openid profile inference-api',
        'state': 'random_state_string'
    }
    auth_url = f"{HF_AUTHORIZE_URL}?{urlencode(params)}"
    return redirect(auth_url)

@app.route('/callback')
def callback():
    code = request.args.get('code')
    
    if not code:
        return "Error: No authorization code received", 400
    
    token_data = {
        'client_id': HF_CLIENT_ID,
        'client_secret': HF_CLIENT_SECRET,
        'code': code,
        'redirect_uri': HF_REDIRECT_URI,
        'grant_type': 'authorization_code'
    }
    
    try:
        token_response = requests.post(HF_TOKEN_URL, data=token_data)
        token_response.raise_for_status()
        token_json = token_response.json()
        
        access_token = token_json.get('access_token')
        
        if not access_token:
            return "Error: Failed to get access token", 400
        
        user_headers = {'Authorization': f'Bearer {access_token}'}
        user_response = requests.get(HF_USER_URL, headers=user_headers)
        user_response.raise_for_status()
        user_info = user_response.json()
        
        session['access_token'] = access_token
        session['user'] = {
            'name': user_info.get('fullname', user_info.get('name', 'User')),
            'username': user_info.get('name', 'user'),
            'avatar': user_info.get('avatarUrl', '')
        }
        
        return redirect(url_for('index'))
        
    except Exception as e:
        return f"Error during authentication: {str(e)}", 500

@app.route('/check-auth')
def check_auth():
    if 'access_token' in session:
        return jsonify({
            'authenticated': True,
            'user': session.get('user')
        })
    return jsonify({'authenticated': False})

@app.route('/get-subscription-info')
def get_subscription_info():
    access_token = session.get('access_token')
    
    if not access_token:
        return jsonify({'error': 'Not authenticated'}), 401
    
    try:
        headers = {'Authorization': f'Bearer {access_token}'}
        sub_response = requests.get(HF_SUBSCRIPTION_URL, headers=headers)
        
        if sub_response.status_code == 200:
            sub_data = sub_response.json()
            plan = sub_data.get('plan', 'free')
            
            if plan.lower() in ['pro', 'enterprise']:
                return jsonify({'plan': 'Pro', 'cost': '2$/day'})
            else:
                return jsonify({'plan': 'Free', 'cost': '0.1$/day'})
        else:
            return jsonify({'plan': 'Free', 'cost': '0.1$/day'})
    except Exception as e:
        return jsonify({'plan': 'Free', 'cost': '0.1$/day'})

@app.route('/chat', methods=['POST'])
def chat():
    access_token = session.get('access_token')
    
    if not access_token:
        return jsonify({'error': 'Not authenticated'}), 401
    
    data = request.json
    message = data.get('message')
    conversation_history = data.get('history', [])
    selected_model = data.get('model', 'gpt-oss-120b')
    
    model_info = AVAILABLE_MODELS.get(selected_model, {})
    model_id = model_info.get('id', 'openai/gpt-oss-120b:nscale')
    
    headers = {
        "Authorization": f"Bearer {access_token}",
        "Content-Type": "application/json"
    }
    
    messages = []
    for msg in conversation_history:
        messages.append({
            "role": msg["role"],
            "content": msg["content"]
        })
    
    messages.append({
        "role": "user",
        "content": message
    })
    
    payload = {
        "messages": messages,
        "model": model_id,
        "stream": True,
        "max_tokens": 4096,
        "temperature": 0.7
    }
    
    def generate():
        try:
            response = requests.post(API_URL, headers=headers, json=payload, stream=True, timeout=60)
            
            if response.status_code != 200:
                error_msg = f"API Error {response.status_code}: {response.text}"
                yield f"data: {json.dumps({'error': error_msg})}\n\n"
                return
            
            for line in response.iter_lines():
                if not line:
                    continue
                if line.startswith(b"data:"):
                    line_data = line.decode("utf-8").lstrip("data:").strip()
                    if line_data == "[DONE]":
                        break
                    try:
                        chunk = json.loads(line_data)
                        if "choices" in chunk and len(chunk["choices"]) > 0:
                            delta = chunk["choices"][0].get("delta", {})
                            content = delta.get("content", "")
                            if content:
                                yield f"data: {json.dumps({'content': content})}\n\n"
                    except json.JSONDecodeError:
                        continue
        except requests.exceptions.Timeout:
            yield f"data: {json.dumps({'error': 'Request timeout. Please try again.'})}\n\n"
        except requests.exceptions.RequestException as e:
            yield f"data: {json.dumps({'error': f'Request failed: {str(e)}'})}\n\n"
        except Exception as e:
            yield f"data: {json.dumps({'error': str(e)})}\n\n"
    
    return Response(stream_with_context(generate()), mimetype='text/event-stream')

if __name__ == '__main__':
    port = int(os.getenv('PORT', 5000))
    app.run(debug=False, host='0.0.0.0', port=port)
