# 📱 WhatsApp AI Multi-Agent

An intelligent, multi-agent AI system integrated directly with WhatsApp. This project leverages Python to create conversational agents capable of handling complex queries, automating tasks, and providing dynamic responses through the WhatsApp interface.

---

## ✨ Features

* **Multi-Agent Architecture:** Routes different types of user queries to specialized AI agents.
* **WhatsApp Integration:** Seamless communication via WhatsApp API.
* **Context-Aware Conversations:** Maintains chat memory for natural, ongoing dialogue.
* **Secure Configuration:** Environment variables securely manage sensitive API keys.

---

## 🛠️ Prerequisites

Before you begin, ensure you have the following installed:
* Python 3.8 or higher
* A WhatsApp Business API account 
* Required AI/LLM API keys (e.g., OpenAI)

---

## 🚀 Installation & Setup

**1. Clone the repository**
git clone https://github.com/sahaja-msls/whatsapp_multi-agent.git
cd whatsapp_multi-agent

**2. Create a virtual environment**
python -m venv venv
venv\Scripts\activate

**3. Install dependencies**
pip install -r requirements.txt

**4. Set up environment variables**
Create a `.env` file in the root directory. Add your necessary API keys and tokens:

WHATSAPP_API_KEY=your_whatsapp_token_here
WHATSAPP_PHONE_NUMBER_ID=your_phone_number_id
OPENAI_API_KEY=your_openai_api_key_here

*(Note: The `.env` file is intentionally ignored by Git to keep your credentials secure.)*

---

## 💻 Usage

Start the main application server:

python app.py

Once the server is running, expose your local server to the internet (using a tool like ngrok) so WhatsApp can send webhooks to your application.


