import requests
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
import time
import os

# إعداد WebDriver
options = webdriver.ChromeOptions()
options.add_argument('--headless')
options.add_argument('--no-sandbox')
options.add_argument('--disable-dev-shm-usage')

service = Service(ChromeDriverManager().install())
driver = webdriver.Chrome(service=service, options=options)

# إعداد بوت تليجرام
TELEGRAM_BOT_TOKEN = os.getenv('TELEGRAM_BOT_TOKEN')
TELEGRAM_CHAT_ID = os.getenv('TELEGRAM_CHAT_ID')

def get_binance_price(symbol):
    url = f'https://api.binance.com/api/v3/ticker/price?symbol={symbol}'
    response = requests.get(url)
    data = response.json()
    print(f"Response from Binance API: {data}")  # طباعة الاستجابة للتحقق
    return float(data['price'])

def send_telegram_message(token, chat_id, text):
    url = f'https://api.telegram.org/bot{token}/sendMessage'
    payload = {
        'chat_id': chat_id,
        'text': text
    }
    requests.post(url, data=payload)

try:
    # التحقق من إعدادات WebDriver
    driver.get('https://www.google.com')
    print("Google page title:", driver.title)

    # الانتقال إلى صفحة Velar Swap
    driver.get('https://app.velar.co/swap')
    print("Velar Swap page loaded.")
    
    # إعطاء وقت كافي لتحميل الصفحة والمحتوى الديناميكي
    time.sleep(10)

    # تغيير العملة إلى aeUSDC
    to_currency_dropdown = driver.find_element(By.XPATH, '//*[@id="root"]/div[2]/div/div/div/div/div[2]/div[2]/div[1]/div/div/button/h4')
    to_currency_dropdown.click()
    time.sleep(5)
    aeusdc_option = driver.find_element(By.XPATH, '//*[@id="tokenSelectionModal"]/div/div[3]/div/button[3]')
    aeusdc_option.click()
    time.sleep(5)
    print("Currency changed to aeUSDC.")

    # إدخال قيمة STX ثم حذفها وإعادة إدخالها
    stx_input = driver.find_element(By.XPATH, '//*[@id="root"]/div[2]/div/div/div/div/div[2]/div[1]/div[2]/div[1]/input')
    stx_input.clear()
    stx_input.send_keys('1')
    time.sleep(2)
    stx_input.clear()
    time.sleep(2)
    stx_input.send_keys('1')
    print("STX value set to 1.")

    # إعطاء وقت كافي لتحديث السعر
    time.sleep(5)

    # استخراج سعر aeUSDC المقابل
    aeusdc_value = driver.find_element(By.XPATH, '//*[@id="root"]/div[2]/div/div/div/div/div[2]/div[2]/div[2]/div[1]/input').get_attribute('value')
    time.sleep(5)

    # طباعة النتائج
    results = f'1 STX = {aeusdc_value} aeUSDC\n'
    print(results)

    # أخذ سعر STX/USDT من Binance
    stx_usdt_price = get_binance_price('STXUSDT')
    results += f'STX/USDT price on Binance: {stx_usdt_price}\n'
    print(results)

    # حساب قيمة 500 aeUSDC مقابل STX في Velar
    aeusdc_value_float = float(aeusdc_value)
    stx_amount_from_500_aeusdc = 500 / aeusdc_value_float
    results += f'500 aeUSDC = {stx_amount_from_500_aeusdc} STX on Velar\n'

    # حساب قيمة STX الناتجة في USDT على Binance
    usdt_value_from_stx = stx_amount_from_500_aeusdc * stx_usdt_price
    results += f'{stx_amount_from_500_aeusdc} STX = {usdt_value_from_stx} USDT on Binance\n'

    # حساب قيمة 500 USDT من STX في Velar
    stx_amount_from_500_usdt = 500 / stx_usdt_price
    aeusdc_value_from_500_usdt = stx_amount_from_500_usdt * aeusdc_value_float
    results += f'500 USDT = {stx_amount_from_500_usdt} STX on Binance\n'
    results += f'{stx_amount_from_500_usdt} STX = {aeusdc_value_from_500_usdt} aeUSDC on Velar\n'

    # تحليل واقتراح الشراء أو البيع
    if usdt_value_from_stx > 500:
        results += "اقتراح: اشترِ STX في Velar وبيعها في Binance لتحقيق ربح.\n"
    else:
        results += "اقتراح: لا توجد فرصة للربح عند شراء STX في Velar وبيعها في Binance.\n"

    if aeusdc_value_from_500_usdt > 500:
        results += "اقتراح: اشترِ STX في Binance وبيعها في Velar لتحقيق ربح.\n"
    else:
        results += "اقتراح: لا توجد فرصة للربح عند شراء STX في Binance وبيعها في Velar.\n"

    # إرسال النتائج إلى تليجرام
    send_telegram_message(TELEGRAM_BOT_TOKEN, TELEGRAM_CHAT_ID, results)
    print("Results sent to Telegram.")

finally:
    # إغلاق المتصفح
    driver.quit()
    print("Browser closed.")
