import os
import re
import random
import requests
from flask import Flask, jsonify, request, Response

app = Flask(__name__)


def get_key_pool(prefix):
    keys = []
    main_key = os.environ.get(prefix, "")
    if main_key:
        keys.append(main_key)

    for i in range(1, 10):
        key = os.environ.get(f"{prefix}_{i}", "")
        if key and key not in keys:
            keys.append(key)

    return keys


GROQ_KEYS = get_key_pool("GROQ_API_KEY")
OPENROUTER_KEYS = get_key_pool("OPENROUTER_API_KEY")
GEMINI_KEYS = get_key_pool("GEMINI_API_KEY") or get_key_pool("GOOGLE_API_KEY")


def call_groq(model_id="llama-3.1-8b-instant", messages=[]):
    if not GROQ_KEYS:
        return None

    chosen_key = random.choice(GROQ_KEYS)
    payload = {"model": model_id, "messages": messages}
    headers = {
        "Authorization": f"Bearer {chosen_key}",
        "Content-Type": "application/json",
    }
    try:
        r = requests.post(
            "https://api.groq.com/openai/v1/chat/completions",
            headers=headers,
            json=payload,
            timeout=15,
        )
        if r.status_code == 200:
            return r.json()
    except Exception:
        pass
    return None


def call_openrouter(model_id="openrouter/auto", messages=[]):
    if not OPENROUTER_KEYS:
        return None

    chosen_key = random.choice(OPENROUTER_KEYS)
    payload = {"model": model_id, "messages": messages}
    headers = {
        "Authorization": f"Bearer {chosen_key}",
        "Content-Type": "application/json",
    }
    try:
        r = requests.post(
            "https://openrouter.ai/api/v1/chat/completions",
            headers=headers,
            json=payload,
            timeout=15,
        )
        if r.status_code == 200:
            return r.json()
    except Exception:
        pass
    return None


def call_gemini(model_id="gemini-1.5-flash", messages=[]):
    if not GEMINI_KEYS:
        return None

    chosen_key = random.choice(GEMINI_KEYS)

    # Convert OpenAI message format to Gemini contents format
    contents = []
    for msg in messages:
        role = "user" if msg.get("role") in ["user", "system"] else "model"
        contents.append({"role": role, "parts": [{"text": msg.get("content", "")}]})

    url = f"https://generativelanguage.googleapis.com/v1beta/models/{model_id}:generateContent?key={chosen_key}"
    headers = {"Content-Type": "application/json"}
    payload = {"contents": contents}

    try:
        r = requests.post(url, headers=headers, json=payload, timeout=15)
        if r.status_code == 200:
            res_data = r.json()
            # Format to match standard Chat Completion response structure
            generated_text = res_data["candidates"][0]["content"]["parts"][0]["text"]
            return {
                "choices": [{"message": {"role": "assistant", "content": generated_text}}]
            }
    except Exception:
        pass
    return None


def is_legacy_ios(user_agent):
    if not user_agent:
        return True

    match = re.search(r"OS (\d+)_", user_agent)
    if match:
        major_version = int(match.group(1))
        if major_version <= 13:
            return True
        return False

    if "iPhone" in user_agent or "iPad" in user_agent or "iPod" in user_agent:
        return True

    return False


# ==========================================
# 1. ULTRA-COMPATIBLE LEGACY HTML (iOS 6-12)
# Self-contained ES5 Markdown parser (No CDNs)
# ==========================================
LEGACY_HTML = """<!DOCTYPE html>
<html>
<head>
    <meta http-equiv="Content-Type" content="text/html; charset=utf-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0, maximum-scale=1.0, user-scalable=no">
    <title>iChat AI</title>
    <meta name="apple-mobile-web-app-capable" content="yes">
    <meta name="apple-mobile-web-app-status-bar-style" content="black">
    <meta name="apple-mobile-web-app-title" content="iChat AI">

    <link rel="apple-touch-icon" href="https://ichatai.up.railway.app/static/icon.png">
    <link rel="icon" type="image/x-icon" href="https://ichatai.up.railway.app/static/icon.png">

    <style type="text/css">
        * {
            -webkit-box-sizing: border-box;
            box-sizing: border-box;
            margin: 0;
            padding: 0;
        }
        html, body {
            width: 100%;
            height: 100%;
            font-family: "Helvetica Neue", Helvetica, Arial, sans-serif;
            background-color: #d8e0e8;
        }
        body {
            background-image: -webkit-gradient(linear, left top, right top, color-stop(0.5, #c8d2dc), color-stop(0.5, #d8e0e8));
            background-image: -webkit-linear-gradient(left, #c8d2dc 50%, #d8e0e8 50%);
            background-size: 4px 100%;
        }
        .header {
            position: fixed;
            top: 0; left: 0; right: 0;
            height: 44px;
            background: -webkit-gradient(linear, left top, left bottom, from(#b0bcc7), color-stop(0.5, #889bb0), color-stop(0.51, #6f8299), to(#6d84a2));
            background: -webkit-linear-gradient(top, #b0bcc7 0%, #889bb0 50%, #6f8299 51%, #6d84a2 100%);
            color: #ffffff;
            text-align: center;
            line-height: 44px;
            font-size: 18px;
            font-weight: bold;
            text-shadow: 0px -1px 1px rgba(0, 0, 0, 0.6);
            border-bottom: 1px solid #2d3e52;
            -webkit-box-shadow: 0px 1px 4px rgba(0,0,0,0.4);
            z-index: 1000;
        }
        #chat-container {
            padding: 54px 10px 60px 10px;
            overflow-y: auto;
            -webkit-overflow-scrolling: touch;
        }
        .bubble {
            max-width: 85%;
            padding: 8px 12px;
            margin-bottom: 10px;
            -webkit-border-radius: 14px;
            border-radius: 14px;
            font-size: 14px;
            line-height: 1.35;
            word-wrap: break-word;
        }
        .user {
            float: right;
            clear: both;
            background: -webkit-gradient(linear, left top, left bottom, from(#0084ff), to(#006bde));
            background: -webkit-linear-gradient(top, #0084ff 0%, #006bde 100%);
            color: #ffffff;
            border: 1px solid #0056b3;
            text-shadow: 0px -1px 1px #003d80;
            -webkit-box-shadow: 0px 1px 2px rgba(0,0,0,0.2);
        }
        .ai {
            float: left;
            clear: both;
            background: -webkit-gradient(linear, left top, left bottom, from(#ffffff), to(#e5e5ea));
            background: -webkit-linear-gradient(top, #ffffff 0%, #e5e5ea 100%);
            color: #000000;
            border: 1px solid #b8b8b8;
            -webkit-box-shadow: 0px 1px 2px rgba(0,0,0,0.15);
        }

        .ai p { margin: 0 0 6px 0; }
        .ai p:last-child { margin-bottom: 0; }
        .ai h1, .ai h2, .ai h3 { margin: 6px 0 4px 0; font-size: 15px; }
        .ai ul, .ai ol { margin: 4px 0 4px 18px; padding: 0; }
        .ai code {
            background: rgba(0,0,0,0.08);
            padding: 1px 4px;
            font-family: Courier, monospace;
            font-size: 12px;
            -webkit-border-radius: 3px;
            border-radius: 3px;
        }
        .ai pre {
            background: #222222;
            color: #00ff66;
            padding: 6px 8px;
            font-family: Courier, monospace;
            font-size: 11px;
            overflow-x: auto;
            -webkit-border-radius: 6px;
            border-radius: 6px;
            margin: 6px 0;
            white-space: pre-wrap;
        }

        .input-area {
            position: fixed;
            bottom: 0; left: 0; right: 0;
            height: 48px;
            background: -webkit-gradient(linear, left top, left bottom, from(#ccd5e0), to(#a0b0c0));
            background: -webkit-linear-gradient(top, #ccd5e0 0%, #a0b0c0 100%);
            padding: 7px 4px;
            border-top: 1px solid #6f8299;
            -webkit-box-shadow: 0px -1px 3px rgba(0,0,0,0.2);
            z-index: 1000;
        }
        select.model-select {
            width: 28%;
            height: 32px;
            font-size: 10px;
            font-weight: bold;
            color: #333;
            background: #f7f7f7;
            border: 1px solid #888;
            -webkit-border-radius: 10px;
            border-radius: 10px;
            outline: none;
            padding: 2px;
        }
        input.legacy-input {
            width: 38%;
            height: 32px;
            padding: 4px 8px;
            font-size: 13px;
            -webkit-border-radius: 14px;
            border-radius: 14px;
            border: 1px solid #888;
            outline: none;
            -webkit-box-shadow: inset 0px 1px 2px rgba(0,0,0,0.3);
        }
        .mic-btn {
            width: 12%;
            height: 32px;
            font-size: 14px;
            color: #333;
            background: -webkit-gradient(linear, left top, left bottom, from(#ffffff), to(#d0d0d0));
            background: -webkit-linear-gradient(top, #ffffff 0%, #d0d0d0 100%);
            border: 1px solid #777;
            -webkit-border-radius: 14px;
            border-radius: 14px;
            outline: none;
            padding: 0;
        }
        .mic-btn.recording {
            background: -webkit-gradient(linear, left top, left bottom, from(#ff3b30), to(#cc2b23));
            background: -webkit-linear-gradient(top, #ff3b30 0%, #cc2b23 100%);
            color: #ffffff;
            border: 1px solid #aa110a;
        }
        button.send-btn {
            width: 18%;
            height: 32px;
            float: right;
            font-size: 13px;
            font-weight: bold;
            color: #ffffff;
            background: -webkit-gradient(linear, left top, left bottom, from(#4cd964), to(#2db844));
            background: -webkit-linear-gradient(top, #4cd964 0%, #2db844 100%);
            border: 1px solid #1e872d;
            -webkit-border-radius: 14px;
            border-radius: 14px;
            text-shadow: 0px -1px 1px #14591e;
            -webkit-box-shadow: 0px 1px 2px rgba(0,0,0,0.3);
        }
    </style>
</head>
<body>
    <div class="header">iChat AI</div>

    <div id="chat-container">
        <div class="bubble ai">Hello! Pick a model below to start chatting.</div>
    </div>

    <div class="input-area">
        <select id="modelSelect" class="model-select">
            <option value="gemini-flash" selected>Google (Gemini 1.5 Flash)</option>
            <option value="groq-llama-3.1">Groq (Llama 3.1 8B)</option>
            <option value="groq-llama-3.3">Groq (Llama 3.3 70B)</option>
            <option value="or-gemma-2">OpenRouter (Gemma 2 9B)</option>
            <option value="groq-gpt-oss">Groq (GPT OSS 20B)</option>
            <option value="or-nemotron">OpenRouter (Nemotron Free)</option>
            <option value="or-qwen-coder">OpenRouter (Qwen Coder)</option>
        </select>
        <input type="text" id="userInput" class="legacy-input" placeholder="Message">
        <button type="button" id="micBtn" class="mic-btn" onclick="toggleDictation()">🎙️</button>
        <button type="button" class="send-btn" onclick="sendMessage()">Send</button>
    </div>

    <script type="text/javascript">
        function parseMarkdown(src) {
            if (!src) return "";
            var out = src.replace(/&/g, "&amp;").replace(/</g, "&lt;").replace(/>/g, "&gt;");
            
            out = out.replace(/```([\s\S]*?)```/g, function(match, code) {
                return '<pre><code>' + code.replace(/^\n+|\n+$/g, '') + '</code></pre>';
            });

            out = out.replace(/`([^`]+)`/g, '<code>$1</code>');
            out = out.replace(/^### (.*$)/gim, '<h3>$1</h3>');
            out = out.replace(/^## (.*$)/gim, '<h2>$1</h2>');
            out = out.replace(/^# (.*$)/gim, '<h1>$1</h1>');

            out = out.replace(/\*\*([^*]+)\*\*/g, '<strong>$1</strong>');
            out = out.replace(/__([^_]+)__/g, '<strong>$1</strong>');
            out = out.replace(/\*([^*]+)\*/g, '<em>$1</em>');
            out = out.replace(/_([^_]+)_/g, '<em>$1</em>');

            out = out.replace(/^\s*[\*\-]\s+(.*$)/gim, '<li>$1</li>');
            out = out.replace(/(<li>[\s\S]*?<\/li>)/gim, '<ul>$1</ul>');
            out = out.replace(/<\/ul>\s*<ul>/gim, '');

            out = out.replace(/\n\n/g, '</p><p>');
            out = out.replace(/\n/g, '<br>');

            return out;
        }

        var recognition = null;
        var isRecording = false;

        if ('webkitSpeechRecognition' in window || 'SpeechRecognition' in window) {
            var SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;
            recognition = new SpeechRecognition();
            recognition.continuous = false;
            recognition.interimResults = true;

            recognition.onstart = function() {
                isRecording = true;
                var micBtn = document.getElementById("micBtn");
                if (micBtn) {
                    micBtn.className = "mic-btn recording";
                    micBtn.innerText = "🛑";
                }
            };

            recognition.onresult = function(event) {
                var transcript = "";
                for (var i = event.resultIndex; i < event.results.length; ++i) {
                    transcript += event.results[i][0].transcript;
                }
                document.getElementById("userInput").value = transcript;
            };

            recognition.onerror = function() { stopDictation(); };
            recognition.onend = function() { stopDictation(); };
        }

        function toggleDictation() {
            if (!recognition) {
                alert("Voice dictation is not supported on this browser.");
                return;
            }
            if (isRecording) { recognition.stop(); } else { recognition.start(); }
        }

        function stopDictation() {
            isRecording = false;
            var micBtn = document.getElementById("micBtn");
            if (micBtn) {
                micBtn.className = "mic-btn";
                micBtn.innerText = "🎙️";
            }
        }

        function sendMessage() {
            if (isRecording && recognition) { recognition.stop(); }

            var input = document.getElementById("userInput");
            var modelSelect = document.getElementById("modelSelect");
            var text = input.value;
            if (!text || text.replace(/^\s+|\s+$/g, '') === "") return;

            var container = document.getElementById("chat-container");
            var userDiv = document.createElement("div");
            userDiv.className = "bubble user";
            userDiv.innerText = text;
            container.appendChild(userDiv);

            input.value = "";
            window.scrollTo(0, document.body.scrollHeight);

            var xhr = new XMLHttpRequest();
            xhr.open("POST", "/v1/chat/completions", true);
            xhr.setRequestHeader("Content-Type", "application/json");

            xhr.onreadystatechange = function() {
                if (xhr.readyState === 4) {
                    var aiDiv = document.createElement("div");
                    aiDiv.className = "bubble ai";

                    if (xhr.status === 200) {
                        try {
                            var res = JSON.parse(xhr.responseText);
                            var rawContent = res.choices[0].message.content;
                            aiDiv.innerHTML = parseMarkdown(rawContent);
                        } catch (e) {
                            aiDiv.innerText = "Error parsing response.";
                        }
                    } else {
                        aiDiv.innerText = "Error " + xhr.status + ": Check backend keys.";
                    }

                    container.appendChild(aiDiv);
                    window.scrollTo(0, document.body.scrollHeight);
                }
            };

            xhr.send(JSON.stringify({
                model: modelSelect.value,
                messages: [{role: "user", content: text}]
            }));
        }
    </script>
</body>
</html>"""


# ==========================================
# 2. MODERN HTML TEMPLATE (iOS 14+ / Desktop)
# ==========================================
MODERN_HTML = """<!DOCTYPE html>
<html>
<head>
    <meta name="viewport" content="width=device-width, initial-scale=1.0, maximum-scale=1.0, user-scalable=no">
    <title>iChat AI</title>
    <meta name="apple-mobile-web-app-capable" content="yes">
    <meta name="apple-mobile-web-app-status-bar-style" content="black">
    <meta name="apple-mobile-web-app-title" content="iChat AI">

    <link rel="apple-touch-icon" href="https://ichatai.up.railway.app/static/icon.png">
    <link rel="icon" type="image/x-icon" href="https://ichatai.up.railway.app/static/icon.png">

    <script src="https://cdnjs.cloudflare.com/ajax/libs/showdown/1.9.1/showdown.min.js"></script>

    <link rel="stylesheet" href="https://cdn.jsdelivr.net/npm/framework7@9/framework7-bundle.min.css">
    <link rel="stylesheet" href="https://cdn.jsdelivr.net/npm/framework7-icons@5.0.5/css/framework7-icons.css">
    <script src="https://cdn.jsdelivr.net/npm/framework7@9/framework7-bundle.min.js"></script>

    <style>
        * { box-sizing: border-box; }
        body {
            margin: 0; padding: 0;
            font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Helvetica, Arial, sans-serif;
        }
        .markdown-content p { margin: 0 0 6px 0; }
        .markdown-content p:last-child { margin-bottom: 0; }
        .markdown-content ul, .markdown-content ol { margin: 4px 0 4px 20px; padding: 0; }
        .markdown-content code {
            background: rgba(0,0,0,0.08); padding: 1px 4px;
            font-family: Courier, monospace; font-size: 12px; border-radius: 3px;
        }
        .markdown-content pre {
            background: #222222; color: #00ff66; padding: 6px 8px;
            font-family: Courier, monospace; font-size: 11px; overflow-x: auto;
            border-radius: 6px; margin: 6px 0; white-space: pre-wrap;
        }
        .modern-icon-btn {
            display: flex; align-items: center; justify-content: center;
            font-size: 22px; cursor: pointer;
        }
    </style>
</head>
<body>
    <div id="app">
        <div class="view view-main">
            <div class="page">
                <div class="navbar">
                    <div class="navbar-bg"></div>
                    <div class="navbar-inner">
                        <div class="title">iChat AI</div>
                        <div class="right">
                            <select id="modelSelectModern" style="font-size: 11px; padding: 4px; border-radius: 8px;">
                                <option value="gemini-flash" selected>Gemini 1.5 Flash</option>
                                <option value="groq-llama-3.1">Llama 3.1 8B</option>
                                <option value="groq-llama-3.3">Llama 3.3 70B</option>
                                <option value="or-gemma-2">Gemma 2 9B</option>
                                <option value="groq-gpt-oss">GPT OSS 20B</option>
                                <option value="or-nemotron">Nemotron</option>
                                <option value="or-qwen-coder">Qwen Coder</option>
                            </select>
                        </div>
                    </div>
                </div>

                <div class="toolbar messagebar">
                    <div class="toolbar-inner">
                        <a class="link icon-only modern-icon-btn" id="micBtnModern" onclick="toggleDictation()">
                            <i class="f7-icons">mic_fill</i>
                        </a>
                        <div class="messagebar-area">
                            <textarea id="userInputModern" placeholder="Message"></textarea>
                        </div>
                        <a class="link icon-only modern-icon-btn" onclick="sendMessage()">
                            <i class="f7-icons">arrow_up_circle_fill</i>
                        </a>
                    </div>
                </div>

                <div class="page-content messages-content">
                    <div class="messages" id="f7-messages">
                        <div class="message message-received">
                            <div class="message-content">
                                <div class="message-bubble">
                                    <div class="message-text markdown-content">Hello! Pick a model above to start chatting.</div>
                                </div>
                            </div>
                        </div>
                    </div>
                </div>
            </div>
        </div>
    </div>

    <script>
        var converter = new showdown.Converter({ simpleLineBreaks: true, strikethrough: true, tables: true });
        var f7App = new Framework7({ el: '#app', theme: 'ios' });
        var f7Messages = f7App.messages.create({ el: '#f7-messages', scrollMessages: true });

        var recognition = null;
        var isRecording = false;

        if ('webkitSpeechRecognition' in window || 'SpeechRecognition' in window) {
            var SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;
            recognition = new SpeechRecognition();
            recognition.continuous = false;
            recognition.interimResults = true;

            recognition.onstart = function() {
                isRecording = true;
                var micBtnModern = document.getElementById("micBtnModern");
                if (micBtnModern) micBtnModern.style.color = "#ff3b30";
            };

            recognition.onresult = function(event) {
                var transcript = "";
                for (var i = event.resultIndex; i < event.results.length; ++i) {
                    transcript += event.results[i][0].transcript;
                }
                document.getElementById("userInputModern").value = transcript;
            };

            recognition.onerror = function() { stopDictation(); };
            recognition.onend = function() { stopDictation(); };
        }

        function toggleDictation() {
            if (!recognition) {
                alert("Voice dictation is not supported on this browser.");
                return;
            }
            if (isRecording) { recognition.stop(); } else { recognition.start(); }
        }

        function stopDictation() {
            isRecording = false;
            var micBtnModern = document.getElementById("micBtnModern");
            if (micBtnModern) micBtnModern.style.color = "";
        }

        function sendMessage() {
            if (isRecording && recognition) { recognition.stop(); }

            var inputElem = document.getElementById("userInputModern");
            var modelElem = document.getElementById("modelSelectModern");
            var text = inputElem.value;
            if (!text || text.trim() === "") return;

            var selectedModel = modelElem.value;
            inputElem.value = "";

            f7Messages.addMessage({ text: text, type: 'sent' });

            var xhr = new XMLHttpRequest();
            xhr.open("POST", "/v1/chat/completions", true);
            xhr.setRequestHeader("Content-Type", "application/json");

            xhr.onreadystatechange = function() {
                if (xhr.readyState === 4) {
                    var rawText = "Error communicating with server.";
                    if (xhr.status === 200) {
                        try {
                            var res = JSON.parse(xhr.responseText);
                            rawText = res.choices[0].message.content;
                        } catch (e) {
                            rawText = "Error parsing AI response.";
                        }
                    } else {
                        rawText = "Error " + xhr.status + ": Check API key configuration.";
                    }

                    var formattedHTML = converter.makeHtml(rawText);
                    f7Messages.addMessage({
                        text: '<div class="markdown-content">' + formattedHTML + '</div>',
                        type: 'received'
                    });
                }
            };

            xhr.send(JSON.stringify({
                model: selectedModel,
                messages: [{role: "user", content: text}]
            }));
        }
    </script>
</body>
</html>"""


@app.route("/", methods=["GET"])
def home():
    user_agent = request.headers.get("User-Agent", "")
    if is_legacy_ios(user_agent):
        return Response(LEGACY_HTML, mimetype="text/html")
    return Response(MODERN_HTML, mimetype="text/html")


@app.route("/v1/chat/completions", methods=["POST"])
@app.route("/chat/completions", methods=["POST"])
def chat():
    data = request.get_json(silent=True) or {}
    messages = data.get("messages", [{"role": "user", "content": "Hello"}])
    selected_model = data.get("model", "gemini-flash")

    res = None

    if selected_model == "gemini-flash":
        res = call_gemini("gemini-1.5-flash", messages) or call_groq(
            "llama-3.1-8b-instant", messages
        )
    elif selected_model == "or-gemma-2":
        res = call_openrouter(
            "google/gemma-2-9b-it:free", messages
        ) or call_groq("llama-3.1-8b-instant", messages)
    elif selected_model == "groq-gpt-oss":
        res = call_groq("openai/gpt-oss-20b", messages) or call_openrouter(
            "openai/gpt-oss-20b:free", messages
        )
    elif selected_model == "groq-llama-3.3":
        res = call_groq(
            "llama-3.3-70b-versatile", messages
        ) or call_openrouter("meta-llama/llama-3.3-70b-instruct:free", messages)
    elif selected_model == "or-nemotron":
        res = call_openrouter(
            "nvidia/nemotron-3-super-120b-a12b:free", messages
        ) or call_groq("llama-3.3-70b-versatile", messages)
    elif selected_model == "or-qwen-coder":
        res = call_openrouter(
            "qwen/qwen-2.5-coder-32b-instruct", messages
        ) or call_gemini("gemini-1.5-flash", messages)
    else:
        res = call_gemini("gemini-1.5-flash", messages) or call_groq(
            "llama-3.1-8b-instant", messages
        )

    if res:
        return jsonify(res), 200
    else:
        return jsonify(
            {
                "error": {
                    "message": "All API provider calls failed. Ensure GEMINI_API_KEY, GROQ_API_KEY, or OPENROUTER_API_KEY environment variables are configured properly."
                }
            }
        ), 500


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
