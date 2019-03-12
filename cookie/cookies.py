import time
from selenium.common.exceptions import TimeoutException
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from os.path import abspath, dirname
import requests
from chaojiying import Chaojiying_Client
from retrying import retry



class WeiboCookies():
    def __init__(self, username, password, browser):
        self.url = 'https://weibo.com/'
        self.browser = browser
        self.wait = WebDriverWait(self.browser, 20)
        self.username = username
        self.password = password
    
    def open(self):
        """
        打开网页输入用户名密码并点击
        :return: None
        """
        self.browser.delete_all_cookies()
        self.browser.get(self.url)
        username = self.wait.until(EC.presence_of_element_located((By.ID, 'loginname')))
        password = self.wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, '.info_list.password div input')))
        submit = self.wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, '.W_btn_a.btn_32px')))
        username.send_keys(self.username)
        password.send_keys(self.password)
        time.sleep(1)
        submit.click()
    
    def password_error(self):
        """
        判断是否密码错误
        :return:
        """
        try:
            return WebDriverWait(self.browser, 5).until(
                EC.text_to_be_present_in_element((By.CSS_SELECTOR, 'span[node-type="text"]'), '用户名或密码错误。'))
        except TimeoutException:
            return False
    
    def login_successfully(self):
        time.sleep(3)
        """
        判断是否登录成功
        :return:
        """
        try:
            return bool(
                WebDriverWait(self.browser, 5).until(EC.presence_of_element_located((By.CLASS_NAME, 'nameBox'))))
        except TimeoutException:
            return False

    def retry_if_result_none(result):
        return result is None

    @retry(retry_on_result=retry_if_result_none,)
    def Captcha_Crack(self):
        time.sleep(2)
        imglab = self.wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, '.code.W_fl')))
        imageURL = self.findElement(By.CSS_SELECTOR(".code.W_fl img")).getAttribute("src")
        imgfile = dirname(abspath(__file__)) + '/captcha.png'
        byte = requests.get(imageURL, headers={'User-Agent': 'Mozilla/5.0'})
        with open(imgfile, 'wb') as f:
            f.write(byte.content)
        chaojiying = Chaojiying_Client('dongxuxiang', 'dxx15950092787', '898583')
        Img = open(imgfile, 'rb').read()
        CAPTCHA = chaojiying.PostPic(Img, 1902)['pic_str']
        Input = self.findElement(By.CSS_SELECTOR(".input_wrap.W_fl input"))
        Input.send_keys(CAPTCHA)
        login = self.findElement(By.CSS_SELECTOR(".W_btn_a.btn_32px"))
        login.click()
        if WebDriverWait(self.browser, 5).until(EC.text_to_be_present_in_element((By.CSS_SELECTOR, 'span[node-type="text"]'), '用户名或密码错误。查看帮助')):
            return 2
        else:
            if WebDriverWait(self.browser, 5).until(EC.text_to_be_present_in_element((By.CSS_SELECTOR, 'span[node-type="text"]'), '输入的验证码不正确')):
                return None
            else:
                return 1

    def get_cookies(self):
        """
        获取Cookies
        :return:
        """
        return self.browser.get_cookies()
    
    def main(self):
        """
        破解入口
        :return:
        """
        self.open()
        if self.password_error():
            return {
                'status': 2,
                'content': '用户名或密码错误'
            }
        # 如果不需要验证码直接登录成功
        if self.login_successfully():
            cookies = self.get_cookies()
            return {
                'status': 1,
                'content': cookies
            }
        login_status = self.Captcha_Crack()
        if login_status == 1:
            cookies = self.get_cookies()
            return {
                'status': 1,
                'content': cookies
            }
        else:
            return {
                'status': 2,
                'content': '用户名或密码错误'
            }


if __name__ == '__main__':
    browser = webdriver.Chrome()
    result = WeiboCookies('15950092787', 'Dongxuxiang', browser).main()
    print(result)
