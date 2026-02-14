import google.generativeai as genai
from google.generativeai.types.generation_types import StopCandidateException

import os, time, threading, pickle
from datetime import datetime
import pytz


from util.typing import Session
from iot import get_iot_status



import logging
logger = logging.getLogger(__name__)

genai.configure(api_key=os.environ["API_KEY"])

model = None          # Hold A global GenAI model
sessions_cache = {}   # Hold a session cache
last_dump_time = None

GRACEFULLY_STOP = False 

with open('./resources/system_instruction.txt') as f:
    instruction = f.read ()
    logger.debug(instruction)


# ========== Function Declaration for Smart Home Status ==========
get_smart_home_status_declaration = {
    "name": "get_smart_home_status",
    "description": "查詢智慧家居設備的即時狀態，包括溫度、門窗、動作感應、電源等資訊。支援多種查詢方式：產品型號、使用者命名、功能類型、事件類型。",
    "parameters": {
        "type_": "OBJECT",
        "properties": {
            "device_name": {
                "type_": "STRING",
                "description": "產品型號過濾（部分匹配），例如：'PST02-A'、'PAN15'、'PST02-C'"
            },
            "user_name": {
                "type_": "STRING",
                "description": "使用者自訂名稱過濾（部分匹配），例如：'五樓'、'客廳'、'大門' - 這是最常用的查詢方式！"
            },
            "device_type": {
                "type_": "STRING",
                "description": "功能類型過濾（部分匹配），例如：'Temperature Sensor'、'Door / Window Sensor'、'PIR Sensor'"
            },
            "event_type": {
                "type_": "STRING",
                "description": "事件類型過濾（部分匹配），例如：'Temperature report'、'Door/window close'、'PIR trigger'"
            }
        }
    }
}

smart_home_tool = [get_smart_home_status_declaration]


# ========== Current Time Function ==========
def get_current_time(timezone=None):
    """
    Get current date and time for a specific timezone

    Args:
        timezone: Timezone name (e.g., 'Asia/Taipei', 'America/New_York')
                 If None, uses system local time

    Returns:
        dict: Current time information
    """
    try:
        if timezone:
            tz = pytz.timezone(timezone)
            now = datetime.now(tz)
        else:
            # Use system local timezone
            now = datetime.now()

        return {
            "datetime": now.strftime("%Y-%m-%d %H:%M:%S"),
            "date": now.strftime("%Y-%m-%d"),
            "time": now.strftime("%H:%M:%S"),
            "day_of_week": now.strftime("%A"),
            "timezone": str(now.tzinfo) if now.tzinfo else "Local",
            "iso_format": now.isoformat(),
            "timestamp": int(now.timestamp())
        }
    except Exception as e:
        logger.error(f"Error getting current time: {e}")
        return {
            "error": str(e),
            "datetime": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        }


# ========== Function Declaration for Current Time ==========
get_current_time_declaration = {
    "name": "get_current_time",
    "description": "取得目前的日期和時間。可以查詢特定時區的時間，或是本地時間。",
    "parameters": {
        "type_": "OBJECT",
        "properties": {
            "timezone": {
                "type_": "STRING",
                "description": "時區名稱（選填），例如：'Asia/Taipei'（台北）、'Asia/Tokyo'（東京）、'America/New_York'（紐約）。如果不指定，使用系統本地時間。"
            }
        }
    }
}

# Combine all tools
all_tools = [get_smart_home_status_declaration, get_current_time_declaration]



def loadChatSession ():
    directory_path = 'history'
    files_and_dirs = os.listdir(directory_path)

    # 過濾出檔案
    files = [f for f in files_and_dirs]    
    logger.debug(files) 

    for f in files_and_dirs:
         filename = os.path.join(directory_path, f)
         if os.path.isfile(filename):
             with open(filename, 'rb') as file:
                 history = pickle.load(file)
                 logger.debug(history)
                 if history != '' :
                    model = getModel() 
                    session = Session()
                    session.chat = model.start_chat(history=history)
                    session.timestamp = time.time() 
                    sessions_cache[str(f)] = session 


def ask (id, content):
    answer = "哇，不知道怎麼回答這個問題"
    if id not in sessions_cache:
        logger.debug ("No Chat session is found for : " + str(id) + ". Starts a new chat session")

        model = getModel()

        chat_session = Session()
        chat_session.chat = model.start_chat(history=[])  # Load history from here
        chat_session.timestamp = time.time()

        sessions_cache[id] = chat_session


    session  = sessions_cache[id]

    logger.debug (session)
    #logger.debug (chat.history)
    try:
        response = session.chat.send_message(content)
        session.timestamp = time.time()

        # Check if response contains function calls
        if response.candidates[0].content.parts:
            part = response.candidates[0].content.parts[0]

            # Check if it's a function call
            if hasattr(part, 'function_call') and part.function_call:
                function_call = part.function_call
                logger.info(f"Function call detected: {function_call.name}")

                # Execute the function
                function_result = None
                if function_call.name == "get_smart_home_status":
                    # Extract arguments
                    args = dict(function_call.args)
                    logger.info(f"Executing function: get_smart_home_status with args: {args}")

                    try:
                        # Call the actual function
                        function_result = get_iot_status(**args)

                        # Send function response back to model
                        function_response = genai.protos.Part(
                            function_response=genai.protos.FunctionResponse(
                                name="get_smart_home_status",
                                response={"result": function_result}
                            )
                        )

                        # Get natural language response
                        final_response = session.chat.send_message(function_response)
                        session.timestamp = time.time()
                        answer = final_response.text

                    except Exception as func_error:
                        logger.error(f"Error executing function: {func_error}", exc_info=True)
                        # Send error back to model
                        error_response = genai.protos.Part(
                            function_response=genai.protos.FunctionResponse(
                                name="get_smart_home_status",
                                response={"error": str(func_error)}
                            )
                        )
                        final_response = session.chat.send_message(error_response)
                        session.timestamp = time.time()
                        answer = final_response.text

                elif function_call.name == "get_current_time":
                    # Extract arguments
                    args = dict(function_call.args)
                    logger.info(f"Executing function: get_current_time with args: {args}")

                    try:
                        # Call the actual function
                        function_result = get_current_time(**args)

                        # Send function response back to model
                        function_response = genai.protos.Part(
                            function_response=genai.protos.FunctionResponse(
                                name="get_current_time",
                                response={"result": function_result}
                            )
                        )

                        # Get natural language response
                        final_response = session.chat.send_message(function_response)
                        session.timestamp = time.time()
                        answer = final_response.text

                    except Exception as func_error:
                        logger.error(f"Error executing function: {func_error}", exc_info=True)
                        # Send error back to model
                        error_response = genai.protos.Part(
                            function_response=genai.protos.FunctionResponse(
                                name="get_current_time",
                                response={"error": str(func_error)}
                            )
                        )
                        final_response = session.chat.send_message(error_response)
                        session.timestamp = time.time()
                        answer = final_response.text

                else:
                    # Unknown function
                    logger.warning(f"Unknown function called: {function_call.name}")
                    answer = response.text if response.text else "抱歉，我無法處理這個請求"
            else:
                # Normal text response
                answer = response.text
        else:
            # No parts in response
            answer = response.text if response.text else "沒有收到回應"

    except StopCandidateException as safety_exception :
        logger.error ("Error occurred when user ask : " + content + "  with exception : " + str(safety_exception))
        answer = "為了保護你，這個問題就不回答了"
    except Exception as e:
        logger.error ("Error occurred when user ask : " + content + "  with exception : " + str(e), exc_info=True)

    return answer


def getModel ():
    global model
    if model is None:
        model = genai.GenerativeModel(
            model_name='gemini-2.5-flash',
            system_instruction=instruction,
            tools=all_tools,
            safety_settings={genai.types.HarmCategory.HARM_CATEGORY_HATE_SPEECH: genai.types.HarmBlockThreshold.BLOCK_NONE,
                             genai.types.HarmCategory.HARM_CATEGORY_HARASSMENT: genai.types.HarmBlockThreshold.BLOCK_NONE,
                             genai.types.HarmCategory.HARM_CATEGORY_SEXUALLY_EXPLICIT: genai.types.HarmBlockThreshold.BLOCK_ONLY_HIGH,
                             genai.types.HarmCategory.HARM_CATEGORY_DANGEROUS_CONTENT: genai.types.HarmBlockThreshold.BLOCK_NONE})
    return model

def history (id):
    data = '' 
    session = sessions_cache[id]
    if session:
        data = str(session.chat.history) 
    return data


def historyPersistentJob () :

    while not GRACEFULLY_STOP:
        historyPersistent()
        time.sleep(60)

def historyPersistent():
    global last_dump_time
    if not sessions_cache is None:
            if not last_dump_time is None:
                for key in sessions_cache:
                    if last_dump_time < sessions_cache[key].timestamp:
                        history = sessions_cache[key].chat.history
                        if history :
                            with open('history/'+key, 'wb') as file:
                                pickle.dump(history, file)
    last_dump_time = time.time()


job = threading.Thread(target=historyPersistentJob)    
job.start()
