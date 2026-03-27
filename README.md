# 🤖 Proactive WhatsApp AI Agent

A multi-agent AI assistant built for WhatsApp that doesn't just answer questions—it actively manages your schedule and pushes real-time reminders to your phone. 

## 🌟 Features
* **Multi-Agent Routing:** Uses LangGraph to dynamically route user questions to the correct tool.
* **Lightning Fast:** Powered by LLaMA-3 (70B) on Groq hardware for near-instant inference.
* **Proactive Reminders:** An internal background scheduler (`APScheduler`) constantly monitors your calendar and uses Twilio's Outbound API to push notifications when an event triggers.
* **Live Tools:** Integrates with OpenWeatherMap, Yahoo Finance (`yfinance`), and NewsAPI for real-time data.

## 🛠️ Tech Stack
* **AI Framework:** LangGraph / LangChain
* **LLM:** LLaMA-3.3-70B-Versatile via Groq
* **Backend:** Python / Flask
* **Communication:** Twilio Sandbox for WhatsApp
* **Job Scheduling:** APScheduler

## 🚀 How to Run Locally

1. **Clone the repository:**
   ```bash
   git clone [https://github.com/YOUR_USERNAME/whatsapp-ai-agent.git](https://github.com/YOUR_USERNAME/whatsapp-ai-agent.git)
   cd whatsapp-ai-agent
2.
