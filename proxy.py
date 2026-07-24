import os
import requests
from flask import Flask, jsonify, request

app = Flask(__name__)

OPENROUTER_API_KEY = os.environ.get("OPENROUTER_API_KEY", "")


@app.route("/", methods=["GET"])
def home():
    return """
    <!DOCTYPE html>
    <html>
    <head>
        <meta name="viewport" content="width=device-width, initial-scale=1.0, maximum-scale=1.0, user-scalable=no">
        <title>iChat</title>
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
                /* iOS 6 linen/stripes background vibe */
                background-image: -webkit-linear-gradient(left, #c8d2dc 50%, #d8e0e8 50%);
                background-size: 4px 100%;
            }
            .header {
                position: fixed;
                top: 0;
                left: 0;
                right: 0;
                height: 44px;
                /* Legacy WebKit linear gradient */
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
                max-width: 80%;
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
            .input-area {
                position: fixed;
                bottom: 0;
                left: 0;
                right: 0;
                height: 48px;
                background: -webkit-gradient(linear, left top, left bottom, from(#ccd5e0), to(#a0b0c0));
                background: -webkit-linear-gradient(top, #ccd5e0 0%, #a0b0c0 100%);
                padding: 7px;
                border-top: 1px solid #6f8299;
                -webkit-box-shadow: 0px -1px 3px rgba(0,0,0,0.2);
            }
            input[type="text"] {
                width: 74%;
                height: 32px;
                padding: 4px 10px;
                font-size: 14px;
                -webkit-border-radius: 16px;
                border-radius: 16px;
                border: 1px solid #888;
                outline: none;
                -webkit-box-shadow: inset 0px 1px 2px rgba(0,0,0,0.3);
            }
            button {
                width: 23%;
                height: 32px;
                float: right;
                font-size: 14px;
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
            <div class="bubble ai">Hello! Ready to chat.</div>
        </div>
        
        <div class="input-area">
            <input type="text" id="userInput" placeholder="Text Message">
            <button onclick="sendMessage()">Send</button>
        </div>

        <script>
            function sendMessage() {
                var input = document.getElementById("userInput");
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
                                aiDiv.innerText = res.choices[0].message.content;
                            } catch (e) {
                                aiDiv.innerText = "Error parsing response.";
                            }
                        } else {
                            aiDiv.innerText = "Server error (" + xhr.status + ").";
                        }
                        
                        container.appendChild(aiDiv);
                        window.scrollTo(0, document.body.scrollHeight);
                    }
                };

                xhr.send(JSON.stringify({
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

    headers = {
        "Authorization": "Bearer " + str(OPENROUTER_API_KEY),
        "Content-Type": "application/json",
    }

    payload = {
        "model": "openrouter/free",
        "messages": messages,
    }

    try:
        r = requests.post(
            "https://openrouter.ai/api/v1/chat/completions",
            headers=headers,
            json=payload,
            timeout=30,
        )
        return jsonify(r.json()), r.status_code
    except Exception as e:
        return jsonify({"error": str(e)}), 500


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
