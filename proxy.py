import os
import random
import requests
from flask import Flask, jsonify, request

app = Flask(__name__)


# Helper function to collect all API keys from environment variables
def get_key_pool(prefix):
    keys = []
    # Check for unnumbered main key (e.g., GROQ_API_KEY)
    main_key = os.environ.get(prefix, "")
    if main_key:
        keys.append(main_key)

    # Check for numbered keys (e.g., GROQ_API_KEY_2, GROQ_API_KEY_3, etc.)
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

<!-- 2. The Single Icon Link (iOS 6 auto-scales this 114x114 PNG) -->
<link rel="apple-touch-icon" href="icon.png">
        
        <script src="https://cdnjs.cloudflare.com/ajax/libs/showdown/1.9.1/showdown.min.js"></script>

        <style>
            * {
                -webkit-box-sizing: border-box;
                box-sizing: border-box;
            }
            body {
                margin: 0;
                padding: 0;
                font-family: "Helvetica Neue", Helvetica, Arial, sans-serif;
                background-color: #d8e0e8;
                background-image: -webkit-linear-gradient(left, #c8d2dc 50%, #d8e0e8 50%);
                background-size: 4px 100%;
            }
            .header {
                position: fixed;
                top: 0;
                left: 0;
                right: 0;
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

            .ai p {
                margin: 0 0 6px 0;
            }
            .ai p:last-child {
                margin-bottom: 0;
            }
            .ai ul, .ai ol {
                margin: 4px 0 4px 20px;
                padding: 0;
            }
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
                bottom: 0;
                left: 0;
                right: 0;
                height: 48px;
                background: -webkit-gradient(linear, left top, left bottom, from(#ccd5e0), to(#a0b0c0));
                background: -webkit-linear-gradient(top, #ccd5e0 0%, #a0b0c0 100%);
                padding: 7px 5px;
                border-top: 1px solid #6f8299;
                -webkit-box-shadow: 0px -1px 3px rgba(0,0,0,0.2);
            }
            select {
                width: 34%;
                height: 32px;
                font-size: 11px;
                font-weight: bold;
                color: #333;
                background: #f7f7f7;
                border: 1px solid #888;
                -webkit-border-radius: 10px;
                border-radius: 10px;
                outline: none;
                padding: 2px;
                -webkit-tap-highlight-color: rgba(0,0,0,0);
            }
            input[type="text"] {
                width: 44%;
                height: 32px;
                padding: 4px 8px;
                font-size: 13px;
                -webkit-border-radius: 14px;
                border-radius: 14px;
                border: 1px solid #888;
                outline: none;
                -webkit-box-shadow: inset 0px 1px 2px rgba(0,0,0,0.3);
                -webkit-tap-highlight-color: rgba(0,0,0,0);
            }
            button {
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
                -webkit-tap-highlight-color: rgba(0,0,0,0);
            }
        </style>
    </head>
    <body>
        <div class="header">iChat AI</div>
        
        <div id="chat-container">
            <div class="bubble ai">Hello! Pick a model below to start chatting.</div>
        </div>
        
        <div class="input-area">
            <select id="modelSelect">
                <option value="groq-llama-3.1" selected>Groq (Llama 3.1 8B)</option>
                <option value="groq-llama-3.3">Groq (Llama 3.3 70B)</option>
                <option value="or-gemma-2">OpenRouter (Gemma 2 9B)</option>
                <option value="groq-gpt-oss">Groq (GPT OSS 20B)</option>
                <option value="or-nemotron">OpenRouter (Nemotron Free)</option>
                <option value="or-qwen-coder">OpenRouter (Qwen Coder Free)</option>
            </select>
            <input type="text" id="userInput" placeholder="Message">
            <button type="button" onclick="sendMessage()">Send</button>
        </div>

        <script>
            var converter = new showdown.Converter({
                simpleLineBreaks: true,
                strikethrough: true,
                tables: true
            });

            function sendMessage() {
                var input = document.getElementById("userInput");
                var modelSelect = document.getElementById("modelSelect");
                var text = input.value;
                if (!text || text.trim() === "") return;

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
                                aiDiv.innerHTML = converter.makeHtml(rawContent);
                            } catch (e) {
                                aiDiv.innerText = "Error parsing response.";
                            }
                        } else {
                            aiDiv.innerText = "Error " + xhr.status + ": Check Render Environment Variables.";
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
        <script type="text/javascript">
(function(document, navigator, standalone) {
    // Only apply this logic if the app is running in standalone (home screen) mode
    if ((standalone in navigator) && navigator[standalone]) {
        var curnode, location = document.location, stop = /^(a|html)$/i;
        
        document.addEventListener('click', function(e) {
            curnode = e.target;
            
            // Find the parent anchor tag if the user clicked an element inside a link
            while (!(stop).test(curnode.nodeName)) {
                curnode = curnode.parentNode;
            }
            
            // If an anchor tag was found and it has an href attribute
            if ('href' in curnode && (curnode.href.indexOf('http') || curnode.href.indexOf(location.host) !== -1)) {
                e.preventDefault();
                location.href = curnode.href;
            }
        }, false);
    }
})(document, window.navigator, 'standalone');
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
        # Default Llama 3.1 Instant
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
