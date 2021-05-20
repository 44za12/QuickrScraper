from selenium import webdriver
from selenium.webdriver.remote.webdriver import WebDriver
from webdriver_manager.chrome import ChromeDriverManager
from time import sleep
import sys, os
from bs4 import BeautifulSoup
import json

import datetime
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC

from selenium.webdriver.common.action_chains import ActionChains

def attach_to_session(executor_url, session_id):
    original_execute = WebDriver.execute
    def new_command_execute(self, command, params=None):
        if command == "newSession":
            return {'success': 0, 'value': None, 'sessionId': session_id}
        else:
            return original_execute(self, command, params)
    WebDriver.execute = new_command_execute
    driver = webdriver.Remote(command_executor=executor_url, desired_capabilities={})
    driver.session_id = session_id
    WebDriver.execute = original_execute
    return driver


def sanitize(x):
    if not x: return
    x = x.strip().replace("\n","")
    return ' '.join(x.split())

def main():
    if len(sys.argv) > 2:
        driver = attach_to_session(sys.argv[1],sys.argv[2])
    else:
        driver = webdriver.Chrome(ChromeDriverManager().install())
        executor_url = driver.command_executor._url
        session_id = driver.session_id
        print(executor_url, session_id)

    if "firsttime" in sys.argv:
        updateconfig(None, None)

    previous, nextPage = readconfig()
    previous = 0 if not previous else previous
    cityName = sys.argv[3]
    nextPage = "https://www.quikr.com/jobs/hire/beautician+{}+zwqxj284607247".format(cityName) if not nextPage else nextPage
    driver.get(nextPage)
    if not len(sys.argv) > 2:
        sleep(200)

    driver.implicitly_wait(10)
    actions = ActionChains(driver)
    while nextPage:
        dcs = driver.find_elements_by_xpath("//div[@class='jsDetailsCard']")
        frange = range(len(dcs))[previous:]
        for i in frange:
            temp = {}
            profile_id = dcs[i].get_attribute("data-profileid")
            locationScript = 'document.getElementById("contact_{}").scrollIntoView();'.format(profile_id)
            driver.execute_script(locationScript)
            modalScript = WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.ID, 'contact_{}'.format(profile_id)))).get_attribute("onclick")
            driver.execute_script(modalScript+";")
            # sleep(1)
            soupContact = BeautifulSoup(driver.page_source,'html.parser')
            temp['Email'] = soupContact.find_all("a",class_="email")[0].text
            temp['Mobile'] = soupContact.find_all("a",class_="mobile")[0].text
            script = '''
                function closeAllModals() {

                    // get modals
                    const modals = document.getElementsByClassName('modal');

                    // on every modal change state like in hidden modal
                    for(let i=0; i<modals.length; i++) {
                    modals[i].classList.remove('show');
                    modals[i].setAttribute('aria-hidden', 'true');
                    modals[i].setAttribute('style', 'display: none');
                    }

                    // get modal backdrops
                    const modalsBackdrops = document.getElementsByClassName('modal-backdrop');

                    // remove every modal backdrop
                    for(let i=0; i<modalsBackdrops.length; i++) {
                    document.body.removeChild(modalsBackdrops[i]);
                    }
                }
                closeAllModals();
            '''
            driver.execute_script(script)
            # sleep(1)
            soup = BeautifulSoup(dcs[i].get_attribute("innerHTML"),'html.parser')
            try:
                temp['Name'] = soup.find_all("span", class_="job-type")[0].text
            except:
                pass
            try:
                temp['Age'] = soup.find_all("span", class_="candAge")[0].text
            except:
                pass
            try:
                temp['Role'] = soup.find_all("span", class_="post-role")[0].text
            except:
                pass
            try:
                location = soup.find_all("span", class_="jsLocality")[0].text
                try:
                    location, city = location.split(",")
                except:
                    city = location
                    location = "Not Found"
                temp['Location'] = location
                temp['City'] = city
            except:
                pass
            try:
                temp['Education'] = soup.find('li', {'title' : 'Education'}).text
            except:
                pass
            try:
                temp['Experience'] = soup.find('li', {'title' : 'Experience'}).text
            except:
                pass
            try:
                temp['Salary'] = soup.find('li', {'title' : 'Salary'}).text
            except:
                pass
            try:
                temp['Job Type'] = soup.find_all("span", class_="jobTypeDesc")[0].text
            except:
                pass
            attrList = soup.find_all("ul", class_="emp-list")[0].find_all('li')
            for j in attrList:
                try:
                    title = j.find('span', {'class' : 'emp-heading'}).text
                    if title == "Hello English score": continue
                    value = j.find('span', {'class' : 'jsProfileItem'}).get('title', None)
                    temp[title] = value
                except:
                    pass
            updateDb(temp)
            updateconfig(i, nextPage)
        try:
            nextPage = driver.find_element_by_xpath("//a[@aria-label='Next']").get_attribute("href")
            driver.get(nextPage)
        except:
            nextPage = None

def updateDb(temp):
    # name = "ambala.json"
    name = sys.argv[3]+".json"
    if not os.path.exists(name):
        data = json.dumps([temp])
        with open(name,"w") as f:
            f.write(data)
    else:
        with open(name,"r") as fr:
            data = json.loads(fr.read())
            data.append(temp)
        with open(name,"w") as fw:
            data = json.dumps(data)
            fw.write(data)

def updateconfig(profileid, url):
    with open("config", "w") as f:
        f.write("{} {}".format(profileid, url))

def readconfig():
    with open("config", "r") as f:
        data = f.read()
    pid, url = data.split()
    if eval(pid):
        pid, url = int(pid), url
    else:
        pid, url = None, None
    return pid, url

if __name__ == '__main__':
    main()