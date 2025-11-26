

#Gloabel variable to track mute status
AGENT_MUTED = False



import cv2
import time
import uuid
from langchain.tools import tool
import requests
from bs4 import BeautifulSoup
import pyautogui
from PIL import Image
import pytesseract
import os
import json
import time
import datetime
import webbrowser
import pygame

import platform
from pathlib import Path
from termcolor import colored


import subprocess



#________________________________vision_tool________________________________________________
@tool
def capture_me(filename:str)->str:
    """open the webcamp, capture a single image and save it as a PNG file. it takes the filename as input without extension and then it will return the unique filename"""
    camera=cv2.VideoCapture(0)
    if not camera.isOpened():
        return "could not open webcam"
    ret,frame = camera.read()
    if not ret:
         return "Failed to grab frame"
    time.sleep(2)
    cv2.imshow("heeeee",frame)
    cv2.waitKey(2000)
    image_name=filename+str(uuid.uuid4())+".png"
    cv2.imwrite(image_name,frame)
    camera.release()
    cv2.destroyAllWindows()
    return f"sucsesfully captured the image as {image_name}"

@tool
def latest_news(limit:int)->list:
    """this latest_news tool is used to get latest news from gogle there is limit to input to get how many news"""
    try:
        url="https://news.google.com/topics/CAAqJQgKIh9DQkFTRVFvSUwyMHZNRE55YXpBU0JXVnVMVWRDS0FBUAE?hl=en-IN&gl=IN&ceid=IN%3Aen"
        headers={"User-Agent":"Mozilla/5.0"}
        response=requests.get(url,headers)
        soup=BeautifulSoup(response.text,"html.parser")
        links=soup.find_all("a",class_="gPFEn")
        news=[]
        for tag in links[:limit]:
            title = tag.text.strip()
            relative_link = tag["href"]
            full_link = f"https://news.google.com{relative_link[1:]}" if relative_link.startswith('.') else relative_link
            #print("Title:",title)
            #print("Link",full_link)
            #print("-"*40)
            news.append(title)
        return news
    except Exception as e:
        return f"the error is ocured {e}"

@tool
def capture_screenshot(filename:str)->str:
    """this fucntion used to capture the screenshot of system and save into png format and return the unique filename"""
    try:
        un_filename=filename+".png"
        if os.path.exists(un_filename):
            un_filename=filename+"_"+str(uuid.uuid4())+".png"
        time.sleep(2)
        screenshot = pyautogui.screenshot()
        screenshot.save(un_filename)
        return un_filename
    except Exception as e:
        return f"there is an error ocurded {e}"


@tool
def image_to_text(filename: str,lang="eng")->str:
    """
    Extracts and returns text from an image file using OCR, with preprocessing.

    Parameters:
    - filename (str): Path to the image file.
    - lang (str): Language code for OCR (default is 'eng').

    Returns:
    - str: Extracted text from the image.
    """
    pytesseract.pytesseract.tesseract_cmd = r"C:\Program Files\Tesseract-OCR\tesseract.exe"
    try:
        image=cv2.imread(filename)
        if image is None:
            return f"Error: could not read file {filename}"
        gray = cv2.cvtColor(image,cv2.COLOR_BGR2GRAY)
        text=pytesseract.image_to_string(gray,lang=lang)
        return text.strip()
    except Exception as e:
        return f"Error processing image: {str(e)}"

#__________________________todo_list_tool__________________________

file_path="todo_list.json"    
def read_todo_list():
    """
    Read the todo list from the JSON file.

    Returns:
        dict: The dictionary containing tasks.
              If file is empty or not found, returns {"tasks": []}.
    """
    try:
        with open(file_path, 'r') as file:
            data = json.load(file)
            return data
    except (FileNotFoundError, json.JSONDecodeError):
        # If the file doesn't exist or is corrupted, return an empty structure
        return {"tasks": []}


def save_todos(data):
    """
    Save the todo list into the JSON file.

    Args:
        data (dict): A dictionary containing the tasks to save.
    """
    with open(file_path, "w") as file:
        json.dump(data, file, indent=2)

@tool
def todo_add(task, time=None):
    """
    Add a new task to the todo list.

    Args:
        task (str): The description of the task.
        time (str, optional): A specific time in ISO format. 
                              If not provided, current datetime is used.
    """
    todos = read_todo_list()

    # Use current time if no time is provided
    if not time:
        time = datetime.now().isoformat()

    # New task structure
    new_task = {
        "task": task,
        "time": time,
    }

    # Append new task into list
    todos["tasks"].append(new_task)

    # Save the updated list
    save_todos(todos)


@tool
def todo_list():
    """
    Retrieve and display all tasks in the todo list.

    Returns:
        list: A list of all tasks with their index, task description, and time.
    """
    todos = read_todo_list()
    task_list = todos.get("tasks", [])

    # Format tasks for display
    formatted_tasks = []
    for idx, item in enumerate(task_list, start=1):
        formatted_tasks.append({
            "id": idx,
            "task": item["task"],
            "time": item["time"]
        })

    return formatted_tasks

@tool
def todo_remove(index):
    """
    Remove a task from the todo list by its index.

    Args:
        index (int): The 1-based index of the task to remove.

    Returns:
        bool: True if task was removed, False if index was invalid.
    """
    todos = read_todo_list()
    task_list = todos.get("tasks", [])

    # Check if index is valid
    if 1 <= index <= len(task_list):
        task_list.pop(index - 1)  # remove task
        todos["tasks"] = task_list
        save_todos(todos)
        return True
    else:
        return False
    
@tool
def current_time()->str:
    """this function is used for returning the current time in iso format it does not takes any input but return time in str"""
    time = datetime.now().isoformat()
    return time
#_________________________________web_tool_____________________________
@tool
def open_website(url:str):
    """
    Open a given URL in the default web browser.

    Args:
        url (str): The website link to open.
    Returns:
        str: Confirmation message.
    """
    if not url.startswith("http://") and not url.startswith("https://"):
        url="https://"+url
    webbrowser.open(url)
    return f"opened website: {url}"
#____________________________persnal_info__________________

@tool
def load_persnal_info():
    """
    this function is used to  store persnal information in json file and return the data as dictionary
    it contains many information
    Returns:
        dict: A dictionary containing personal information if the file exists,
              otherwise an empty dictionary.
    """
    if not os.path.exists("persnal_info.json"):
        return {}
    with open("persnal_info.json","r") as f:
        return json.load(f)
    
#________________________________play_music_____________________


@tool
def music_folder_list(folder: str) -> list:
    """
    List all music files (MP3/WAV) in the given folder.

    Args:
        folder (str): Path to the music folder.

    Returns:
        list: Sorted list of music filenames (not full paths).
    """

    # Validate folder exists
    if not os.path.exists(folder):
        return ["Error: Folder not found"]

    # Validate it's a directory
    if not os.path.isdir(folder):
        return ["Error: Provided path is not a folder"]

    try:
        # List only mp3 and wav files (ignore hidden/system files)
        music_files = [
            f for f in os.listdir(folder)
            if f.lower().endswith((".mp3", ".wav")) and not f.startswith(".")
        ]

        # Sort alphabetically for cleaner output
        return sorted(music_files)

    except Exception as e:
        return [f"Error: {str(e)}"]
@tool
def play_sound(file: str) -> str:
    """
    Play an audio file (MP3 or WAV).

    Args:
        file (str): Full path to the audio file.

    Returns:
        str: Status message.
    """
    # Check file exists
    if not os.path.isfile(file):
        return f"Error: File '{file}' not found."

    try:
        system_platform = platform.system()

        if system_platform == "Windows":
            os.startfile(file)

        elif system_platform == "Darwin":  # macOS
            subprocess.Popen(["open", file])

        else:  # Linux
            subprocess.Popen(["xdg-open", file])

        return f"Playing sound: {os.path.basename(file)}"

    except Exception as e:
        return f"Error playing sound: {str(e)}"
#____________________________mute tool_____________________________

@tool
def mute()->str:
    """ this function is used to mute the agent it does not take any input but return the status of agent"""
    global AGENT_MUTED
    AGENT_MUTED=True
    return "Agent muted"

@tool
def unmute()->str:
    """ this function is used to unmute the agent it does not take any input but return the status of agent"""
    global AGENT_MUTED
    AGENT_MUTED=False
    return "Agent unmuted"



@tool
def open_image(file_path: str):
    """
    Open an image file using the default image viewer of the operating system.

    Args:
        file_path (str): Path to the image file to open.

    Returns:
        None
    """
    path = Path(file_path)

    # Check if file exists
    if not path.is_file():
        print(colored(f"❌ File not found: {file_path}", "red"))
        return

    try:
        system = platform.system()
        if system == "Windows":
            os.startfile(path)  # Windows default
        elif system == "Darwin":  # macOS
            os.system(f"open '{path}'")
        else:  # Linux
            os.system(f"xdg-open '{path}'")
        print(colored(f"✅ Opened image: {file_path}", "green"))
    except Exception as e:
        print(colored(f"Error opening image: {e}", "red"))

#______________________________________________llm_model______________

from langchain.chat_models import init_chat_model
import getpass
from dotenv import load_dotenv

load_dotenv()

os.environ["GOOGLE_API_KEY"] = os.getenv("GEMINI_API_KEY")
if not os.environ.get("GOOGLE_API_KEY"):
  os.environ["GOOGLE_API_KEY"] = getpass.getpass("Enter API key for Google Gemini: ")

# Initialize the LLM (Google Gemini)
model = init_chat_model("gemini-2.5-flash", model_provider="google_genai")    
SYSTEM_PROMPT = (
    "You are Luna, an AI assistant built by Shivanshu Prajapati. "
    "Always answer in minimal words, be concise, and friendly. "
    "Keep responses short and clear."
)

@tool
def llm_tool(query: str) -> str:
    """
    General-purpose LLM tool for reasoning, summarization, Q&A,coding, etc.

    Args:
        query (str): The input question or task.

    Returns:
        str: The model's response.
    """
    try:
        # Directly use the chat model without an agent
        messages = [
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": query}
        ]
        response=model.invoke(messages)
        return response.content
    except Exception as e:
        return f"Error processing the query: {e}"


import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.image import MIMEImage

load_dotenv()
MY_EMAIL=os.getenv("MY_EMAIL")
MY_APP_NAME=os.getenv("MY_APP_NAME")
MY_APP_PASSWORD=os.getenv("MY_APP_PASSWORD")

@tool
def send_email(reciver_email:str,subject:str,body:str)->str:
    """this function is used to send email it takes reciver_email,subject,body as input and return the status of email"""
    msg=MIMEMultipart()
    msg["FROM"]=MY_EMAIL
    msg["TO"]=reciver_email
    msg["Subject"]=subject
    msg.attach(MIMEText(body,"plain"))
    try:
        with smtplib.SMTP("smtp.gmail.com",587) as server:
            server.starttls()
            server.login(MY_EMAIL,MY_APP_PASSWORD)
            server.send_message(msg)
        return "email has been sent"
    except Exception as e:
        return f"there is an error ocurred {e}"

@tool
def send_email_with_image(reciver_email:str,subject:str,body:str,image_path:str)->str:
    """this function is used to send email and image as attachement it takes reciver_email,subject,body,image_path as input and return the status of email"""

    msg=MIMEMultipart()
    msg["FROM"]=MY_EMAIL
    msg["TO"]=reciver_email
    msg["Subject"]=subject
    msg.attach(MIMEText(body,"plain"))
    try:
        if os.path.exists(image_path):
            with open(image_path,"rb") as img:
                image=MIMEImage(img.read())
                image.add_header("Content-Disposition",f"attachment; filename={os.path.basename(image_path)}")
                msg.attach(image)
        else:
            return f"Error: image file '{image_path}' not found."
        with smtplib.SMTP("smtp.gmail.com",587) as server:
            server.starttls()
            server.login(MY_EMAIL,MY_APP_PASSWORD)
            server.send_message(msg)
        return "email has been sent"
    except Exception as e:
        return f"there is an error ocurred {e}"
#________________________________tikinhter hidden overlay____________________

import tkinter as  tk
from threading import Thread
from multiprocessing import Process
class TransparentOverlay:
    def __init__(self, text, width=400, height=200, alpha=0.7):
        self.text = text
        self.width = width
        self.height = height
        self.alpha = alpha

    def run(self):
        root = tk.Tk()

        # setup window
        root.overrideredirect(True)
        root.attributes("-topmost", True)
        root.attributes("-alpha", self.alpha)

        screen_width = root.winfo_screenwidth()
        screen_height = root.winfo_screenheight()
        x = (screen_width - self.width) // 2
        y = (screen_height - self.height) // 2
        root.geometry(f"{self.width}x{self.height}+{x}+{y}")

        # close on click or esc
        root.bind("<Button-1>", lambda e: root.destroy())
        root.bind("<Escape>", lambda e: root.destroy())

        # scrollable text
        frame = tk.Frame(root, bg="black")
        frame.pack(expand=True, fill="both", padx=10, pady=10)
        scrollbar = tk.Scrollbar(frame)
        scrollbar.pack(side="right", fill="y")

        text_widget = tk.Text(
            frame,
            yscrollcommand=scrollbar.set,
            font=("Arial", 16),
            bg="black",
            fg="white",
            wrap="word"
        )
        text_widget.insert("1.0", self.text)
        text_widget.config(state="disabled")
        text_widget.pack(expand=True, fill="both", padx=10, pady=10)
        scrollbar.config(command=text_widget.yview)

        root.mainloop()

@tool
def hidden_screen_overlay(text:str)->str:
    """this function is used to display the text on  hidden screen as overlay it takes text as input and return the status of overlay"""
    overlay=TransparentOverlay(text=text)
    #overlay.run
    p=Process(target=overlay.run)
    p.start()
    return f"overlay display with is active"


if __name__=="__main__":
    #print(latest_news())
    #capture_screenshot()
    #re=send_email_with_image("kshivansh.knp@gmail.com","this is subject just for fun ","this is body of email just for fun i try to send email to myself using python  smtp thanks for you reading hope you are fine shivanshu ",r"C:\Users\knath\OneDrive\Pictures\Screenshots\yumi_screenshot.png")
    #hidden_screen_overlay("this is just for testing the overlay screen")
    print(load_persnal_info())




















