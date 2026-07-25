import os
import random
import requests
from flask import Flask, jsonify, request

app = Flask(__name__)


# Helper function to collect all API keys from environment variables
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


# Gather key pools for both providers
GROQ_KEYS = get_key_pool("GROQ_API_KEY")
OPENROUTER_KEYS = get_key_pool("OPENROUTER_API_KEY")


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


@app.route("/", methods=["GET"])
def home():
    return """
    <!DOCTYPE html>
    <html>
    <head>
        <meta name="viewport" content="width=device-width, initial-scale=1.0, maximum-scale=1.0, user-scalable=no">
        <title>iChat AI</title>
        <meta name="apple-mobile-web-app-capable" content="yes">
        <meta name="apple-mobile-web-app-status-bar-style" content="black">
        <meta name="apple-mobile-web-app-title" content="iChat AI">

        <link rel="apple-touch-icon" href="https://ichatapp-7vsi.onrender.com/static/icon.png">
        <link rel="icon" type="image/x-icon" href="https://ichatapp-7vsi.onrender.com/static/icon.png">
        
        <script src="https://cdnjs.cloudflare.com/ajax/libs/showdown/1.9.1/showdown.min.js"></script>

        <script>
            (function() {
                function getIOSVersion() {
                    var ua = navigator.userAgent;
                    if (/iP(hone|od|ad)/.test(ua)) {
                        var match = ua.match(/OS (\d+)_(\d+)_?(\d+)?/);
                        if (match && match[1]) {
                            return parseInt(match[1], 10);
                        }
                    }
                    return null;
                }

                var iosVer = getIOSVersion();

                if (iosVer === null || iosVer >= 14) {
                    window.isModernUI = true;

                    var f7css = document.createElement('link');
                    f7css.rel = 'stylesheet';
                    f7css.href = 'https://cdn.jsdelivr.net/npm/framework7@9/framework7-bundle.min.css';
                    document.head.appendChild(f7css);

                    var f7icons = document.createElement('link');
                    f7icons.rel = 'stylesheet';
                    f7icons.href = 'https://cdn.jsdelivr.net/npm/@icon/framework7-icons/framework7-icons.css';
                    document.head.appendChild(f7icons);

                    var f7js = document.createElement('script');
                    f7js.src = 'https://cdn.jsdelivr.net/npm/framework7@9/framework7-bundle.min.js';
                    f7js.onload = function() {
                        window.f7App = new Framework7({
                            el: '#app',
                            theme: 'ios',
                        });
                        window.f7Messages = window.f7App.messages.create({
                            el: '#f7-messages',
                            scrollMessages: true
                        });
                    };
                    document.head.appendChild(f7js);
                } else {
                    window.isModernUI = false;
                }
            })();
        </script>

        <style>
            * { -webkit-box-sizing: border-box; box-sizing: border-box; }
            body {
                margin: 0; padding: 0;
                font-family: "Helvetica Neue", Helvetica, Arial, sans-serif;
                background-color: #d8e0e8;
            }
            
            /* Shared Markdown Formatting Styles */
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

            /* Legacy iOS 6 Styles */
            #legacy-container {
                background-image: -webkit-linear-gradient(left, #c8d2dc 50%, #d8e0e8 50%);
                background-size: 4px 100%;
                min-height: 100vh;
            }
            .header {
                position: fixed; top: 0; left: 0; right: 0; height: 44px;
                background: -webkit-linear-gradient(top, #b0bcc7 0%, #889bb0 50%, #6f8299 51%, #6d84a2 100%);
                color: #ffffff; text-align: center; line-height: 44px;
                font-size: 18px; font-weight: bold;
                text-shadow: 0px -1px 1px rgba(0, 0, 0, 0.6);
                border-bottom: 1px solid #2d3e52;
                -webkit-box-shadow: 0px 1px 4px rgba(0,0,0,0.4);
                z-index: 1000;
            }
            #chat-container { padding: 54px 10px 60px 10px; overflow-y: auto; }
            .bubble {
                max-width: 85%; padding: 8px 12px; margin-bottom: 10px;
                border-radius: 14px; font-size: 14px; line-height: 1.35; word-wrap: break-word;
            }
            .user {
                float: right; clear: both;
                background: -webkit-linear-gradient(top, #0084ff 0%, #006bde 100%);
                color: #ffffff; border: 1px solid #0056b3;
                text-shadow: 0px -1px 1px #003d80;
            }
            .ai {
                float: left; clear: both;
                background: -webkit-linear-gradient(top, #ffffff 0%, #e5e5ea 100%);
                color: #000000; border: 1px solid #b8b8b8;
            }
            .input-area {
                position: fixed; bottom: 0; left: 0; right: 0; height: 48px;
                background: -webkit-linear-gradient(top, #ccd5e0 0%, #a0b0c0 100%);
                padding: 7px 4px; border-top: 1px solid #6f8299;
                -webkit-box-shadow: 0px -1px 3px rgba(0,0,0,0.2);
            }
            select.model-select {
                width: 28%; height: 32px; font-size: 10px; font-weight: bold;
                color: #333; background: #f7f7f7; border: 1px solid #888;
                border-radius: 10px; outline: none; padding: 2px;
            }
            input.legacy-input {
                width: 38%; height: 32px; padding: 4px 8px; font-size: 13px;
                border-radius: 14px; border: 1px solid #888; outline: none;
            }
            .mic-btn {
                width: 12%; height: 32px; font-size: 14px; color: #333;
                background: -webkit-linear-gradient(top, #ffffff 0%, #d0d0d0 100%);
                border: 1px solid #777; border-radius: 14px; outline: none;
            }
            .mic-btn.recording {
                background: -webkit-linear-gradient(top, #ff3b30 0%, #cc2b23 100%);
                color: #ffffff; border: 1px solid #aa110a;
            }
            button.send-btn {
                width: 18%; height: 32px; float: right; font-size: 13px; font-weight: bold; color: #ffffff;
                background: -webkit-linear-gradient(top, #4cd964 0%, #2db844 100%);
                border: 1px solid #1e872d; border-radius: 14px;
            }
        </style>
    </head>
    <body>

        <div id="legacy-container">
            <div class="header">iChat AI</div>
            
            <div id="chat-container">
                <div class="bubble ai markdown-content">Hello! Pick a model below to start chatting.</div>
            </div>
            
            <div class="input-area">
                <select id="modelSelect" class="model-select">
                    <option value="groq-llama-3.1" selected>Groq (Llama 3.1 8B)</option>
                    <option value="groq-llama-3.3">Groq (Llama 3.3 70B)</option>
                    <option value="or-gemma-2">OpenRouter (Gemma 2 9B)</option>
                    <option value="groq-gpt-oss">Groq (GPT OSS 20B)</option>
                    <option value="or-nemotron">OpenRouter (Nemotron Free)</option>
                    <option value="or-qwen-coder">OpenRouter (Qwen Coder Free)</option>
                </select>
                <input type="text" id="userInput" class="legacy-input" placeholder="Message">
                <button type="button" id="micBtn" class="mic-btn" onclick="toggleDictation()">🎙️</button>
                <button type="button" class="send-btn" onclick="sendMessage()">Send</button>
            </div>
        </div>

        <div id="app" style="display: none;">
            <div class="view view-main">
                <div class="page">
                    <div class="navbar">
                        <div class="navbar-bg"></div>
                        <div class="navbar-inner">
                            <div class="title">iChat AI</div>
                            <div class="right">
                                <select id="modelSelectModern" style="font-size: 11px; padding: 4px; border-radius: 8px;">
                                    <option value="groq-llama-3.1" selected>Llama 3.1 8B</option>
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
                            <a class="link icon-only" id="micBtnModern" onclick="toggleDictation()">
                                <i class="f7-icons">mic_fill</i>
                            </a>
                            <div class="messagebar-area">
                                <textarea id="userInputModern" placeholder="Message"></textarea>
                            </div>
                            <a class="link icon-only" onclick="sendMessage()">
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
            var converter = new showdown.Converter({ 
                simpleLineBreaks: true,
                strikethrough: true,
                tables: true
            });

            // Toggle Layout Based on Detected iOS Version
            document.addEventListener("DOMContentLoaded", function() {
                var legacyView = document.getElementById('legacy-container');
                var modernView = document.getElementById('app');

                if (window.isModernUI) {
                    if (legacyView) legacyView.style.display = 'none';
                    if (modernView) modernView.style.display = 'block';
                } else {
                    if (legacyView) legacyView.style.display = 'block';
                    if (modernView) modernView.style.display = 'none';
                }
            });

            // Web Speech API Voice Dictation Logic
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
                    var micBtnModern = document.getElementById("micBtnModern");
                    if (micBtn) {
                        micBtn.className = "mic-btn recording";
                        micBtn.innerText = "🛑";
                    }
                    if (micBtnModern) {
                        micBtnModern.style.color = "#ff3b30";
                    }
                };

                recognition.onresult = function(event) {
                    var transcript = "";
                    for (var i = event.resultIndex; i < event.results.length; ++i) {
                        transcript += event.results[i][0].transcript;
                    }
                    var input = window.isModernUI ? document.getElementById("userInputModern") : document.getElementById("userInput");
                    if (input) input.value = transcript;
                };

                recognition.onerror = function() { stopDictation(); };
                recognition.onend = function() { stopDictation(); };
            }

            function toggleDictation() {
                if (!recognition) {
                    alert("Voice dictation is not supported on this device/browser.");
                    return;
                }
                if (isRecording) { recognition.stop(); } else { recognition.start(); }
            }

            function stopDictation() {
                isRecording = false;
                var micBtn = document.getElementById("micBtn");
                var micBtnModern = document.getElementById("micBtnModern");
                if (micBtn) {
                    micBtn.className = "mic-btn";
                    micBtn.innerText = "🎙️";
                }
                if (micBtnModern) {
                    micBtnModern.style.color = "";
                }
            }

            // Universal Messaging Logic
            function sendMessage() {
                if (isRecording && recognition) { recognition.stop(); }

                var inputElem = window.isModernUI ? document.getElementById("userInputModern") : document.getElementById("userInput");
                var modelElem = window.isModernUI ? document.getElementById("modelSelectModern") : document.getElementById("modelSelect");

                var text = inputElem.value;
                if (!text || text.trim() === "") return;

                var selectedModel = modelElem.value;
                inputElem.value = "";

                if (window.isModernUI && window.f7Messages) {
                    window.f7Messages.addMessage({ text: text, type: 'sent' });
                } else {
                    var container = document.getElementById("chat-container");
                    var userDiv = document.createElement("div");
                    userDiv.className = "bubble user";
                    userDiv.innerText = text;
                    container.appendChild(userDiv);
                    window.scrollTo(0, document.body.scrollHeight);
                }

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

                        if (window.isModernUI && window.f7Messages) {
                            window.f7Messages.addMessage({
                                text: '<div class="markdown-content">' + formattedHTML + '</div>',
                                type: 'received'
                            });
                        } else {
                            var container = document.getElementById("chat-container");
                            var aiDiv = document.createElement("div");
                            aiDiv.className = "bubble ai markdown-content";
                            aiDiv.innerHTML = formattedHTML;
                            container.appendChild(aiDiv);
                            window.scrollTo(0, document.body.scrollHeight);
                        }
                    }
                };

                xhr.send(JSON.stringify({
                    model: selectedModel,
                    messages: [{role: "user", content: text}]
                }));
            }
        </script>
    </body>
    </html>
    """


@app.route("/v1/chat/completions", methods=["POST"])
@app.route("/chat/completions", methods=["POST"])
def chat():
    data = request.get_json(silent=True) or {}
    messages = data.get("messages", [{"role": "user", "content": "Hello"}])
    selected_model = data.get("model", "groq-llama-3.1")

    res = None

    if selected_model == "or-gemma-2":
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
            "qwen/qwen-2.5-coder-32b-instruct:free", messages
        )
    else:
        res = call_groq("llama-3.1-8b-instant", messages) or call_openrouter(
            "openrouter/auto", messages
        )

    if res:
        return jsonify(res), 200
    else:
        return jsonify(
            {
                "error": {
                    "message": "All API provider calls failed. Check key environment variables."
                }
            }
        ), 500


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
