#Import libraries
from bs4 import BeautifulSoup
import requests
from selenium import webdriver
import time
from selenium.webdriver.firefox.options import Options
import mysql.connector
from mysql.connector import errorcode
import re
#------------------------------------------

#def funcs
def combine(first_list,second_list):

    in_first = set(first_list)
    in_second = set(second_list)

    in_second_but_not_in_first = in_second - in_first

    return  first_list + list(in_second_but_not_in_first)

def strToInt (txt):
    p=r'([۰۱۲۳۴۵۶۷۸۹]+٫{0,1}[۰۱۲۳۴۵۶۷۸۹]*٫{0,1}[۰۱۲۳۴۵۶۷۸۹]*٫{0,1}[۰۱۲۳۴۵۶۷۸۹]*)'
    match=re.findall(p,txt)
    if len(match)>0 :
        return int(match[0].replace('٫',''))
    else : return 0
    

def createId(link):
    temp=link.split('/')    
    return(temp[-1])


def cleanstr(str):
    return str.replace('\u200c',' ')


#---------------------------------------------------------
#Constants
SCROLL_PAUSE_TIME=0.5  #s

#---------------------------------------------------------
#connect to database
cnx = mysql.connector.connect(user='root', password='',
                              host='127.0.0.1',
                              database='carDB')
cursor=cnx.cursor()                              


#Get 100 items
url='https://divar.ir/s/tehran/car'
options = Options()
options.headless = True
driver=webdriver.Firefox(firefox_options=options)
driver.get(url)


soup=BeautifulSoup(driver.page_source,'html.parser')
results=soup.findAll('a',class_="kt-post-card")

while(len(results)<1000):
    
    # Get scroll height
    last_height = driver.execute_script("return document.body.scrollHeight")

    for i in range (0,8):
        # Scroll down to bottom
        driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")

        # Wait to load page
        time.sleep(SCROLL_PAUSE_TIME)

        # Calculate new scroll height and compare with last scroll height
        new_height = driver.execute_script("return document.body.scrollHeight")
        if new_height == last_height:
            break
        last_height = new_height
        i+=1
    soup=BeautifulSoup(driver.page_source,'html.parser')
    temp_list=soup.findAll('a',class_="kt-post-card")
    results=combine(results,temp_list)



#get pages and extract data and store in database
for result in results :
    link='https://divar.ir'+result['href']
    new_page=requests.get(link)
    id=createId(link)
    if new_page.status_code == 200 :
        

        soup1=BeautifulSoup(new_page.text,'html.parser')

        brandvamodel=soup1.find('p',text='برند و مدل')
        if brandvamodel==None :
            print (link)
            continue
        a_tag=brandvamodel.find_next('a',class_="kt-unexpandable-row__action kt-text-truncate").getText().split('،')
        if(len(a_tag)<3) : 
            a_tag.append('')
            a_tag.append('')

        span_tag=soup1.findAll('span',class_='kt-group-row-item__title kt-body kt-body--sm')
        km=strToInt(span_tag[0].find_next('span').getText())
        date=strToInt(span_tag[1].find_next('span').getText())
        color=span_tag[2].find_next('span').getText()

        body=soup1.find('p',text='وضعیت بدنه')
        if body!=None :
            body_status=body.find_next('p',class_="kt-unexpandable-row__value").getText()
        else : 
            body_status=''
        
  
        price_tag=soup1.find('p',text='قیمت')
        price=price_tag.find_next('p',class_="kt-unexpandable-row__value").getText()
        if strToInt(price)==0 :
            continue
        else: price=strToInt(price)
        
        try:
            cursor.execute('''INSERT INTO car VALUES (\'{id}\',
                \'{brand}\',\'{model}\',\'{tip}\',{km},{date},\'{color}\',\'{body}\',\'{price}\')'''
                .format(id=id,brand=cleanstr(a_tag[0]),model=cleanstr(a_tag[1]),tip=cleanstr(a_tag[2]),km=km,
                       date=date,color=cleanstr(color),body=cleanstr(body_status),price=price))
            cnx.commit()
        except mysql.connector.Error as err:
            print(err)
            continue
            



cursor.close()
cnx.close()
driver.quit()

