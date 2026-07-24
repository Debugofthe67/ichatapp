import os
import requests
from flask import Flask, jsonify, request

app = Flask(__name__)

OPENROUTER_API_KEY = os.environ.get("OPENROUTER_API_KEY")


@app.route("/", methods=["GET"])
def home():
    return """
    <!DOCTYPE html>
    <html>
    <head>
        <meta name="viewport" content="width=device-width, initial-scale=1.0, maximum-scale=1.0, user-scalable=no">
        <title>iChat AI</title>
        <style>
            * { box-sizing: border-box; }
            body { margin: 0; padding: 0; font-family: "Helvetica Neue", Helvetica, Arial, sans-serif; background-color: #d8e0e8; }
            .header { position: fixed; top: 0; left: 0; right: 0; height: 44px; background: linear-gradient(to bottom, #b0bcc7 0%, #889bb0 50%, #6f8299 51%, #6d84a2 100%); color: white; text-align: center; line-height: 44px; font-size: 18px; font-weight: bold; text-shadow: 0px -1px 1px #333; border-bottom: 1px solid #2d3e52; z-index: 1000; }
            #chat-container { padding: 54px 10px 60px 10px; overflow-y: auto; }
            .bubble { max-width: 80%; padding: 8px 12px; margin-bottom: 10px; border-radius: 14px; font-size: 15px; line-height: 1.3; word-wrap: break-word; }
            .user { float: right; clear: both; background: linear-gradient(to bottom, #0084ff, #006bde); color: white; border: 1px solid #0056b3; }
            .ai { float: left; clear: both; background: linear-gradient(to bottom, #ffffff, #e5e5ea); color: black; border: 1px solid #cccccc; }
            .input-area { position: fixed; bottom: 0; left: 0; right: 0; height: 50px; background: linear-gradient(to bottom, #ccd5e0, #a0b0c0); padding: 8px; border-top: 1px solid #708090; }
            input[type="text"] { width: 75%; height: 32px; padding: 4px 8px; font-size: 14px; border-radius: 14px; border: 1px solid #888; outline: none; }
            button { width: 22%; height: 32px; float: right; font-size: 14px; font-weight: bold; color: white; background: linear-gradient(to bottom, #4cd964, #2db844); border: 1px solid #1e872d; border-radius: 14px; }
        </style>
    </head>
    <body>
        <div class="header">iChat AI</div>
        <div id="chat-container">
            <div class="bubble ai">Hello! Ready to chat on iOS 6.</div>
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
                            aiDiv.innerText = "Error: " + xhr.status;
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
