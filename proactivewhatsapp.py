import os
import requests
import yfinance as yf
from datetime import datetime
from flask import Flask, request
from twilio.twiml.messaging_response import MessagingResponse
from twilio.rest import Client
from apscheduler.schedulers.background import BackgroundScheduler
from langchain_core.tools import tool
from langgraph.prebuilt import create_react_agent
from langchain_groq import ChatGroq
from dotenv import load_dotenv
load_dotenv() 

app = Flask(__name__)

GROQ_API_KEY = os.getenv("GROQ_API_KEY")
WEATHER_API_KEY = os.getenv("WEATHER_API_KEY")
NEWS_API_KEY = os.getenv("NEWS_API_KEY")
TWILIO_SID = os.getenv("TWILIO_SID")
TWILIO_AUTH_TOKEN = os.getenv("TWILIO_AUTH_TOKEN")
TWILIO_NUMBER = os.getenv("TWILIO_NUMBER")
YOUR_PHONE_NUMBER = os.getenv("YOUR_PHONE_NUMBER")

twilio_client = Client(TWILIO_SID, TWILIO_AUTH_TOKEN)

# ==========================================
# 2. UPGRADED MEMORY (Now with time!)
# ==========================================
# Calendar now stores dictionaries so we can track exact times
memory_db = {"todo": [], "calendar": []}

# ==========================================
# 3. AGENT TOOLS
# ==========================================
# ==========================================
# 3. AGENT TOOLS (Upgraded with @tool decorator)
# ==========================================

@tool
def get_weather(location: str) -> str:
    """Useful for getting current weather updates. Input MUST be the city name as a string."""
    url = f"http://api.openweathermap.org/data/2.5/weather?q={location}&appid={WEATHER_API_KEY}&units=metric"
    try:
        res = requests.get(url).json()
        return f"Weather in {location}: {res['weather'][0]['description'].title()}, {res['main']['temp']}°C"
    except Exception:
        return f"Could not fetch weather for {location}."

@tool
def get_stock(ticker: str) -> str:
    """Useful for getting stock prices. Input should be a stock ticker symbol. 
    IMPORTANT: For Indian stocks, you MUST append '.NS' (e.g., RELIANCE.NS, BPCL.NS, INFY.NS)."""
    try:
        price = yf.Ticker(ticker.strip().upper()).history(period="1d")['Close'].iloc[-1]
        return f"Current price of {ticker.upper()}: ${price:.2f}"
    except Exception:
        return f"Could not fetch stock price for {ticker}. Check if the ticker symbol is correct."

@tool
def manage_tasks(command: str) -> str:
    """Manages to-do lists and calendar events. Input formats MUST be exactly: 'add todo: [task]', 'list todo', 'list calendar', or 'add calendar: YYYY-MM-DD HH:MM | [event]'"""
    try:
        parts = command.lower().split(":", 1)
        action_type = parts[0].strip()
        
        if "list todo" in action_type:
            return "To-Do:\n" + "\n".join(memory_db["todo"]) if memory_db["todo"] else "To-Do list is empty."
            
        elif "add todo" in action_type:
            item = parts[1].strip()
            memory_db["todo"].append(item)
            return f"Added '{item}' to To-Do list."
            
        elif "list calendar" in action_type:
            events = [f"{e['time']} - {e['event']}" for e in memory_db["calendar"]]
            return "Calendar:\n" + "\n".join(events) if events else "No events scheduled."
             
        elif "add calendar" in action_type:
            time_str, event_desc = parts[1].split("|")
            memory_db["calendar"].append({
                "time": time_str.strip(),
                "event": event_desc.strip(),
                "notified": False
            })
            return f"Added '{event_desc.strip()}' for {time_str.strip()}."
            
        return "Command failed. Use the exact formats provided."
    except Exception as e:
        return f"Error managing tasks. Did you use the right format?"

# We group the tools into a list like this now
tools = [get_weather, get_stock, manage_tasks]
# Initialize Groq Brain
# Initialize Groq Brain (Using LLaMA 3.3 70B Versatile for high reliability)
llm = ChatGroq(api_key=GROQ_API_KEY,model="llama-3.3-70b-versatile", temperature=0)

# Strict system instructions to prevent tool hallucinations
system_prompt = """You are a helpful WhatsApp assistant. You have specific tools for Weather, Stocks, and Tasks. 
NEVER attempt to use tools that are not explicitly provided to you (like brave_search or web_search). 
If a tool fails, tell the user gracefully."""

agent = create_react_agent(llm, tools=tools)

# ==========================================
# 4. THE ALARM CLOCK (Background Scheduler)
# ==========================================
def check_calendar():
    """This function runs silently in the background every 60 seconds."""
    now_str = datetime.now().strftime("%Y-%m-%d %H:%M")
    
    for item in memory_db["calendar"]:
        # If the time matches right now, and we haven't alerted you yet
        if item["time"] == now_str and not item["notified"]:
            
            # THE MEGAPHONE: Push a WhatsApp message to your phone
            alert_message = f"🚨 *CALENDAR REMINDER* 🚨\n\nIt's time for: {item['event']}"
            twilio_client.messages.create(
                from_=TWILIO_NUMBER,
                body=alert_message,
                to=YOUR_PHONE_NUMBER
            )
            
            # Mark as notified so it doesn't alert you again
            item["notified"] = True
            print(f"Notification sent for: {item['event']}")

# Start the ticking clock
scheduler = BackgroundScheduler()
scheduler.add_job(func=check_calendar, trigger="interval", seconds=60)
scheduler.start()

# ==========================================
# 5. WHATSAPP WEBHOOK (Listening for incoming)
# ==========================================
@app.route("/whatsapp", methods=["POST"])
def whatsapp_reply():
    incoming_msg = request.values.get("Body", "").strip()
    
    try:
        # Combine strict rules with the real-time clock
        system_instructions = (
            f"You are a helpful WhatsApp assistant. You have specific tools for Weather, Stocks, and Tasks. "
            f"NEVER attempt to use tools that are not explicitly provided to you (like brave_search or web_search). "
            f"If a tool fails, tell the user gracefully. "
            f"The current date and time is {datetime.now().strftime('%Y-%m-%d %H:%M')}."
        )
        
        # Feed the instructions and the user's message to the agent
        response = agent.invoke({"messages": [("system", system_instructions), ("human", incoming_msg)]})
        response_text = response["messages"][-1].content
    except Exception as e:
        print(f"Agent Error: {e}")
        response_text = "Error processing request."

    resp = MessagingResponse()
    resp.message().body(response_text)
    return str(resp)

# IMPORTANT: Shut down the scheduler cleanly if you kill the server
import atexit
atexit.register(lambda: scheduler.shutdown())

if __name__ == "__main__":
    app.run(port=5000, debug=True, use_reloader=False) 
    # use_reloader=False prevents the background clock from running twice


