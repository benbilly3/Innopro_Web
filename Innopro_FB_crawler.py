from selenium import webdriver
from selenium.webdriver.common.keys import Keys

from datetime import datetime

import pandas as pd
import time, math, os, re, random

from config import facebook_account, facebook_password

def loginToFacebook(browser, email, password):
    facebook_url = 'https://www.facebook.com/'
    browser.get(facebook_url)
    time.sleep(3)
    #login
    search=browser.find_element_by_id('email')
    search.send_keys(email)#填mail
    time.sleep(3)
    search=browser.find_element_by_id('pass')
    search.send_keys(password)#填密碼
    search.send_keys(Keys.RETURN) # hit return after you enter search text,使用Keys物件功能


def getPostOrderData(browser, orderUrl):
    # 回傳：商品ID、Po文日期、爬文日期/時間
    # 所有留言的：用戶名稱、用戶facebookUrl、留言時間、訂單數量、留言原文
    browser.get(orderUrl) #進入商品貼文網址
    comments = pd.DataFrame(columns=['username','fbURL','commentTime','orderCount','commentContent'])

    totalCommentsCount = re.search(r'\d+', browser.find_element_by_xpath("//a[@data-testid='UFI2CommentsCount/root']").text).group()                            

    # 若留言超過50則，需點開留言
    if int(totalCommentsCount) >50:
        loadCommentButton = browser.find_element_by_xpath("//a[@data-testid='UFI2CommentsPagerRenderer/pager_depth_0']")
        pressTime = math.floor(int(TotalCommentsCount)/50)
        for i in range (pressTime):
            loadCommentButton.click()
            time.sleep(3)

    #抓取留言資料
    comments_list = browser.find_element_by_xpath(".//div[@data-testid='UFI2CommentsList/root_depth_0']")
    comment_roots = comments_list.find_elements_by_xpath(".//div[@data-testid='UFI2Comment/root_depth_0']")
    for index, comment_root in enumerate(comment_roots):
        
        comment_body = comment_root.find_element_by_xpath(".//div[@data-testid='UFI2Comment/body']")
        username = comment_body.find_element_by_xpath(".//a[contains(@data-hovercard,'')]").text
        comment_content = comment_body.text.split(' ')[-1]
        order_count = comment_content.replace('+','').replace('＋','')
        fbUrl = comment_root.find_element_by_xpath(".//a[contains(@href,'/')]").get_attribute('href')
        
        comment_time = comment_root.find_element_by_tag_name('abbr').get_attribute('data-tooltip-content')

        comments.loc[index] = (username,fbUrl,comment_time,order_count,comment_content)

    #有兩種形式
    if browser.find_elements_by_class_name('_3w8y')!=[]:
        tag = browser.find_elements_by_class_name('_3w8y')
    else:
        tag = browser.find_elements_by_tag_name('p')


    wine_main=[tag[i].text for i in range(len(tag))]#抓取商品內容主文
    #抓<p>標籤第一行的"wineID"
    index_data=wine_main[0]    
    wine_id=index_data[index_data.find("-")+1:index_data.find(">")]
    comments["wineID"]=wine_id

    #抓<p>標籤第一行的"publishDate(團購發布年月)"、"crawlDate(爬取時間)"
    year=index_data[1:5]
    month=index_data[index_data.find("/")+1:index_data.find("月")]
    publish_date = datetime.strptime(year+'-'+month, '%Y-%m')
    crawl_day=datetime.now().strftime('%Y-%m-%d %H:%M')

    comments["publishDate"]=publish_date
    comments["crawlDate"]=crawl_day

    #過濾掉非數字留言
    comments["orderCount"]=comments["orderCount"].apply(lambda s:pd.to_numeric(s,errors='coerce'))
    df = comments.dropna()
    return df, year, month, wine_id

def InnoproFBCrawler(email,password,orderUrl):
    #跳過chrome通知允許alert windows
    #driverpath="/Users/benbilly3/Desktop/創潮爬蟲/chromedriver"#74版，win的省略
    
    # 設定 pandas col 顯示字數
    pd.set_option('max_colwidth',200)
    
    #chromedriver 放在專案資料夾下
    currentPath = os.getcwd()
    driverPath = currentPath + '/chromedriver'

    options = webdriver.ChromeOptions()
    prefs = {'profile.default_content_setting_values' :{'notifications' : 2}}
    options.add_experimental_option('prefs',prefs)

    #操控chromedriver
    browser = webdriver.Chrome(executable_path=driverPath,options = options)#模擬瀏覽器，跳過通知允許

    loginToFacebook(browser, facebook_account, facebook_password)
    
    time.sleep(60)
    
    df, year, month, wine_id = getPostOrderData(browser, orderUrl)

    if not os.path.exists(currentPath+"/Innopro_crawl_data/"):
        os.mkdir("Innopro_crawl_data")
    if not os.path.exists(currentPath+"/Innopro_crawl_data/"+year+month):
        os.mkdir("Innopro_crawl_data/"+year+month)

    df.to_csv(currentPath+"/Innopro_crawl_data/"+year+month+'/'+year+month+"_"+wine_id+".csv")
    
    browser.close()