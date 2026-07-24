import os
import requests
from flask import Flask, jsonify, request

app = Flask(__name__)

OPENROUTER_API_KEY = os.environ.get("OPENROUTER_API_KEY", "")
GROQ_API_KEY = os.environ.get("GROQ_API_KEY", "")


@app.route("/", methods=["GET"])
def home():
    return """
    <!DOCTYPE html>
    <html>
    <head>
        <meta name="viewport" content="width=device-width, initial-scale=1.0, maximum-scale=1.0, user-scalable=no">
        <title>iChat AI</title>
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
                font-size: 15px;
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
            /* Code box styling for Markdown blocks */
            pre {
                background: #222222;
                color: #00ff66;
                padding: 8px;
                font-family: Courier, monospace;
                font-size: 12px;
                overflow-x: auto;
                -webkit-border-radius: 6px;
                border-radius: 6px;
                margin: 6px 0;
                white-space: pre-wrap;
            }
            code {
                background: rgba(0,0,0,0.08);
                padding: 1px 4px;
                font-family: Courier, monospace;
                font-size: 13px;
                -webkit-border-radius: 4px;
                border-radius: 4px;
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
                width: 32%;
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
            }
            input[type="text"] {
                width: 46%;
                height: 32px;
                padding: 4px 8px;
                font-size: 13px;
                -webkit-border-radius: 14px;
                border-radius: 14px;
                border: 1px solid #888;
                outline: none;
                -webkit-box-shadow: inset 0px 1px 2px rgba(0,0,0,0.3);
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
            }
        </style>
    </head>
    <body>
        <div class="header">iChat AI</div>
        
        <div id="chat-container">
            <div class="bubble ai">Hello! Ready to chat using Groq Instant.</div>
        </div>
        
        <div class="input-area">
            <select id="modelSelect">
                <option value="groq-llama-3.1" selected>Groq (Instant)</option>
                <option value="groq-llama-3.3">Groq (3.3 70B)</option>
                <option value="openrouter">OpenRouter Free</option>
            </select>
            <input type="text" id="userInput" placeholder="Message">
            <button onclick="sendMessage()">Send</button>
        </div>

        <script>
            // Simple iOS 6-compatible Markdown Parser
            function parseMarkdown(text) {
                if (!text) return "";

                // 1. Convert ```code blocks``` into <pre> tags
                text = text.replace(/```([\s\S]*?)```/g, "<pre>$1</pre>");

                // 2. Convert `inline code` into <code> tags
                text = text.replace(/`([^`]+)`/g, "<code>$1</code>");

                // 3. Convert **bold** into <b>
                text = text.replace(/\*\*(.*?)\*\*/g, "<b>$1</b>");

                // 4. Convert *italic* into <i>
                text = text.replace(/\*(.*?)\*/g, "<i>$1</i>");

                // 5. Convert numbered lists (1. Item)
                text = text.replace(/^(\d+)\.\s+(.*)$/gm, "<br><b>$1.</b> $2");

                // 6. Convert bullet lists (* Item or - Item)
                text = text.replace(/^[\*\-]\s+(.*)$/gm, "<br>&bull; $1");

                // 7. Line breaks
                text = text.replace(/\n/g, "<br>");

                return text;
            }

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
                                aiDiv.innerHTML = parseMarkdown(rawContent);
                            } catch (e) {
                                aiDiv.innerText = "Error parsing response.";
                            }
                        } else {
                            aiDiv.innerText = "Error: " + xhr.status + " - " + xhr.responseText;
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
    </html>
    """


@app.route("/v1/chat/completions", methods=["POST"])
@app.route("/chat/completions", methods=["POST"])
def chat():
    data = request.get_json(silent=True) or {}
    messages = data.get("messages", [{"role": "user", "content": "Hello"}])
    selected_model = data.get("model", "groq-llama-3.1")

    def call_groq(model_id="llama-3.1-8b-instant"):
        if not GROQ_API_KEY:
            return None
        payload = {"model": model_id, "messages": messages}
        headers = {
            "Authorization": f"Bearer {GROQ_API_KEY}",
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

    def call_openrouter():
        if not OPENROUTER_API_KEY:
            return None
        payload = {"model": "openrouter/free", "messages": messages}
        headers = {
            "Authorization": f"Bearer {OPENROUTER_API_KEY}",
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

    res = None

    if selected_model == "groq-llama-3.3":
        res = call_groq("llama-3.3-70b-versatile") or call_openrouter()
    elif selected_model == "openrouter":
        res = call_openrouter() or call_groq("llama-3.1-8b-instant")
    else:
        # Default: Instant Llama 3.1
        res = call_groq("llama-3.1-8b-instant") or call_openrouter()

    if res:
        return jsonify(res), 200
    else:
        return jsonify(
            {
                "error": {
                    "message": "All providers failed or rate limits reached. Please try again in a minute."
                }
            }
        ), 500


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
