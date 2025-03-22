import random
import string
import time
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import NoSuchElementException, TimeoutException

def get_accounts():
    """讀取 input.txt，並返回 email, password 的列表"""
    valid_accounts = []
    
    with open("input.txt", "r", encoding="utf-8") as f:
        lines = [line.strip() for line in f if line.strip()]  # 去除空行
    
    for line in lines:
        parts = line.split("----", 1)  # 只分割一次，避免密碼中有冒號
        if len(parts) == 2:  # 確保格式正確
            valid_accounts.append(parts)
    
    # 移除已讀取的帳號
    with open("input.txt", "w", encoding="utf-8") as f:
        f.writelines("\n".join(lines[len(valid_accounts):]))  # 只保留未處理的帳號
    
    return valid_accounts

def generate_random_name():
    """生成 5~16 位隨機大小寫字母與數字"""
    return ''.join(random.choices(string.ascii_letters + string.digits, k=random.randint(5, 16)))

def process_account(email, password):
    """處理單個帳戶登入與變更名稱"""
    random_name = generate_random_name()
    print(f"處理帳戶: {email}, 新名稱: {random_name}")

    # 設置 WebDriver（顯示前台瀏覽器）
    options = webdriver.ChromeOptions()
    options.add_argument("--window-size=1280,800")  # 設定視窗大小
    driver = webdriver.Chrome(options=options)
    wait = WebDriverWait(driver, 15)  # 設定最多等待 15 秒

    try:
        # 1. 打開登入頁面
        driver.get("https://sisu.xboxlive.com/connect/XboxLive/?state=login&cobrandId=8058f65d-ce06-4c30-9559-473c9275a65d&tid=896928775&ru=https%3A%2F%2Fwww.minecraft.net%2Fzh-hant%2Flogin&aid=1142970254")

        # 2. 等待 email 輸入框出現
        email_input = wait.until(EC.presence_of_element_located((By.ID, "usernameEntry")))
        email_input.send_keys(email + Keys.RETURN)

        # 3. 等待密碼輸入框出現
        password_input = wait.until(EC.presence_of_element_located((By.ID, "passwordEntry")))
        password_input.send_keys(password + Keys.RETURN)

        # 4. 檢查「略過」按鈕，直到它消失
        while True:
            try:
                skip_button = driver.find_element(By.ID, "iShowSkip")
                skip_button.click()
                time.sleep(2)
            except NoSuchElementException:
                break  # 找不到「略過」按鈕，代表已跳過

        # 5. 點擊「否」按鈕
        try:
            no_button = wait.until(EC.element_to_be_clickable((By.XPATH, '//button[@data-testid="secondaryButton"]')))
            no_button.click()
        except TimeoutException:
            pass  # 如果按鈕不存在，就跳過

        # **✅ 6. 等待網頁跳轉到變更名稱頁面**
        wait.until(EC.url_contains("msaprofile"))

        # 7. 點擊變更名稱按鈕
        try:
            change_name_link = wait.until(EC.element_to_be_clickable((By.XPATH, '//a[@data-aem-contentname="Change Profile Name"]')))
            change_name_link.click()
        except TimeoutException:
            print(f"帳戶 {email} 未找到變更名稱選項")
            raise Exception("未找到變更名稱選項")

        # 8. 等待名稱輸入框可用
        name_input = wait.until(EC.element_to_be_clickable((By.ID, "change-java-profile-name")))
        name_input.clear()
        name_input.send_keys(random_name)

        # 9. 等待「設定個人資料名稱」按鈕變成可點擊狀態
        update_button = wait.until(EC.element_to_be_clickable((By.XPATH, '//button[contains(@class, "change-profile-name__update-btn")]')))
        update_button.click()

        # **✅ 等待 3 秒，確保名稱設置成功**
        time.sleep(3)

        # 10. 記錄到 output.txt（確保每次寫入都換行）
        with open("output.txt", "a", encoding="utf-8") as f:
            f.write(f"\n{email}----{password}----{random_name}")

        print(f"帳戶 {email} 變更成功，已記錄")

    except Exception as e:
        print(f"帳戶 {email} 發生錯誤: {e}")
        # **將錯誤的帳戶記錄到 fail.txt**
        with open("fail.txt", "a", encoding="utf-8") as f:
            f.write(f"\n{email}----{password}")

    finally:
        driver.quit()

if __name__ == "__main__":
    accounts = get_accounts()
    
    if not accounts:
        print("❌ 沒有有效的帳戶可處理，請檢查 input.txt 格式")
    else:
        print(f"🔄 檢測到 {len(accounts)} 個帳戶，將依序處理")

        for email, password in accounts:
            process_account(email, password)
            print(f"✅ 帳戶 {email} 完成，等待 1 秒後處理下一個...")
            time.sleep(1)  # 確保每個帳號處理後再進行下一個
