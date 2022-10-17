import datetime
import os
from threading import Thread
import requests
import re
import time
import dingding
from requests.adapters import HTTPAdapter
from requests.packages.urllib3.util.retry import Retry


class LoginError(Exception):
    """Login Exception"""
    pass


class ZJULogin(object):
    """
    Attributes:
        username: (str) 浙大统一认证平台用户名（一般为学号）
        password: (str) 浙大统一认证平台密码
        sess: (requests.Session) 统一的session管理
    """
    
    headers = {
        'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/100.0.4896.127 Safari/537.36',
    }
    
    # URL
    BASE_URL = "https://courses.zju.edu.cn/api/todos?no-intercept=true"
    LOGIN_URL = "https://zjuam.zju.edu.cn/cas/login?service=http%3A%2F%2Fservice.zju.edu.cn%2F"

    def __init__(self, username, password):
        self.username = username
        self.password = password
        self.sess = requests.Session()
        
        # 这将GETURL 和重试 3 次，以防requests.exceptions.ConnectionError. 
        # backoff_factor将有助于在尝试之间应用延迟，以避免在定期请求配额的情况下再次失败。
        self.retry = Retry(connect=3, backoff_factor=0.5)
        self.adaptor = HTTPAdapter(max_retries=self.retry)
        self.sess.mount('http://', self.adaptor)
        self.sess.mount('https://', self.adaptor)

    def login(self):
        """Login to ZJU platform"""
        try:
            res = self.sess.get(self.BASE_URL)
        except res.exception.ConnectionError:
            res.status_code = "Connection refused"
         
        time.sleep(1)   # 等待一秒
            
        execution = re.search(
            'name="execution" value="(.*?)"', res.text).group(1)
        res = self.sess.get(
            url='https://zjuam.zju.edu.cn/cas/v2/getPubKey').json()
        n, e = res['modulus'], res['exponent']
        encrypt_password = self._rsa_encrypt(self.password, e, n)

        data = {
            'username': self.username,
            'password': encrypt_password,
            'execution': execution,
            '_eventId': 'submit',
            "authcode": ""
        }
        res = self.sess.post(url=self.LOGIN_URL, data=data)
        # check if login successfully
        if '用户名或密码错误' in res.content.decode():
            raise LoginError('登录失败，请核实账号密码重新登录')
        print("统一认证平台登录成功~")
        return self.sess

    def _rsa_encrypt(self, password_str, e_str, M_str):
        password_bytes = bytes(password_str, 'ascii')
        password_int = int.from_bytes(password_bytes, 'big')
        e_int = int(e_str, 16)
        M_int = int(M_str, 16)
        result_int = pow(password_int, e_int, M_int)
        return hex(result_int)[2:].rjust(128, '0')


class getdll(ZJULogin):
    """
    Attributes:
        get请求"https://courses.zju.edu.cn/api/todos?no-intercept=true" 返回列表

    """

    def __init__(self, username, password):
        super().__init__(username, password)
        self.login()

    def getddl(self):
        res = self.sess.get(self.BASE_URL)
        try:
            res = res.json()['todo_list']
            for event in res:
                self.compare(event)
        except:
            raise LoginError('获取数据失败')

    def compare(self, event):
        # 获取当前UTC时间
        daynow = time.strftime('%Y-%m-%d', time.localtime(time.time()))
        timenow = time.strftime('%H:%M', time.localtime(time.time()))

        event_time = str(event.get('end_time'))
        endtime = re.findall('(.*)T(.*?):00Z', event_time) # 这里用到正则提取，贪婪的概念可以自行搜索
        
        # 有可能event获取的内容为空，因此需要进行过滤
        if not endtime:
            return
        else:
            endtime = endtime[0]

        endday = datetime.datetime.strptime(endtime[0], '%Y-%m-%d')
        endhour = datetime.datetime.strptime(endtime[1], '%H:%M')

        # 时区问题，endhour加八小时；GitHub上的时间是UTC时间,而不是北京时间，本机调试记得把下面注释去掉
        # endhour += datetime.timedelta(hours=8)
        
        # 获得剩余天数，剩余小时数，剩余分钟数
        dayleft = (
            endday-datetime.datetime.strptime(daynow, '%Y-%m-%d')).days
        hourleft = (
            endhour-datetime.datetime.strptime(timenow, '%H:%M')).seconds//3600
        minuteleft = (
            endhour-datetime.datetime.strptime(timenow, '%H:%M')).seconds//60-hourleft*60
        
        if dayleft > 0 and dayleft < 7:
            self.reminder(event.get('course_name')+'作业 ' +
                  event.get('title') + ' : 剩余时间'+str(dayleft)+'天')
            print(event.get('course_name')+'作业 ' +
                  event.get('title') + ' : 剩余时间'+str(dayleft)+'天')
        if dayleft == 0 and hourleft > 0:
            self.reminder(event.get('course_name')+'作业 ' +
                  event.get('title') + ' : 剩余时间'+str(round(hourleft))+'小时' + str(minuteleft)+'分钟')
            print(event.get('course_name')+'作业 ' +
                  event.get('title') + ' : 剩余时间'+str(round(hourleft))+'小时' + str(minuteleft)+'分钟')
            self.reminder('再不写真要寄了')

    def reminder(self, content):
        title = 'DDL小助手提醒您:'
        dingding.dingding_bot(title, content)
    
    def run(self):
        self.getddl()

if __name__ == '__main__':
    username = os.getenv('ZJU_USERNAME')
    password = os.getenv('ZJU_PASSWORD')
    getdll(username, password).run()
