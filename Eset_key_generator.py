from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait as wait
from selenium.webdriver.support import expected_conditions as EC
from hashlib import sha256
from random import choice
import requests
import time
import re
import logging

service = Service('chromedriver.exe')
ESET_REGISTRATION_LINK = 'https://login.eset.com/Register'
CHARS = 'abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ1234567890!@#$%^&*()'

logging.basicConfig(
    level=logging.DEBUG, 
    format="%(asctime)s - %(levelname)s - %(message)s",  
    datefmt="%Y-%m-%d %H:%M:%S",  
    filename="app.log", 
    filemode="w"  
)

browser_eset = webdriver.Chrome(service=service)
browser_eset.get(ESET_REGISTRATION_LINK)

wait(browser_eset, 10).until(EC.visibility_of_element_located((By.XPATH, '//*[@id="cookiebar"]/div[1]')))
button_eset_cockies = browser_eset.find_element(By.XPATH, '/html/body/div[2]/div[1]/div/div[2]/div[2]/button')
button_eset_cockies.click()


def get_domains():
    response = requests.get("https://api.mail.tm/domains")
    r = response.json()["hydra:member"][0]["domain"]
    logging.debug(f'Get domain: {r}')
    return r

def create_account(email, password):
    response = requests.post("https://api.mail.tm/accounts", json={"address": email, "password": password})
    r = response.json()
    logging.debug(f'Create account: {r}')
    return r

def get_token(email, password):
    response = requests.post("https://api.mail.tm/token", json={"address": email, "password": password})
    r = response.json().get("token")
    logging.debug(f'Get token: {r}')
    return r

def get_messages(token):
    headers = {"Authorization": f"Bearer {token}"}
    response = requests.get("https://api.mail.tm/messages", headers=headers)
    r = response.json()["hydra:member"]
    logging.debug(f'Get messages: {r}')
    return r

def get_message_content(token, message_id):
    headers = {"Authorization": f"Bearer {token}"}
    response = requests.get(f"https://api.mail.tm/messages/{message_id}", headers=headers)
    r = response.json().get("text", "")
    logging.debug(f'Get message content: {r}')
    return r

def extract_confirmation_link(text):
    match = re.search(r'https?://\S+', text)
    r = match.group(0) if match else "Ссылка не найдена"
    logging.debug(f'Get message content: {r}')
    return r

before = ''.join(choice(CHARS) for _ in range(100))

domain = get_domains()
email = f"test_{int(time.time())}@{domain}"
password = sha256(before.encode()).hexdigest()+'A'

logging.info(f'Создание временной почты: {email}')
create_account(email, password)
token = get_token(email, password)

if token:
    logging.debug(f'Успешно получили токен аутентификации!')      
    logging.debug(f'Ожидание писем...')      

    email_input = browser_eset.find_element(By.XPATH, '//*[@id="email"]')
    email_input.send_keys(email)
    email_input.send_keys(Keys.ENTER)
    
    wait(browser_eset, 10).until(EC.visibility_of_element_located((By.XPATH, '//*[@id="password"]')))
    password_input = browser_eset.find_element(By.XPATH, '//*[@id="password"]')
    password_input.send_keys(password)
    password_input.send_keys(Keys.ENTER)
    
    time.sleep(10)  # Подождем немного, чтобы появилось письмо
    
    messages = get_messages(token)
    
    if messages:
        logging.info(f'Полученные сообщения:')      
        for msg in messages:
            for msg in messages:
                logging.info(f"От: {msg['from']['address']}, Тема: {msg['subject']}")      
                message_text = get_message_content(token, msg['id'])
                confirmation_link = extract_confirmation_link(message_text).replace(']','')
                logging.info(f"Ссылка для подтверждения: {confirmation_link}")
                browser_eset.get(confirmation_link)
    else:
        logging.debug("Сообщений пока нет.")
else:
    logging.debug("Ошибка получения токена.")

wait(browser_eset, 10).until(EC.visibility_of_element_located((By.XPATH, '//*[@id="main-content"]/div/div[1]/div/main/div/div/div[2]/div/div/div/div/div[2]/div/div/div/button')))
browser_eset.find_element(By.XPATH, '//*[@id="main-content"]/div/div[1]/div/main/div/div/div[2]/div/div/div/div/div[2]/div/div/div/button').click()

wait(browser_eset, 10).until(EC.visibility_of_element_located((By.XPATH, '//*[@id="license-add-new-slides"]/div/ion-slide[1]/div/div/div[3]/div/button')))
browser_eset.find_element(By.XPATH, '//*[@id="license-add-new-slides"]/div/ion-slide[1]/div/div/div[3]/div/button').click()

browser_eset.find_element(By.XPATH, '//*[@id="license-add-new-slides"]/div/ion-slide[1]/div/button').click()

wait(browser_eset, 10).until(EC.visibility_of_element_located((By.XPATH, '//*[@id="main-content"]/div/div/div/main/div/div/div[2]/div/div/div/div/div/div/div/div[1]/div/div/div/button')))
browser_eset.find_element(By.XPATH, '//*[@id="main-content"]/div/div/div/main/div/div/div[2]/div/div/div/div/div/div/div/div[1]/div/div/div/button').click()
browser_eset.find_element(By.XPATH, '//*[@id="main-content"]/div/div/div/main/div/div/div[2]/div/div/div/div/button[1]').click()

wait(browser_eset, 10).until(EC.visibility_of_element_located((By.XPATH, '//*[@id="main-content"]/div/div[1]/div/main/div/div/div[2]/div/div/div[2]/div/div/div/div/div[2]/div/div/div/button')))
browser_eset.find_element(By.XPATH, '//*[@id="main-content"]/div/div[1]/div/main/div/div/div[2]/div/div/div[2]/div/div/div/div/div[2]/div/div/div/button').click()
browser_eset.find_element(By.XPATH, '//*[@id="main-content"]/div/div[1]/div/main/div/div/div[2]/div/div/div[2]/div/button').click()

key = browser_eset.find_element(By.CLASS_NAME , 'css-1hznddj').text[221:]
logging.info(key)
print(key)