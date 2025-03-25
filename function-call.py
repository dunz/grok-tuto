import json

from pydantic import BaseModel, Field
from typing import Literal

import os
from dotenv import load_dotenv
from openai import OpenAI

# .env 파일 로드
load_dotenv()
XAI_API_KEY = os.getenv("XAI_API_KEY")

# ============================================ tool 선언 부 ============================================ # 
# 함수 및 파라미터 정의
class TemperatureRequest(BaseModel):
    location: str = Field(description="The city and state, e.g. San Francisco, CA")
    unit: Literal["celsius", "fahrenheit"] = Field(
        "fahrenheit", description="Temperature unit"
    )

class CeilingRequest(BaseModel):
    location: str = Field(description="The city and state, e.g. San Francisco, CA")

def get_current_temperature(**kwargs):
    request = TemperatureRequest(**kwargs)
    temperature: int
    if request.unit.lower() == "fahrenheit":
        temperature = 59
    elif request.unit.lower() == "celsius":
        temperature = 15
    else:
        raise ValueError("unit must be one of fahrenheit or celsius")
    return {
        "location": request.location,
        "temperature": temperature,
        "unit": request.unit.lower(),
    }

def get_current_ceiling(**kwargs):
    request = CeilingRequest(**kwargs)
    return {
        "location": request.location,
        "ceiling": 15000,
        "ceiling_type": "broken",
        "unit": "ft",
    }


# JSON 스키마 생성
get_current_temperature_schema = TemperatureRequest.model_json_schema()
get_current_ceiling_schema = CeilingRequest.model_json_schema()

# Pydantic JSON 스키마를 사용한 매개변수 정의
tools_definition = [
    {
        "type": "function",
        "function": {
            "name": "get_current_temperature",
            "description": "Get the current temperature in a given location",
            "parameters": get_current_temperature_schema,
        },
    },
    {
        "type": "function",
        "function": {
            "name": "get_current_ceiling",
            "description": "Get the current cloud ceiling in a given location",
            "parameters": get_current_ceiling_schema,
        },
    },
]

tools_map = {
    "get_current_temperature": get_current_temperature,
    "get_current_ceiling": get_current_ceiling,
}


# ============================================ 메시지 전송 부 ============================================ #

client = OpenAI(
    api_key=XAI_API_KEY,
    base_url="https://api.x.ai/v1",
)

messages = [{"role": "user", "content": "What's the temperature like in San Francisco?"}]
response = client.chat.completions.create(
    model="grok-2-latest",
    messages=messages,
    tools=tools_definition,  # The dictionary of our functions and their parameters
    tool_choice="auto",
)

# tool_calls가 포함된 응답을 확인할 수 있다
# print(response.choices[0].message)

# ============================================ 추가 메시지 전송 부 ============================================ #

# 도구 호출을 포함한 보조 메시지를 메시지에 추가한다
messages.append(response.choices[0].message)

# 응답 본문에 도구 호출이 있는지 확인한다
# 또한 이것을 함수로 감싸서 코드를 더 깔끔하게 만들 수도 있다

if response.choices[0].message.tool_calls:
    for tool_call in response.choices[0].message.tool_calls:

        # Grok이 호출하려는 도구 함수 이름과 인수를 가져온다
        function_name = tool_call.function.name
        function_args = json.loads(tool_call.function.arguments)

        # 이전에 정의한 도구 함수 중 하나를 인수와 함께 호출한다
        result = tools_map[function_name](**function_args)

        # 도구 함수 호출의 결과를 채팅 메시지 기록에 추가한다
        # with "role": "tool"
        messages.append(
            {
                "role": "tool",
                "content": json.dumps(result),
                "tool_call_id": tool_call.id  # Grok의 응답에 제공된 tool_call.id
            }
        )

response = client.chat.completions.create(
    model="grok-2-latest",
    messages=messages,
    tools=tools_definition,
    tool_choice="auto"
)

print('history:: ', messages)
print(response.choices[0].message)
