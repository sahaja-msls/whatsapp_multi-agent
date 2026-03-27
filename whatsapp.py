import os
import yfinance as yf
import requests
from flask import Flask, request
from twilio.twiml.messaging_response import MessagingResponse
from langchain_core.tools import Tool
from langgraph.prebuilt import create_react_agent

# --- NEW GROQ IMPORT ---
from langchain_groq import ChatGroq

app = Flask(__name__)
# --- SET YOUR API KEYS HERE ---
os.environ["GROQ_API_KEY"] = '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'
WEATHER_API_KEY = '7fb83a6f3a260a61d5dc0966dcc34acf'
NEWS_API_KEY = '69d9f64dbf464b288de6c2404e432173'

# ==========================================
# AGENT TOOLS (The specific skills)
# ==========================================

def get_weather(location):
    url = f"http://api.openweathermap.org/data/2.5/weather?q={location}&appid={WEATHER_API_KEY}&units=metric"
    try:
        res = requests.get(url).json()
        return f"Weather in {location}: {res['weather'][0]['description'].title()}, {res['main']['temp']}°C"
    except Exception:
        return f"Could not fetch weather for {location}."

def get_stock(ticker):
    try:
        stock = yf.Ticker(ticker.strip().upper())
        # Get the last closing price
        price = stock.history(period="1d")['Close'].iloc[-1]
        return f"Current price of {ticker.upper()}: ${price:.2f}"
    except Exception:
        return f"Could not fetch stock price for {ticker}."

def get_news(topic):
    # Defaulting to US top headlines for testing
    url = f"https://newsapi.org/v2/top-headlines?country=us&apiKey={NEWS_API_KEY}"
    try:
        res = requests.get(url).json()
        articles = [article['title'] for article in res.get('articles', [])[:3]]
        return "Here is the latest news:\n- " + "\n- ".join(articles)
    except Exception:
        return "Could not fetch the local news."

# In-memory dictionary for To-Do/Calendar testing
memory_db = {"todo": [], "calendar": []}

def manage_tasks(command):
    """Handles To-Do and Calendar commands. Example inputs: 'add todo: buy milk', 'list calendar'"""
    try:
        parts = command.lower().split(":")
        action_type = parts[0].strip() 
        
        if "list todo" in action_type:
            return "To-Do List:\n" + "\n".join(memory_db["todo"]) if memory_db["todo"] else "Your To-Do list is empty."
            
        elif "add todo" in action_type:
            item = parts[1].strip()
            memory_db["todo"].append(item)
            return f"Added '{item}' to your To-Do list."
            
        elif "list calendar" in action_type:
             return "Calendar Events:\n" + "\n".join(memory_db["calendar"]) if memory_db["calendar"] else "No events scheduled."
             
        elif "add calendar" in action_type:
            event = parts[1].strip()
            memory_db["calendar"].append(event)
            return f"Added '{event}' to your Calendar."
            
        return "Invalid command. Use format like 'add todo: task' or 'list calendar'."
    except Exception:
        return "Error managing tasks. Please check your command format."

# ==========================================
# MULTI-AGENT SETUP 
# ==========================================

tools = [
    Tool(
        name="WeatherTool",
        func=get_weather,
        description="Useful for getting current weather updates. Input should be a city name."
    ),
    Tool(
        name="StockTool",
        func=get_stock,
        description="Useful for getting stock prices. Input should be a stock ticker symbol (e.g., AAPL, TSLA)."
    ),
    Tool(
        name="NewsTool",
        func=get_news,
        description="Useful for getting current local or world news headlines. Input can be 'latest'."
    ),
    Tool(
        name="TaskManagerTool",
        func=manage_tasks,
        description="Manages to-do lists and calendar events. Input formats: 'add todo: [task]', 'list todo', 'add calendar: [event details]', 'list calendar'."
    )
]

# --- INITIALIZE GROQ INSTEAD OF GEMINI ---
llm = ChatGroq(model="llama-3.3-70b-versatile", temperature=0)

# Create the agent
agent = create_react_agent(llm, tools=tools)

# ==========================================
# WHATSAPP WEBHOOK (Flask Server)
# ==========================================

@app.route("/whatsapp", methods=["POST"])
def whatsapp_reply():
    incoming_msg = request.values.get("Body", "").strip()
    
    try:
        response = agent.invoke({"messages": [("human", incoming_msg)]})
        response_text = response["messages"][-1].content
    except Exception as e:
        print(f"Agent Error: {e}")
        response_text = "I'm sorry, my systems encountered an error processing that request."

    resp = MessagingResponse()
    msg = resp.message()
    msg.body(response_text)
    
    return str(resp)

if __name__ == "__main__":
    app.run(port=5000, debug=True)