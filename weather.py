import json
from groq import groq
client = Groq(api_key='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')
def get_weather(loc:str)-> str:
    """A dummy tool to simulate fetching live stock prices."""
    printf("fething the weather for the ",loc)
    weathers={
        "delhi":"25 degree and sunny",
        "mumbai":"26 degree and rainy",
        "bangalore":"27 degree and cloudy",
        "hyderabad":"28 degree and sunny",
        "chennai":"29 degree and rainy",
        "guntur":"30 degree and sunny"
    }
    return json.dumps({"loc":loc,"weather":weathers.get(loc.lower(),"weather not found")})
    tools=[{"type":"function","function":"get_weather","description":"get weather for a given location",
    "parameters":{"type":"object","properties":{"loc":{"type":"string","description":"location"}},"required":["loc"]}}]
def weather_agent(user_query:str):
    messages=[{'role':'user','content':user_query}]
    response=client.chat.completions.create(model="llama-3.3-70b-versatile",messages=messages,tools=tools,tool_choice="auto")
    response_message=response.choices[0].message
    tool_calls=response_message.tool_calls
    