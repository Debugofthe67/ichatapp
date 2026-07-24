# iChatApp

iChatApp is a lightweight web client and native iOS application designed to bring modern AI chat capabilities to legacy iOS devices (such as iOS 6) as well as modern browsers. It features an iOS 6-style UI, Markdown rendering support, multi-model AI routing through Groq and OpenRouter, and web-based voice dictation.

---

## Features

* **Legacy iOS Aesthetics:** Styled with classic iOS 6 glassmorphism headers, gradient chat bubbles, and native-feeling UI elements.
* **Standalone Web App:** Configured with iOS meta tags (`apple-mobile-web-app-capable`) and tap interceptors to hide Safari browser Chrome when added to the Home Screen.
* **Markdown Support:** Integrates Showdown.js to parse AI responses into formatted HTML (code blocks, bold text, lists, and tables).
* **Multi-Model Routing:** Proxy server dynamically routes requests between Groq and OpenRouter key pools.
* **Voice Dictation:** Web Speech API integration allows hands-free voice input directly into the message bar.
* **Native Cydia Package Setup:** Includes setup configuration and compilation scripts for building a native `.deb` package via Theos.

---

## Architecture Overview

1. **Frontend:** HTML/CSS/JS served directly via Flask. Works as a PWA/WebClip on iOS devices or as a native Objective-C UIKit view built with Theos.
2. **Backend Proxy (`proxy.py`):** Flask application hosted on Render. Handles CORS, manages API key rotation pools, and normalizes chat completion endpoints (`/v1/chat/completions`).
3. **AI Providers:**
   * **Groq:** Llama 3.1 8B Instant, Llama 3.3 70B Versatile, GPT OSS 20B.
   * **OpenRouter:** Gemma 2 9B, Nemotron, Qwen Coder.

---

## File Structure

```text
ichatapp/
├── proxy.py              # Flask proxy backend & inline web app
├── static/
│   └── icon.png          # App icon for WebClips and standalone app
