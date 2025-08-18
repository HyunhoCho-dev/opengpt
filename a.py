import json
import requests
from flask import Flask, request, Response, session
import uuid

app = Flask(__name__)
app.secret_key = 'your-secret-key-here'  # 실제 운영시 변경 필요

API_URL = "https://router.huggingface.co/v1/chat/completions"
API_KEY = "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"

headers = {
    "Authorization": f"Bearer {API_KEY}",
}

# 각 세션별 대화 기록 저장
conversations = {}

def stream_query(payload):
    response = requests.post(API_URL, headers=headers, json=payload, stream=True)
    for line in response.iter_lines():
        if not line or not line.startswith(b"data:"):
            continue
        if line.strip() == b"data: [DONE]":
            return
        try:
            yield json.loads(line.decode("utf-8").lstrip("data:").rstrip("\n"))
        except:
            continue

@app.route("/")
def index():
    return """
<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>OpenGPT - CTTechnology</title>
  <style>
    * {
      margin: 0;
      padding: 0;
      box-sizing: border-box;
    }
    
    /* 스크롤바 제거 */
    ::-webkit-scrollbar {
      display: none;
    }
    
    * {
      -ms-overflow-style: none;
      scrollbar-width: none;
    }
    
    body {
      font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
      background: #ffffff;
      min-height: 100vh;
      display: flex;
      align-items: center;
      justify-content: center;
      color: #202123;
      overflow-x: hidden;
    }
    
    .main-container {
      text-align: center;
      max-width: 700px;
      padding: 60px 40px;
      width: 100%;
    }
    
    .logo {
      font-size: 4.5rem;
      font-weight: 700;
      margin-bottom: 1rem;
      color: #202123;
      letter-spacing: -0.02em;
    }
    
    .subtitle {
      font-size: 1.5rem;
      margin-bottom: 0.5rem;
      color: #666;
      font-weight: 400;
    }
    
    .company {
      font-size: 1rem;
      margin-bottom: 2rem;
      color: #999;
      font-weight: 300;
    }
    
    .language-selector {
      margin-bottom: 2rem;
    }
    
    .language-buttons {
      display: flex;
      gap: 10px;
      justify-content: center;
      flex-wrap: wrap;
    }
    
    .lang-btn {
      background: #f7f7f8;
      border: 1px solid #e5e5e5;
      border-radius: 6px;
      padding: 8px 16px;
      cursor: pointer;
      transition: all 0.2s;
      font-size: 14px;
      color: #666;
    }
    
    .lang-btn.active {
      background: #202123;
      color: white;
      border-color: #202123;
    }
    
    .lang-btn:hover {
      border-color: #ccc;
    }
    
    .description {
      font-size: 1.2rem;
      line-height: 1.6;
      margin-bottom: 3rem;
      color: #555;
      max-width: 600px;
      margin-left: auto;
      margin-right: auto;
    }
    
    .start-button {
      background: #202123;
      border: none;
      color: white;
      padding: 16px 32px;
      font-size: 1.1rem;
      border-radius: 8px;
      cursor: pointer;
      transition: all 0.2s ease;
      font-weight: 600;
      font-family: inherit;
    }
    
    .start-button:hover {
      background: #333;
      transform: translateY(-1px);
    }
    
    .features {
      display: grid;
      grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
      gap: 30px;
      margin-top: 4rem;
      padding: 0 20px;
    }
    
    .feature-card {
      padding: 24px;
      border-radius: 12px;
      border: 1px solid #e5e5e5;
      background: #fafafa;
      transition: all 0.2s ease;
    }
    
    .feature-card:hover {
      border-color: #d0d0d0;
      transform: translateY(-2px);
    }
    
    .feature-icon {
      font-size: 2rem;
      margin-bottom: 12px;
    }
    
    .feature-title {
      font-size: 1.1rem;
      font-weight: 600;
      margin-bottom: 8px;
      color: #202123;
    }
    
    .feature-desc {
      font-size: 0.95rem;
      color: #666;
      line-height: 1.4;
    }
    
    @media (max-width: 768px) {
      .main-container {
        padding: 40px 20px;
      }
      
      .logo {
        font-size: 3rem;
      }
      
      .subtitle {
        font-size: 1.2rem;
      }
      
      .features {
        grid-template-columns: 1fr;
        gap: 20px;
      }
      
      .language-buttons {
        gap: 8px;
      }
      
      .lang-btn {
        padding: 6px 12px;
        font-size: 13px;
      }
    }
  </style>
</head>
<body>
  <div class="main-container">
    <div class="logo">OpenGPT</div>
    <div class="subtitle">AI Assistant</div>
    <div class="company">Powered by CTTechnology</div>
    
    <div class="language-selector">
      <div class="language-buttons">
        <button class="lang-btn active" data-lang="en" onclick="selectLanguage('en')">🇺🇸 English</button>
        <button class="lang-btn" data-lang="ko" onclick="selectLanguage('ko')">🇰🇷 한국어</button>
        <button class="lang-btn" data-lang="ja" onclick="selectLanguage('ja')">🇯🇵 日本語</button>
        <button class="lang-btn" data-lang="zh" onclick="selectLanguage('zh')">🇨🇳 中文</button>
        <button class="lang-btn" data-lang="es" onclick="selectLanguage('es')">🇪🇸 Español</button>
        <button class="lang-btn" data-lang="fr" onclick="selectLanguage('fr')">🇫🇷 Français</button>
      </div>
    </div>
    
    <div class="description" id="description">
      Ask me anything. I'll provide creative and helpful answers.<br>
      From coding and writing to analysis and brainstorming - I'm here to help.
    </div>
    
    <button class="start-button" onclick="startChat()" id="startBtn">
      Start Chatting
    </button>
    
    <div class="features">
      <div class="feature-card">
        <div class="feature-icon">💬</div>
        <div class="feature-title" id="feature1Title">Natural Conversations</div>
        <div class="feature-desc" id="feature1Desc">Real-time streaming for smooth, natural dialogue</div>
      </div>
      
      <div class="feature-card">
        <div class="feature-icon">🧠</div>
        <div class="feature-title" id="feature2Title">Memory</div>
        <div class="feature-desc" id="feature2Desc">Remembers previous conversations for context</div>
      </div>
      
      <div class="feature-card">
        <div class="feature-icon">⚡</div>
        <div class="feature-title" id="feature3Title">Fast Responses</div>
        <div class="feature-desc" id="feature3Desc">Powered by latest AI models for quick answers</div>
      </div>
    </div>
  </div>

  <script>
    let selectedLanguage = 'en';
    
    const translations = {
      en: {
        description: "Ask me anything. I'll provide creative and helpful answers.<br>From coding and writing to analysis and brainstorming - I'm here to help.",
        startBtn: "Start Chatting",
        feature1Title: "Natural Conversations",
        feature1Desc: "Real-time streaming for smooth, natural dialogue",
        feature2Title: "Memory",
        feature2Desc: "Remembers previous conversations for context",
        feature3Title: "Fast Responses",
        feature3Desc: "Powered by latest AI models for quick answers"
      },
      ko: {
        description: "무엇이든 물어보세요. 창의적이고 도움이 되는 답변을 드립니다.<br>코딩, 글쓰기, 분석, 아이디어 제안까지 모든 것을 도와드려요.",
        startBtn: "채팅 시작하기",
        feature1Title: "자연스러운 대화",
        feature1Desc: "실시간 스트리밍으로 부드럽고 자연스러운 대화",
        feature2Title: "기억 기능",
        feature2Desc: "이전 대화 내용을 기억하여 맥락적 응답",
        feature3Title: "빠른 응답",
        feature3Desc: "최신 AI 모델로 신속한 답변 제공"
      },
      ja: {
        description: "何でもお聞きください。創造的で役立つ回答を提供します。<br>コーディング、執筆、分析、アイデア提案まで、すべてをお手伝いします。",
        startBtn: "チャット開始",
        feature1Title: "自然な会話",
        feature1Desc: "リアルタイムストリーミングでスムーズで自然な対話",
        feature2Title: "記憶機能",
        feature2Desc: "以前の会話を記憶してコンテキストに応じた応答",
        feature3Title: "高速応答",
        feature3Desc: "最新のAIモデルで迅速な回答を提供"
      },
      zh: {
        description: "向我询问任何问题。我将提供创意且有用的答案。<br>从编程、写作到分析、头脑风暴 - 我都能帮助您。",
        startBtn: "开始聊天",
        feature1Title: "自然对话",
        feature1Desc: "实时流式传输，流畅自然的对话体验",
        feature2Title: "记忆功能",
        feature2Desc: "记住之前的对话内容，提供有上下文的回应",
        feature3Title: "快速响应",
        feature3Desc: "采用最新AI模型，提供快速回答"
      },
      es: {
        description: "Pregúntame cualquier cosa. Proporcionaré respuestas creativas y útiles.<br>Desde programación y escritura hasta análisis e ideas - estoy aquí para ayudar.",
        startBtn: "Comenzar Chat",
        feature1Title: "Conversaciones Naturales",
        feature1Desc: "Transmisión en tiempo real para diálogo suave y natural",
        feature2Title: "Memoria",
        feature2Desc: "Recuerda conversaciones previas para respuestas contextuales",
        feature3Title: "Respuestas Rápidas",
        feature3Desc: "Impulsado por los últimos modelos de IA para respuestas rápidas"
      },
      fr: {
        description: "Demandez-moi n'importe quoi. Je fournirai des réponses créatives et utiles.<br>Du codage à l'écriture en passant par l'analyse et le brainstorming - je suis là pour vous aider.",
        startBtn: "Commencer le Chat",
        feature1Title: "Conversations Naturelles",
        feature1Desc: "Streaming en temps réel pour un dialogue fluide et naturel",
        feature2Title: "Mémoire",
        feature2Desc: "Se souvient des conversations précédentes pour des réponses contextuelles",
        feature3Title: "Réponses Rapides",
        feature3Desc: "Alimenté par les derniers modèles d'IA pour des réponses rapides"
      }
    };
    
    function selectLanguage(lang) {
      selectedLanguage = lang;
      
      // 언어 버튼 상태 업데이트
      document.querySelectorAll('.lang-btn').forEach(btn => {
        btn.classList.remove('active');
      });
      document.querySelector(`[data-lang="${lang}"]`).classList.add('active');
      
      // 텍스트 업데이트
      const translation = translations[lang];
      document.getElementById('description').innerHTML = translation.description;
      document.getElementById('startBtn').textContent = translation.startBtn;
      document.getElementById('feature1Title').textContent = translation.feature1Title;
      document.getElementById('feature1Desc').textContent = translation.feature1Desc;
      document.getElementById('feature2Title').textContent = translation.feature2Title;
      document.getElementById('feature2Desc').textContent = translation.feature2Desc;
      document.getElementById('feature3Title').textContent = translation.feature3Title;
      document.getElementById('feature3Desc').textContent = translation.feature3Desc;
    }
    
    function startChat() {
      window.location.href = `/chat?lang=${selectedLanguage}`;
    }
  </script>
</body>
</html>
"""

@app.route("/chat")
def chat_page():
    # 세션 ID 생성
    if 'session_id' not in session:
        session['session_id'] = str(uuid.uuid4())
    
    # 언어 파라미터 가져오기
    lang = request.args.get('lang', 'en')
    
    return f"""
<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>OpenGPT Chat - CTTechnology</title>
  <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/highlight.js/11.9.0/styles/default.min.css">
  <script src="https://cdnjs.cloudflare.com/ajax/libs/highlight.js/11.9.0/highlight.min.js"></script>
  <script src="https://cdnjs.cloudflare.com/ajax/libs/marked/4.3.0/marked.min.js"></script>
  <style>
    /* 스크롤바 제거 */
    ::-webkit-scrollbar {{
      display: none;
    }}
    
    * {{
      -ms-overflow-style: none;
      scrollbar-width: none;
    }}
    
    body {{
      font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
      background: #f7f7f8;
      color: #202123;
      margin: 0;
      display: flex;
      flex-direction: column;
      height: 100vh;
      overflow-x: hidden;
      width: 100vw;
    }}
    
    header {{
      background: #fff;
      border-bottom: 1px solid #e5e5e5;
      padding: 12px 20px;
      font-weight: 600;
      font-size: 16px;
      text-align: center;
      position: sticky;
      top: 0;
      z-index: 10;
      display: flex;
      justify-content: space-between;
      align-items: center;
      flex-shrink: 0;
      width: 100%;
    }}
    
    .home-button {{
      background: #f7f7f8;
      border: 1px solid #e5e5e5;
      border-radius: 6px;
      padding: 6px 12px;
      color: #565869;
      text-decoration: none;
      font-size: 14px;
      transition: background 0.2s;
      cursor: pointer;
      white-space: nowrap;
    }}
    
    .home-button:hover {{
      background: #e5e5e5;
    }}
    
    main {{
      flex: 1;
      display: flex;
      justify-content: center;
      overflow: hidden;
      width: 100%;
      position: relative;
    }}
    
    .chat-container {{
      width: 100%;
      max-width: 768px;
      display: flex;
      flex-direction: column;
      height: 100%;
      min-width: 0;
      position: relative;
    }}
    
    .messages-area {{
      flex: 1;
      overflow-y: auto;
      scroll-behavior: auto;
      padding: 0;
      width: 100%;
      position: relative;
    }}
    
    .message-row {{
      padding: 24px 20px;
      border-bottom: 1px solid rgba(0,0,0,.1);
      width: 100%;
      min-width: 0;
    }}
    
    .message-row.user {{
      background: white;
    }}
    
    .message-row.assistant {{
      background: #f7f7f8;
    }}
    
    .message-content {{
      max-width: 100%;
      margin: 0 auto;
      display: flex;
      gap: 16px;
      min-width: 0;
      width: 100%;
    }}
    
    .message-content.user {{
      justify-content: flex-end;
    }}
    
    .avatar {{
      width: 30px;
      height: 30px;
      border-radius: 4px;
      background: #19c37d;
      flex-shrink: 0;
      display: flex;
      align-items: center;
      justify-content: center;
      color: white;
      font-weight: 600;
      font-size: 12px;
      margin-top: 2px;
    }}
    
    .avatar.assistant {{ 
      display: none;
    }}
    
    .message-text {{
      flex: 1;
      font-size: 16px;
      line-height: 1.7;
      color: #202123;
      word-wrap: break-word;
      word-break: break-word;
      overflow-wrap: break-word;
      hyphens: auto;
      min-width: 0;
      max-width: 100%;
      width: calc(100% - 46px);
    }}
    
    .message-row.assistant .message-text {{
      width: 100%;
    }}
    
    .message-text * {{
      max-width: 100% !important;
      word-wrap: break-word !important;
      word-break: break-word !important;
      overflow-wrap: break-word !important;
      box-sizing: border-box !important;
    }}
    
    .message-text h1,
    .message-text h2,
    .message-text h3 {{
      margin: 16px 0 8px 0;
      color: #202123;
      word-break: break-word;
      line-height: 1.3;
    }}
    
    .message-text h1 {{ font-size: 1.4em; }}
    .message-text h2 {{ font-size: 1.2em; }}
    .message-text h3 {{ font-size: 1.1em; }}
    
    .message-text p {{
      margin: 8px 0;
      word-break: break-word;
      line-height: 1.6;
    }}
    
    .message-text ul,
    .message-text ol {{
      margin: 8px 0;
      padding-left: 20px;
      max-width: 100%;
    }}
    
    .message-text li {{
      margin: 4px 0;
      word-break: break-word;
    }}
    
    .message-text blockquote {{
      border-left: 4px solid #e5e5e5;
      margin: 16px 0;
      padding-left: 16px;
      color: #666;
      word-break: break-word;
      max-width: 100%;
    }}
    
    .message-text table {{
      border-collapse: collapse;
      margin: 16px 0;
      width: 100%;
      max-width: 100%;
      font-size: 13px;
      table-layout: auto;
      overflow: hidden;
    }}
    
    .message-text th,
    .message-text td {{
      border: 1px solid #e5e5e5;
      padding: 6px 8px;
      text-align: left;
      word-break: break-word;
      overflow-wrap: break-word;
      hyphens: auto;
      max-width: 0;
      overflow: hidden;
    }}
    
    .message-text th {{
      background: #f7f7f8;
      font-weight: 600;
      font-size: 12px;
    }}
    
    .message-text pre {{
      background: #f6f8fa;
      border: 1px solid #e1e4e8;
      border-radius: 6px;
      padding: 12px;
      overflow-x: auto;
      margin: 16px 0;
      max-width: 100%;
      font-size: 13px;
      line-height: 1.4;
    }}
    
    .message-text code {{
      background: #f6f8fa;
      padding: 2px 4px;
      border-radius: 3px;
      font-family: 'SF Mono', Monaco, 'Cascadia Code', 'Roboto Mono', Consolas, 'Courier New', monospace;
      font-size: 0.85em;
      word-break: break-all;
      overflow-wrap: break-word;
    }}
    
    .message-text pre code {{
      background: none;
      padding: 0;
      word-break: normal;
      white-space: pre-wrap;
      overflow-wrap: break-word;
    }}
    
    .input-area {{
      background: #fff;
      border-top: 1px solid #d9d9e3;
      padding: 16px;
      flex-shrink: 0;
      width: 100%;
    }}
    
    .input-wrapper {{
      max-width: 768px;
      margin: 0 auto;
      width: 100%;
    }}
    
    .input-box {{
      display: flex;
      background: #f7f7f8;
      border: 1px solid #d9d9e3;
      border-radius: 12px;
      padding: 8px 12px;
      align-items: flex-end;
      gap: 8px;
      width: 100%;
    }}
    
    #input {{
      flex: 1;
      border: none;
      background: transparent;
      outline: none;
      font-size: 16px;
      resize: none;
      line-height: 1.5;
      min-height: 20px;
      max-height: 120px;
      font-family: inherit;
      word-wrap: break-word;
      min-width: 0;
    }}
    
    #send {{
      background: #19c37d;
      border: none;
      border-radius: 6px;
      color: white;
      cursor: pointer;
      padding: 8px 16px;
      font-size: 14px;
      font-weight: 600;
      transition: background 0.2s;
      white-space: nowrap;
      flex-shrink: 0;
    }}
    
    #send:hover:not(:disabled) {{ 
      background: #15a46a; 
    }}
    
    #send:disabled {{
      background: #d9d9e3;
      cursor: not-allowed;
    }}
    
    .welcome {{
      text-align: center;
      margin: 80px 20px;
      color: #565869;
    }}
    
    .welcome h1 {{
      font-size: 24px;
      font-weight: 600;
      margin-bottom: 12px;
      color: #202123;
    }}
    
    .examples {{
      display: grid;
      grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
      gap: 12px;
      margin-top: 24px;
    }}
    
    .example-card {{
      background: #fff;
      border: 1px solid #e5e5e5;
      border-radius: 8px;
      padding: 16px;
      cursor: pointer;
      transition: all 0.2s;
      font-size: 14px;
      color: #565869;
      text-align: left;
      word-break: break-word;
    }}
    
    .example-card:hover {{ 
      background: #f0f0f0;
      border-color: #19c37d;
    }}
    
    .typing {{
      display: inline-block;
      margin-left: 6px;
    }}
    
    .dot {{
      height: 6px;
      width: 6px;
      margin: 0 1px;
      background-color: #8e8ea0;
      border-radius: 50%;
      display: inline-block;
      animation: blink 1.4s infinite both;
    }}
    
    .dot:nth-child(2) {{ animation-delay: 0.2s; }}
    .dot:nth-child(3) {{ animation-delay: 0.4s; }}
    
    @keyframes blink {{
      0%, 80%, 100% {{ opacity: 0; }}
      40% {{ opacity: 1; }}
    }}
    
    @media (max-width: 768px) {{
      .examples {{
        grid-template-columns: 1fr;
      }}
      
      .message-text {{
        font-size: 15px;
      }}
      
      .message-row {{
        padding: 20px 16px;
      }}
      
      .input-area {{
        padding: 12px;
      }}
      
      .message-text table {{
        font-size: 12px;
      }}
      
      .message-text th,
      .message-text td {{
        padding: 4px 6px;
      }}
    }}
  </style>
</head>
<body>
  <header>
    <a href="/" class="home-button">← Home</a>
    <span>OpenGPT Chat (by CTTechnology)</span>
    <button class="home-button" onclick="clearChat()">🗑️ Clear Chat</button>
  </header>
  
  <main>
    <div class="chat-container">
      <div class="messages-area" id="chatbox">
        <div class="welcome" id="welcome">
          <h1>Hello! I'm OpenGPT 🎉</h1>
          <p>Ask me anything. I'm here to help with helpful answers!</p>
          <div class="examples">
            <div class="example-card" onclick="sendExample('Explain programming concepts')">
              <strong>💻 Programming</strong><br>
              Explain programming concepts
            </div>
            <div class="example-card" onclick="sendExample('Help me with creative writing')">
              <strong>✍️ Writing</strong><br>
              Help me with creative writing
            </div>
            <div class="example-card" onclick="sendExample('Organize my daily tasks')">
              <strong>📋 Productivity</strong><br>
              Organize my daily tasks
            </div>
            <div class="example-card" onclick="sendExample('I need some creative ideas')">
              <strong>💡 Ideas</strong><br>
              I need some creative ideas
            </div>
          </div>
        </div>
      </div>
      
      <div class="input-area">
        <div class="input-wrapper">
          <div class="input-box">
            <textarea id="input" rows="1" placeholder="Send a message..."></textarea>
            <button id="send">Send</button>
          </div>
        </div>
      </div>
    </div>
  </main>

  <script>
    const chatbox = document.getElementById("chatbox");
    const input = document.getElementById("input");
    const send = document.getElementById("send");
    const welcome = document.getElementById("welcome");
    const selectedLanguage = '{lang}';

    // Markdown 설정
    marked.setOptions({{
      highlight: function(code, lang) {{
        if (lang && hljs.getLanguage(lang)) {{
          return hljs.highlight(code, {{language: lang}}).value;
        }}
        return hljs.highlightAuto(code).value;
      }},
      breaks: true,
      gfm: true
    }});

    // 텍스트 영역 자동 높이 조절
    input.addEventListener('input', function() {{
      this.style.height = 'auto';
      this.style.height = Math.min(this.scrollHeight, 120) + 'px';
    }});

    // 스크롤 최적화 변수
    let isScrolling = false;
    let scrollTimeout;

    function smoothScrollToBottom() {{
      if (!isScrolling) {{
        isScrolling = true;
        chatbox.scrollTop = chatbox.scrollHeight;
        
        clearTimeout(scrollTimeout);
        scrollTimeout = setTimeout(() => {{
          isScrolling = false;
        }}, 100);
      }}
    }}

    function addMessage(text, isBot=false) {{
      if (welcome && welcome.parentNode) {{
        welcome.remove();
      }}
      
      const row = document.createElement("div");
      row.className = "message-row " + (isBot ? "assistant" : "user");
      
      const content = document.createElement("div");
      content.className = "message-content" + (isBot ? "" : " user");
      
      const messageDiv = document.createElement("div");
      messageDiv.className = "message-text";
      
      if (!isBot) {{
        const avatar = document.createElement("div");
        avatar.className = "avatar";
        avatar.textContent = "You";
        content.appendChild(avatar);
      }}
      
      if (isBot) {{
        // 마크다운 렌더링
        messageDiv.innerHTML = marked.parse(text);
        // 코드 하이라이팅
        messageDiv.querySelectorAll('pre code').forEach((block) => {{
          hljs.highlightElement(block);
        }});
      }} else {{
        messageDiv.textContent = text;
      }}
      
      content.appendChild(messageDiv);
      row.appendChild(content);
      chatbox.appendChild(row);
      
      // 부드러운 스크롤
      smoothScrollToBottom();
      
      return messageDiv;
    }}

    async function sendMessage() {{
      const message = input.value.trim();
      if (!message) return;
      
      addMessage(message, false);
      input.value = "";
      input.style.height = 'auto';
      send.disabled = true;

      const botMsg = addMessage("", true);
      const indicator = document.createElement("span");
      indicator.className = "typing";
      indicator.innerHTML = '<span class="dot"></span><span class="dot"></span><span class="dot"></span>';
      botMsg.appendChild(indicator);

      try {{
        const response = await fetch("/api/chat", {{
          method: "POST",
          headers: {{ "Content-Type": "application/x-www-form-urlencoded" }},
          body: "message=" + encodeURIComponent(message) + "&lang=" + encodeURIComponent(selectedLanguage)
        }});

        const reader = response.body.getReader();
        const decoder = new TextDecoder("utf-8");
        let botMessage = "";
        let updateCounter = 0;
        
        botMsg.innerHTML = "";
        
        while (true) {{
          const {{ done, value }} = await reader.read();
          if (done) break;
          
          const chunk = decoder.decode(value, {{ stream: true }});
          botMessage += chunk;
          
          // 화면 흔들림 방지를 위해 업데이트 빈도 조절
          updateCounter++;
          if (updateCounter % 3 === 0 || done) {{
            // 실시간 마크다운 렌더링
            botMsg.innerHTML = marked.parse(botMessage);
            botMsg.querySelectorAll('pre code').forEach((block) => {{
              hljs.highlightElement(block);
            }});
            
            // 부드러운 스크롤
            smoothScrollToBottom();
          }}
        }}
        
        // 최종 렌더링
        botMsg.innerHTML = marked.parse(botMessage);
        botMsg.querySelectorAll('pre code').forEach((block) => {{
          hljs.highlightElement(block);
        }});
        smoothScrollToBottom();
        
      }} catch (error) {{
        botMsg.textContent = "Sorry, an error occurred. Please try again.";
      }}
      
      send.disabled = false;
      input.focus();
    }}

    function sendExample(text) {{
      input.value = text;
      sendMessage();
    }}
    
    function clearChat() {{
      if (confirm('Are you sure you want to clear all conversation history?')) {{
        fetch('/api/clear', {{ method: 'POST' }})
          .then(() => location.reload());
      }}
    }}

    send.addEventListener("click", sendMessage);
    
    input.addEventListener("keydown", function(e) {{
      if (e.key === "Enter" && !e.shiftKey) {{
        e.preventDefault();
        sendMessage();
      }}
    }});

    // 페이지 로드시 입력창에 포커스
    input.focus();
  </script>
</body>
</html>
"""

@app.route("/api/chat", methods=["POST"])
def api_chat():
    user_message = request.form["message"]
    language = request.form.get("lang", "en")
    session_id = session.get('session_id')
    
    if not session_id:
        session['session_id'] = str(uuid.uuid4())
        session_id = session['session_id']
    
    # 세션별 대화 기록 가져오기
    if session_id not in conversations:
        conversations[session_id] = []
    
    # 사용자 메시지를 대화 기록에 추가
    conversations[session_id].append({"role": "user", "content": user_message})

    # 언어별 시스템 프롬프트
    language_prompts = {
        "en": "You are OpenGPT, an advanced AI chatbot created by CTTechnology. Be helpful, polite, and creative. Answer clearly with examples if possible. Use proper markdown formatting for better readability - use headers, lists, code blocks, tables when appropriate. For code examples, always specify the language. Structure your responses well with clear sections. Remember our conversation history and provide contextual responses. Respond in English.",
        "ko": "당신은 CTTechnology에서 만든 고급 AI 챗봇 OpenGPT입니다. 도움이 되고, 정중하고, 창의적으로 답변하세요. 가능하면 예시와 함께 명확하게 답변하세요. 가독성을 위해 적절한 마크다운 형식을 사용하세요 - 헤더, 목록, 코드 블록, 테이블 등을 적절히 활용하세요. 코드 예시의 경우 항상 언어를 명시하세요. 명확한 섹션으로 응답을 잘 구조화하세요. 대화 기록을 기억하고 맥락적인 응답을 제공하세요. 한국어로 답변하세요.",
        "ja": "あなたはCTTechnologyが作成した高度なAIチャットボットOpenGPTです。親切で礼儀正しく、創造的に答えてください。可能であれば例とともに明確に答えてください。読みやすさのために適切なマークダウン形式を使用してください - ヘッダー、リスト、コードブロック、テーブルなどを適切に活用してください。コード例の場合は常に言語を明示してください。明確なセクションで応答を構造化してください。会話履歴を覚えて文脈的な応答を提供してください。日本語で回答してください。",
        "zh": "您是CTTechnology创建的高级AI聊天机器人OpenGPT。请提供有帮助、礼貌和创意的回答。尽可能用例子清楚地回答。为了提高可读性，请使用适当的markdown格式 - 适当使用标题、列表、代码块、表格等。对于代码示例，请始终指定语言。用清晰的部分很好地构建您的回答。记住我们的对话历史并提供上下文相关的回答。用中文回答。",
        "es": "Eres OpenGPT, un chatbot de IA avanzado creado por CTTechnology. Sé útil, educado y creativo. Responde claramente con ejemplos si es posible. Usa el formato markdown apropiado para mejor legibilidad - usa encabezados, listas, bloques de código, tablas cuando sea apropiado. Para ejemplos de código, siempre especifica el lenguaje. Estructura bien tus respuestas con secciones claras. Recuerda nuestro historial de conversación y proporciona respuestas contextuales. Responde en español.",
        "fr": "Vous êtes OpenGPT, un chatbot IA avancé créé par CTTechnology. Soyez utile, poli et créatif. Répondez clairement avec des exemples si possible. Utilisez un formatage markdown approprié pour une meilleure lisibilité - utilisez des en-têtes, des listes, des blocs de code, des tableaux le cas échéant. Pour les exemples de code, spécifiez toujours le langage. Structurez bien vos réponses avec des sections claires. Souvenez-vous de notre historique de conversation et fournissez des réponses contextuelles. Répondez en français."
    }

    system_prompt = language_prompts.get(language, language_prompts["en"])

    # 전체 대화 기록을 포함한 메시지 구성
    messages = [{"role": "system", "content": system_prompt}] + conversations[session_id]

    payload = {
        "messages": messages,
        "model": "openai/gpt-oss-120b:fireworks-ai",
        "stream": True,
        "max_tokens": 4000,
        "temperature": 0.7
    }

    def generate():
        assistant_response = ""
        try:
            for chunk in stream_query(payload):
                if "choices" in chunk and len(chunk["choices"]) > 0:
                    delta = chunk["choices"][0]["delta"].get("content", "")
                    if delta:
                        assistant_response += delta
                        yield delta
            
            # AI 응답을 대화 기록에 추가
            if assistant_response:
                conversations[session_id].append({"role": "assistant", "content": assistant_response})
        except Exception as e:
            yield f"Error: {str(e)}"

    return Response(generate(), mimetype="text/plain")

@app.route("/api/clear", methods=["POST"])
def clear_conversation():
    session_id = session.get('session_id')
    if session_id and session_id in conversations:
        del conversations[session_id]
    return "OK"

if __name__ == "__main__":
    app.run(debug=True)