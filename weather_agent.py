import json
from groq import Groq
client = Groq(api_key='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')
import requests

def get_weather(loc, api_key='7fb83a6f3a260a61d5dc0966dcc34acf'):
    # Base URL for OpenWeatherMap Current Weather Data
    base_url = "http://api.openweathermap.org/data/2.5/weather"
    
    # Parameters for the API call
    params = {
        'q': loc,
        'appid': api_key,
        'units': 'metric'  # Use 'imperial' for Fahrenheit
    }

    try:
        response = requests.get(base_url, params=params)
        print(response)
        response.raise_for_status()  # Check for HTTP errors
        
        data = response.json()
        print(data)
        
        # Extract specific details
        temp = data['main']['temp']
        description = data['weather'][0]['description']
        humidity = data['main']['humidity']
        feels_like=data['main']['feels_like']

        
        return json.dumps(data)
    except requests.exceptions.HTTPError:
        print("Error: City not found or invalid API key.")
        return json.dumps({"loc":loc,"temp":"not found","description":"not found","humidity":"not found"}) 
    except Exception as e:
        print(f"An error occurred: {e}")


tools=[{
    "type": "function",
    "function": {
        "name": "get_weather",
        "description": "get weather for a given location",
        "parameters": {
            "type": "object",
            "properties": {
                "loc": {"type": "string", "description": "location"}
            },
            "required": ["loc"]
        }
    }
}]

def weather_agent(user_query:str):
    messages=[{'role':'system','content':'you are a weather assistant,you should give it shortly and if you not found the specific location just return i\'ve not found the location or weather,dont give xml format'},{'role':'user','content':user_query}]
    response=client.chat.completions.create(model="llama-3.3-70b-versatile",messages=messages,tools=tools,tool_choice="auto")
    response_message=response.choices[0].message
    tool_calls=response_message.tool_calls
    if tool_calls:
        messages.append(response_message)
        for tool_call in tool_calls:
            function_name=tool_call.function.name
            function_args=json.loads(tool_call.function.arguments)
            if function_name == 'get_weather':
                print("callind the get_weather function")
                function_response=get_weather(loc=function_args.get('loc'))
                print(function_response)
                messages.append({'role':'tool','tool_call_id':tool_call.id,'name':function_name,'content':function_response})
        second_response=client.chat.completions.create(model='llama-3.3-70b-versatile',messages=messages)
        response2_message=second_response.choices[0].message.content
        return response2_message
    else:
        return f'{response_message.content}'
if __name__=='__main__':
    weather_agent('what is the weather in guntur?')
    weather_agent('what is meant by weather')