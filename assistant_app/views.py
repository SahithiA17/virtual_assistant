from django.shortcuts import render
from django.http import JsonResponse
from django.conf import settings
from django.views.decorators.csrf import csrf_exempt
from .models import ChatMessage
import requests
import psutil
import platform
import random
import socket
from PIL import Image
import io
import base64
import json
import os
import string
import speedtest
import pyautogui
import wolframalpha
import subprocess
import webbrowser
from urllib.parse import quote_plus
import pywhatkit
from datetime import datetime
import pyautogui
import time
import platform
import subprocess
import pygetwindow as gw
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from django.conf import settings
import re

# Stability SDK
from stability_sdk import client
import stability_sdk.interfaces.gooseai.generation.generation_pb2 as generation


# ------------------ Core Functions ------------------

def tell_joke():
    jokes = [
        "Why don't scientists trust atoms? Because they make up everything!",
        "Why did the computer go to the doctor? Because it had a virus!",
        "Why was the math book sad? Because it had too many problems.",
        "Why do programmers prefer dark mode? Because light attracts bugs!"
    ]
    return random.choice(jokes)


def get_ip():
    '''
    hostname = socket.gethostname()
    ip_address = socket.gethostbyname(hostname)
    return ip_address
    '''
    try:
        ip = requests.get("https://api.ipify.org").text
        return f"Your public IP address is {ip}."
    except:
        return "Could not retrieve IP address."

def get_system_stats():
    battery = psutil.sensors_battery()
    cpu = psutil.cpu_percent()
    ram = psutil.virtual_memory().percent
    system = platform.system()
    release = platform.release()
    return f"System: {system} {release}, CPU usage: {cpu}%, RAM usage: {ram}%, Battery: {battery.percent if battery else 'N/A'}%"


def get_weather(city=None):
    api_key = settings.OPENWEATHER_API_KEY
    if not api_key:
        return "Weather API key not configured."
    if not city:
        city = "London"

    city = city.strip(string.punctuation).capitalize()

    url = f"http://api.openweathermap.org/data/2.5/weather?q={city}&appid={api_key}&units=metric"
    try:
        res = requests.get(url).json()
        if res.get("cod") != 200:
            return f"Could not get weather info for '{city}'."
        temp = res['main']['temp']
        desc = res['weather'][0]['description']
        return f"The temperature in {city} is {temp}°C with {desc}."
    except Exception as e:
        return f"Sorry, I couldn't get the weather info due to: {e}"


def generate_image_from_text(text):
    api_key = settings.DREAMSTUDIO_API_KEY
    if not api_key:
        print("No API key found.")
        return None

    try:
        stability_api = client.StabilityInference(
            key=api_key,
            engine="stable-diffusion-xl-1024-v1-0",
            verbose=False,
        )

        answers = stability_api.generate(prompt=text, seed=95456)
        for resp in answers:
            for artifact in resp.artifacts:
                if artifact.finish_reason == generation.FILTER:
                    print("Blocked by safety filter.")
                    return None
                elif artifact.type == generation.ARTIFACT_IMAGE:
                    img = Image.open(io.BytesIO(artifact.binary))
                    buffered = io.BytesIO()
                    img.save(buffered, format="PNG")
                    return base64.b64encode(buffered.getvalue()).decode()

    except Exception as e:
        print("Image generation error:", str(e))
        return None

def internet_speed_test():
    try:
        st = speedtest.Speedtest()
        download = st.download() / 1_000_000  # Mbps
        upload = st.upload() / 1_000_000  # Mbps
        return f"Download speed: {download:.2f} Mbps, Upload speed: {upload:.2f} Mbps."
    except Exception as e:
        return f"Speed test failed: {str(e)}"

def take_screenshot():
    try:
        screenshot = pyautogui.screenshot()

        # Define folder path relative to your Django project base directory
        folder = os.path.join(settings.BASE_DIR, 'media', 'screenshots')
        
        # Create folder if not exists
        os.makedirs(folder, exist_ok=True)

        # Define full save path
        save_path = os.path.join(folder, "django_test_screenshot.png")

        # Save screenshot
        screenshot.save(save_path)

        # Convert screenshot to base64 for inline display
        buffered = io.BytesIO()
        screenshot.save(buffered, format="PNG")
        img_str = base64.b64encode(buffered.getvalue()).decode('utf-8')
        
        print("Screenshot saved at:", save_path)
        print("Screenshot base64 length:", len(img_str))
        return "data:image/png;base64," + img_str
    except Exception as e:
        print("Screenshot error:", e)
        return None

def brief_info(query):
    try:
        client_w = wolframalpha.Client(settings.WOLFRAMALPHA_API)
        res = client_w.query(query)
        # Take first three pods of plaintext answers
        answers = []
        for pod in res.pods:
            if pod.text:
                answers.append(pod.text)
            if len(answers) >= 3:
                break
        return " ".join(answers) if answers else "No info found."
    except Exception as e:
        return f"Failed to get info: {str(e)}"

def math_gk_query(query):
    return brief_info(query)

def open_app(app_name):
    # Example: open calculator (Windows)
    try:
        if platform.system() == "Windows":
            if "calculator" in app_name.lower():
                subprocess.Popen('calc.exe')
                return "Opening Calculator."
            elif "notepad" in app_name.lower():
                subprocess.Popen('notepad.exe')
                return "Opening Notepad."
            else:
                return f"Sorry, app {app_name} is not supported yet."
        else:
            return "App opening supported only on Windows currently."
    except Exception as e:
        return f"Failed to open app: {str(e)}"

def open_website(url):
    try:
        if not url.startswith("http"):
            url = "https://" + url
        webbrowser.open(url)
        return f"Opening website {url}."
    except Exception as e:
        return f"Failed to open website: {str(e)}"

def google_search(query):
    search_url = f"https://www.google.com/search?q={query.replace(' ', '+')}"
    webbrowser.open(search_url)
    return f"Here are the Google search results for {query}."

def play_youtube(video):
    try:
        pywhatkit.playonyt(video)
        return f"Playing {video} on YouTube."
    except Exception as e:
        return f"Failed to play video: {str(e)}"

def take_note(text):
    try:
        with open("notes.txt", "a") as f:
            f.write(f"{datetime.now()}: {text}\n")
        return "Note saved."
    except Exception as e:
        return f"Failed to save note: {str(e)}"

def get_news():
    try:
        api_key = settings.NEWS_API
        url = f"https://newsapi.org/v2/top-headlines?country=us&apiKey={api_key}"
        res = requests.get(url).json()
        articles = res.get("articles", [])[:5]
        headlines = [f"{i+1}. {a['title']}" for i, a in enumerate(articles)]
        return "Here are the top news headlines:\n" + "\n".join(headlines)
    except Exception as e:
        return f"Failed to fetch news: {str(e)}"

def get_movies():
    try:
        api_key = settings.TMDB_API
        trending_titles = [
            "Dune Part Two",
            "Oppenheimer",
            "Civil War",
            "Godzilla x Kong",
            "The Fall Guy"
        ]
        movies = []
        for i, title in enumerate(trending_titles):
            url = f"http://www.omdbapi.com/?t={title}&apikey={api_key}"
            res = requests.get(url).json()

            if res.get("Response") == "True":
                movies.append(f"{i+1}. {res.get('Title')} ({res.get('Year')})")
            else:
                movies.append(f"{i+1}. {title} - Not Found")

        return "Trending movies:\n" + "\n".join(movies)
    except Exception as e:
        return f"Failed to get movies: {str(e)}"
        

def get_map(city):
    try:
        city = city.strip().replace(" ", "+")
        map_url = f"https://www.google.com/maps/place/{city}"
        return f"Here is the map of {city.replace('+', ' ')}: {map_url}"
    except Exception as e:
        return f"Failed to get map: {str(e)}"

def get_distance(origin, destination):
    try:
        origin_fmt = origin.strip().replace(" ", "+")
        destination_fmt = destination.strip().replace(" ", "+")
        map_url = f"https://www.google.com/maps/dir/{origin_fmt}/{destination_fmt}"
        return f"Here is the route from {origin} to {destination}: {map_url}"
    except Exception as e:
        return f"Failed to get distance: {str(e)}"

def open_new_tab():
    # Ctrl+T for new tab
    pyautogui.hotkey('ctrl', 't')
    return "New tab opened."

def close_current_tab():
    # Ctrl+W for close tab
    pyautogui.hotkey('ctrl', 'w')
    return "Current tab closed."

def switch_tab(direction='next'):
    # Ctrl+Tab or Ctrl+Shift+Tab to switch tabs
    if direction == 'next':
        pyautogui.hotkey('ctrl', 'tab')
    else:
        pyautogui.hotkey('ctrl', 'shift', 'tab')
    return f"Switched to {direction} tab."

def copy_text():
    pyautogui.hotkey('ctrl', 'c')
    return "Copied selected text."

def paste_text():
    pyautogui.hotkey('ctrl', 'v')
    return "Pasted text."

def delete_text():
    pyautogui.press('delete')
    return "Deleted selected text."

def select_all_text():
    pyautogui.hotkey('ctrl', 'a')
    return "Selected all text."

def minimize_window(title=None):
    try:
        if title:
            win = gw.getWindowsWithTitle(title)[0]
        else:
            win = gw.getActiveWindow()
        win.minimize()
        return f"Window '{win.title}' minimized."
    except Exception as e:
        return f"Failed to minimize window: {str(e)}"

def maximize_window(title=None):
    try:
        if title:
            win = gw.getWindowsWithTitle(title)[0]
        else:
            win = gw.getActiveWindow()
        win.maximize()
        return f"Window '{win.title}' maximized."
    except Exception as e:
        return f"Failed to maximize window: {str(e)}"

def close_window(title=None):
    try:
        if title:
            win = gw.getWindowsWithTitle(title)[0]
        else:
            win = gw.getActiveWindow()
        win.close()
        return f"Window '{win.title}' closed."
    except Exception as e:
        return f"Failed to close window: {str(e)}"

def switch_window(title=None):
    try:
        if title:
            win = gw.getWindowsWithTitle(title)[0]
        else:
            return "Please specify window title to switch."
        win.activate()
        return f"Switched to window '{win.title}'."
    except Exception as e:
        return f"Failed to switch window: {str(e)}"
    
def send_email(to_email, subject, body):
    try:
        sender_email = settings.EMAIL_HOST_USER
        sender_password = settings.EMAIL_HOST_PASSWORD
        msg = MIMEMultipart()
        msg['From'] = sender_email
        msg['To'] = to_email
        msg['Subject'] = subject
        msg.attach(MIMEText(body, 'plain'))

        server = smtplib.SMTP(settings.EMAIL_HOST, settings.EMAIL_PORT)
        server.starttls()
        server.login(sender_email, sender_password)
        server.send_message(msg)
        server.quit()
        return "Email sent successfully."
    except Exception as e:
        return f"Failed to send email: {str(e)}"
    
def assistant_reply(user_input):
    user_input = user_input.lower()
    response = ""
    img_prompt = None

    if 'joke' in user_input:
        response = tell_joke()
    elif 'ip address' in user_input:
        response = get_ip()
    elif 'system stats' in user_input:
        response = get_system_stats()
    elif 'weather' in user_input:
        words = user_input.split()
        city = words[-1].strip(string.punctuation).capitalize() if len(words) > 1 else None
        response = get_weather(city)
    elif 'generate image' in user_input:
        img_prompt = user_input.replace('generate image', '').strip()
        response = "Generating your image now..."    
    elif 'internet speed' in user_input or 'speed test' in user_input:
        response = internet_speed_test()
    elif 'screenshot' in user_input:
        img_prompt = "screenshot"
        response = "Taking screenshot now..."
    elif 'info about' in user_input:
        query = user_input.replace("info about", "").strip()
        response = brief_info(query)
    elif 'math' in user_input or 'calculate' in user_input:
        query = user_input.replace("calculate", "").replace("math", "").strip()
        response = math_gk_query(query)
    elif 'open app' in user_input:
        app_name = user_input.replace("open app", "").strip()
        response = open_app(app_name)
    elif 'open website' in user_input:
        url = user_input.replace("open website", "").strip()
        response = open_website(url)
    elif 'google search' in user_input:
        query = user_input.replace("google search", "").strip()
        response = google_search(query)
    elif 'play youtube' in user_input:
        video = user_input.replace("play youtube", "").strip()
        response = play_youtube(video)
    elif 'take note' in user_input:
        note = user_input.replace("take note", "").strip()
        response = take_note(note)
    elif 'news' in user_input:
        response = get_news()
    elif 'movies' in user_input or 'tv series' in user_input:
        response = get_movies()
    elif 'show map' in user_input:
        city = user_input.replace("show map", "").strip()
        response = get_map(city)
    elif 'distance between' in user_input:
        try:
            parts = user_input.split("distance between")[1].split("and")
            origin = parts[0].strip()
            destination = parts[1].strip()
            response = get_distance(origin, destination)
        except Exception:
            response = "Please provide cities like: distance between city1 and city2"
    elif 'open new tab' in user_input:
        response = open_new_tab()
    elif 'close tab' in user_input:
        response = close_current_tab()
    elif 'switch tab next' in user_input:
        response = switch_tab('next')
    elif 'switch tab previous' in user_input:
        response = switch_tab('previous')
    elif 'copy text' in user_input:
        response = copy_text()
    elif 'paste text' in user_input:
        response = paste_text()
    elif 'delete text' in user_input:
        response = delete_text()
    elif 'select all' in user_input:
        response = select_all_text()
    elif 'minimize window' in user_input:
        response = minimize_window()
    elif 'maximize window' in user_input:
        response = maximize_window()
    elif 'close window' in user_input:
        response = close_window()
    elif 'switch window' in user_input:
    # You might want to extract window title or name from input
        title = user_input.replace('switch window', '').strip()
        response = switch_window(title)
    elif 'send e-mail' in user_input:
        # Expect format "send email to email@example.com subject Hello body This is test"
        try:
            parts = user_input.split(" ")
            to_index = parts.index("to") + 1
            subject_index = parts.index("subject") + 1
            body_index = parts.index("body") + 1
            to_email = parts[to_index]
            subject = " ".join(parts[subject_index:body_index-1])
            body = " ".join(parts[body_index:])
            response = send_email(to_email, subject, body)
        except Exception:
            response = "Email command format error. Please say: send email to [email] subject [subject] body [body]."

    else:
        return "Sorry, I did not understand.", None
    return response, img_prompt

# ------------------ Views ------------------

def index(request):
    image_data = None
    image_type = None
    if request.method == "POST":
        user_message = request.POST.get('user_message')
        assistant_response, img_prompt = assistant_reply(user_message)
        
        if img_prompt:
            if img_prompt == "screenshot":
                image_data = take_screenshot()
                image_type = "screenshot"  
                if image_data:
                    assistant_response += " (Screenshot is saved.)" 
                    print("image_data in view (screenshot):", image_data[:100])    
                else:
                    assistant_response += " Sorry, I couldn't take screenshot for that."
            else:
                image_data = generate_image_from_text(img_prompt)
                image_type = "generated"
                if image_data:
                    assistant_response += " (Scroll down to see the image.)"
                else:
                    assistant_response += " Sorry, I couldn't generate an image for that."

        ChatMessage.objects.create(user_message=user_message, assistant_response=assistant_response)

        chats = ChatMessage.objects.all().order_by('timestamp')
        return render(request, 'assistant_app/index.html', {
            'chats': chats,
            'image_data': image_data,
            'image_type': image_type
        })

    chats = ChatMessage.objects.all().order_by('timestamp')
    return render(request, 'assistant_app/index.html', {'chats': chats})


@csrf_exempt
def voice_assistant_api(request):
    if request.method == "POST":
        try:
            data = json.loads(request.body)
            user_message = data.get('user_message', '').strip()
        except Exception:
            return JsonResponse({'error': 'Invalid JSON'}, status=400)

        assistant_response, img_prompt = assistant_reply(user_message)
        image_data = None
        image_requested = False
        image_type = None

        if img_prompt:
            if img_prompt == "screenshot":
                image_data = take_screenshot()
                image_type = "screenshot"
                if image_data:
                    assistant_response += " (Screenshot is saved.)"
                    print("image_data in view (screenshot):", image_data[:100]) 
                else:
                    assistant_response += " Sorry, I couldn't take screenshot for that."
            else:
                image_data = generate_image_from_text(img_prompt)
                image_type = "generated"
                image_requested = True
                if image_data:
                    assistant_response += " (Scroll down to see the image.)"
                else:
                    assistant_response += " Sorry, I couldn't generate an image for that."

        ChatMessage.objects.create(user_message=user_message, assistant_response=assistant_response)

        return JsonResponse({
            'assistant_response': assistant_response,
            'image_data': image_data,
            'image_requested': image_requested,
            'image_type': image_type
        })

    return JsonResponse({'error': 'POST method required'}, status=405)
