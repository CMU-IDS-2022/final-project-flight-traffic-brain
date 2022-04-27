import pickle
from selenium import webdriver
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.chrome.options import Options
from bs4 import BeautifulSoup
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time
chrome_options = webdriver.ChromeOptions()
chrome_options.add_argument('--headless')



origin = pickle.load(open('OriginState.sav','rb'))
dest = pickle.load(open('DestState.sav','rb'))
origin[:] = map(lambda x: x.replace(' ',"%20"), origin) 
dest[:] = map(lambda x: x.replace(' ',"%20"), dest) 
miles = []

browser = webdriver.Chrome("chromedriver",options=chrome_options)
for og in dest:
    for de in dest[1:]:
        url = 'https://www.mapdevelopers.com/mileage_calculator.php?&from=%s&to=%s' % (og, de)
        browser.get(url)
        time.sleep(2)
        html = browser.page_source
        soup = BeautifulSoup(html,'html.parser')
        # Find the required tag
        status_flight = soup.find(id="status_flight")
        start = status_flight.get_text().find(":")+2
        end = status_flight.get_text().find("miles")
        #print([og.replace("%20"," "), de.replace("%20"," "), float(status_flight.get_text()[start:end])])
        miles.append([og.replace("%20"," "), de.replace("%20"," "), float(status_flight.get_text()[start:end])])
browser.quit()

browser = webdriver.Chrome("chromedriver",options=chrome_options)
og_extra = (set(origin)-set(dest)).pop()
for de in dest:
    url = 'https://www.mapdevelopers.com/mileage_calculator.php?&from=%s&to=%s' % (og_extra, de)
    browser.get(url)
    time.sleep(2)
    html = browser.page_source
    soup = BeautifulSoup(html,'html.parser')
    # Find the required tag
    status_flight = soup.find(id="status_flight")
    start = status_flight.get_text().find(":")+2
    end = status_flight.get_text().find("miles")
    #print([og_extra.repalce("%20"," "), de.replace("%20"," "), float(status_flight.get_text()[start:end])])
    miles.append([og_extra.repalce("%20"," "), de.replace("%20"," "), float(status_flight.get_text()[start:end])])
browser.quit()


#pickle.dump(miles,open("miles.sav",'wb'))
miles_dic= {(i[0],i[1]):i[2] for i in miles}
#miles_dic
pickle.dump(miles_dic,open("miles_dic.sav",'wb'))
