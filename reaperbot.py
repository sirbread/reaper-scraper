import time
import os
import discord
from discord.ext import tasks
from datetime import datetime
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager

TOKEN = "yourdiscordbottoken" #set up a discord bot at the developer portal, or watch a yt video idk
CHANNEL_ID = 0 #change this to your server's channel id in which you want the bot to ping you (keep as int)
PING_THRESHOLDS = ["15 minutes", "16 minutes", "17 minutes", "18 minutes", "19 minutes", "20 minutes", "21 minutes", "22 minutes", "23 minutes", "24 minutes", "25 minutes", "26 minutes", "27 minutes", "28 minutes", "29 minutes", "30 minutes", "31 minutes", "32 minutes", "33 minutes", "34 minutes", "35 minutes"]  
USER_IDS = [0, 1, 2] #change this to the user ids of the people you want to ping  

options = webdriver.ChromeOptions()
options.add_argument("--disable-gpu")
options.add_argument("--no-sandbox")
options.add_argument("--headless")

driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)

URL = "https://artofproblemsolving.com/reaper/reaper.php?id=92"
USERNAME = "username" #change to your aops username (or an alt) so it can log in and scrape :3
PASSWORD = "password" #same thing, but password

client = discord.Client(intents=discord.Intents.default())

last_reaps = []
already_pinged = set()

def log_message(message):
    with open("recent_reaps.txt", "a", encoding="utf-8") as file:
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        file.write(f"[{timestamp}] {message}\n")

def scrape_timer():
    global last_reaps
    try:
        driver.get(URL)
        wait = WebDriverWait(driver, 15)

        login_button = wait.until(EC.element_to_be_clickable((By.CLASS_NAME, "online-login-button")))
        login_button.click()

        username_field = wait.until(EC.presence_of_element_located((By.ID, "login-id")))
        password_field = wait.until(EC.presence_of_element_located((By.ID, "password")))

        username_field.send_keys(USERNAME)
        password_field.send_keys(PASSWORD)

        login_button = wait.until(EC.element_to_be_clickable((By.ID, "login-button")))
        login_button.click()

        wait.until(EC.presence_of_element_located((By.ID, "last-reap")))
        wait.until(EC.presence_of_element_located((By.ID, "recent-reaps")))

        log_message("Logged in successfully.")

        recent_reaps_div = driver.find_element(By.ID, "recent-reaps")
        last_reaps = recent_reaps_div.text.split("\n")

    except Exception as e:
        error_message = f"Login error: {e}"
        log_message(error_message)
        print(error_message)

@tasks.loop(seconds=1)
async def check_timer():
    global last_reaps, already_pinged
    try:
        last_reap_div = driver.find_element(By.ID, "last-reap")
        current_timer = last_reap_div.text.strip()

        os.system('cls' if os.name == 'nt' else 'clear')
        print(f"{current_timer}")

        for threshold in PING_THRESHOLDS:
            if threshold in current_timer:
                minutes_only = threshold.split()[0]  
                if minutes_only not in already_pinged:  
                    already_pinged.add(minutes_only)  
                    channel = client.get_channel(CHANNEL_ID)
                    if channel:
                        user_mentions = " ".join(f"<@{uid}>" for uid in USER_IDS)
                        await channel.send(f"{user_mentions} Timer has reached {threshold}!")

        recent_reaps_div = driver.find_element(By.ID, "recent-reaps")
        current_reaps = recent_reaps_div.text.split("\n")

        new_reaps = [line for line in current_reaps if line not in last_reaps]

        if new_reaps:
            already_pinged.clear() 
            with open("recent_reaps.txt", "a", encoding="utf-8") as file:
                for line in new_reaps:
                    file.write(line + "\n")

            last_reaps = current_reaps  


    except Exception as e:
        error_message = f"Error in check_timer: {e}"
        log_message(error_message)
        print(error_message)

@client.event
async def on_ready():
    print(f'Logged in as {client.user}')
    scrape_timer()
    check_timer.start()

client.run(TOKEN)
