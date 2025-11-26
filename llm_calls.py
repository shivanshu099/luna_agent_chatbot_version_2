import getpass
import os
from dotenv import load_dotenv
from llm_tools import capture_me,latest_news,capture_screenshot,image_to_text,todo_add,todo_list,todo_remove,open_website,load_persnal_info,music_folder_list,play_sound,current_time,llm_tool,send_email,send_email_with_image,mute,unmute,hidden_screen_overlay
from langchain.chat_models import init_chat_model
from langchain.agents import initialize_agent
from langgraph.prebuilt import create_react_agent
from langgraph.checkpoint.memory import MemorySaver

load_dotenv()

os.environ["GOOGLE_API_KEY"] = os.getenv("GEMINI_API_KEY")
if not os.environ.get("GOOGLE_API_KEY"):
  os.environ["GOOGLE_API_KEY"] = getpass.getpass("Enter API key for Google Gemini: ")

model = init_chat_model("gemini-2.5-flash", model_provider="google_genai")
tools=[capture_me,latest_news,capture_screenshot,image_to_text,todo_add,todo_list,todo_remove,open_website,load_persnal_info,music_folder_list,play_sound,current_time,llm_tool,send_email,send_email_with_image,mute,unmute,hidden_screen_overlay]

system_instruction = """
You are Luna, a highly concise AI assistant created by Shivanshu Prajapati.
Your rules:
- Always respond in 1–2 short sentences unless the user explicitly asks for a detailed explanation.
- Be respectful, efficient, and minimal at all times.
- Use the appropriate tool immediately whenever it helps answer the user's request.
- If information is missing or unclear, first check the personal_info tool before responding.
- Stay strictly focused on the user's request and avoid unnecessary conversation.
- Refer to yourself only as "Luna."

"""

memory=MemorySaver()

agent = create_react_agent(
  tools = tools,
  model=model,
  checkpointer=memory,
)

config ={"configurable":{"thread_id":"session1"}}

#re = agent.invoke("hi how you doing")
def llm_callu(query:str)->str:
  re = agent.invoke(
    {
    "messages": [
      {"role":"system","content":system_instruction},
    {"role": "user", 
     "content": query}]},config=config)
  return re["messages"][-1].content

#print(re["messages"][-1].content)


 

























