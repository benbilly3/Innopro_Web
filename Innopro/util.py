from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.common.exceptions import NoSuchElementException, StaleElementReferenceException

from datetime import datetime

import pandas as pd
import time
import math
import os
import re
import random
import pickle

from tqdm import tqdm


def initBrowser():

    # chromedriver 放在專案資料夾下，並命名為 chromedriver
    currentPath = os.getcwd()
    driverPath = currentPath + '/chromedriver'

    options = webdriver.ChromeOptions()
    prefs = {'profile.default_content_setting_values': {'notifications': 2}}
    options.add_experimental_option('prefs', prefs)
    # options.add_argument("--headless")

    browser = webdriver.Chrome(
        executable_path=driverPath, options=options)  # 模擬瀏覽器，跳過通知允許

    return browser


def loginToFacebook(browser, email, password):
    print('logging in to fb')
    facebook_url = 'https://www.facebook.com/'
    browser.get(facebook_url)

    time.sleep(3)

    # Load Cookies
    cookies = pickle.load(open("cookies.pkl", "rb"))
    for cookie in cookies:
        browser.add_cookie(cookie)

    browser.refresh()
    time.sleep(2)

    try:
        # login
        email_field = browser.find_element_by_id('email')
        email_field.send_keys(email)  # 填mail
        time.sleep(1)
        pw_field = browser.find_element_by_id('pass')
        pw_field.send_keys(password)  # 填密碼
        # hit return after you enter search text,使用Keys物件功能
        pw_field.send_keys(Keys.RETURN)

        print('login success')

        # update cookies
        cookies = browser.get_cookies()
        for cookie in cookies:
            if isinstance(cookie.get('expiry'), float):
                cookie['expiry'] = int(cookie['expiry'])
        pickle.dump(cookies, open("cookies.pkl", "wb"))
        print('cookies updated')

    except Exception as e:
        if 'no such element' in e.msg:
            print('You already logged in')
        else:
            print(e)


def getPostLinks(browser, groupUrl, keywords):

    browser.get(groupUrl)
    time.sleep(5)
    # 滾動到頁面底部
    # Get scroll height
    last_height = browser.execute_script("return document.body.scrollHeight")

    print('scrolling posts')
    isBottom = False

    # prevent infinite loop
    counter = 0

    while isBottom == False and counter < 99:
        browser.execute_script(
            "window.scrollTo(0, document.body.scrollHeight);")

        try:
            # group_pager 是社團底部 '查李王 and 6,039 other people are in this group. ... See All Members' 這個 element
            group_pager = browser.find_element_by_xpath(
                "//div[contains(@class,'groupsStreamMemeberBox')]")
        except NoSuchElementException:
            # 還沒到底部，會出現此 Error 為正常
            pass
        except Exception as e:
            print(e.msg)
        else:
            isBottom = True

        counter += 1
        time.sleep(random.randint(3, 5))

    time.sleep(2)

    browser.execute_script("window.scrollTo(0,0)")

    time.sleep(3)

    see_more_links = browser.find_elements_by_xpath(
        '//span[@class="text_exposed_link"]')

    print('clicking see more buttons')
    for index, see_more in enumerate(see_more_links):
        try:
            el_offsetTop = see_more.location['y'] - 300
            browser.execute_script(
                "window.scrollTo(0, {});".format(el_offsetTop))
            see_more.click()

        except Exception as e:
            print('erro while clicking {}th post\'s see more link'.format(index))
            print(e)
        time.sleep(1)

    # get_attribute取出貼文超連結
    posts = browser.find_elements_by_xpath(
        '//div[@class="_5pcr userContentWrapper"]')

    # 刪除非賣酒文的 po 文
    print('removing non-selling posts')
    for index, post in enumerate(posts[:]):
        if '出貨名單' in post.text or '宅配' in post.text or '結束按讚活動' in post.text:
            posts.remove(post)
        elif keywords in post.text:
            pass
        else:
            posts.remove(post)

    print('processing all item\'s information')
    postsdata = pd.DataFrame(
        columns=['item_id', 'year', 'month', 'item_name', 'link', 'price'])
    for index, post in enumerate(posts):

        link = post.find_element_by_class_name('_5pcq').get_attribute('href')
        post_preview = post.text
        post_preview = post_preview.replace('：', ':').replace('　', ' ').replace('＄', '$')
        item_name_word = "酒名:" if "酒名:" in post_preview else "品名:"
        item_name = post_preview[post_preview.find(
            item_name_word)+3:post_preview.find("\n", post_preview.find(item_name_word))]

        secondHeartPos = post_preview.find("\n<3", post_preview.find("\n<3")+1)
        thirdHeartPos = post_preview.find("<3\n")

        price = post_preview[secondHeartPos+4:thirdHeartPos-1].replace('X', '0').replace('x', '0')
        # 去除掉怪異的後綴詞
        price = ''.join(filter(lambda x: x.isdigit(), price))

        item_id = post_preview.split('-')[1]
        year = post_preview[post_preview.find("<")+1:post_preview.find("/")]
        month = post_preview[post_preview.find("/")+1:post_preview.find("月")]

        postsdata.loc[index] = (item_id, year, month,
                                item_name, link, price)
    return postsdata


def getPostOrderData(browser, postUrl, postDatas):
    # 回傳：商品 ID、Po 文日期、爬文日期/時間
    # 所有留言的：用戶名稱、用戶 facebookUrl、留言時間、訂單數量、留言原文
    # 在此階段會一併儲存整篇 po 文的 html，所以需要讀取 postsData 這個變數
    browser.get(postUrl)  # 進入商品貼文網址
    comments = pd.DataFrame(
        columns=['comment_order', 'username', 'fbuid', 'fbURL', 'commentTime', 'orderCount', 'commentContent'])

    try:
        loadCommentButton = browser.find_element_by_xpath(
            '//a[@data-testid="UFI2CommentsPagerRenderer/pager_depth_0"]'
        )
        print('comment counts more than 50')
        loadCommentOffsetY = loadCommentButton.location['y'] - 300
        browser.execute_script(
            "window.scrollTo(0, {});".format(loadCommentOffsetY))

    except NoSuchElementException:
        print('comment counts less than 50')
        print('all comments loaded')
        isAllCommentsLoaded = True
    except Exception as e:
        print(e.msg)
    else:
        isAllCommentsLoaded = False

    while isAllCommentsLoaded == False:
        try:
            loadCommentButton.click()
            time.sleep(0.5)
        except StaleElementReferenceException:
            print('all comments loaded')
            isAllCommentsLoaded = True
        except Exception as e:
            print(e.msg)

    # 抓取留言資料
    comments_list = browser.find_element_by_xpath(
        ".//div[@data-testid='UFI2CommentsList/root_depth_0']")
    comment_roots = comments_list.find_elements_by_xpath(
        ".//div[@data-testid='UFI2Comment/root_depth_0']")

    # FB 留言時間字串格式
    # https://docs.python.org/zh-cn/3/library/datetime.html#strftime-and-strptime-behavior
    datetime_format = "%A, %B %d, %Y at %I:%M %p"
    for index, comment_root in enumerate(comment_roots):
        comment_body = comment_root.find_element_by_xpath(
            ".//div[@data-testid='UFI2Comment/body']")
        username = comment_body.find_element_by_xpath(
            ".//a[contains(@data-hovercard,'')]").text

        profile_pic_a = comment_root.find_element_by_xpath(
            "div[contains(@class,'lfloat')]//a[contains(@data-hovercard,'user.php?id=')]")
        id_link = profile_pic_a.get_attribute('data-hovercard')
        fbuid = id_link[id_link.find('user.php?id=')+12:]
        comment_content = comment_body.text.split(' ')[-1]
        order_count = comment_content.replace('+', '').replace('＋', '')
        fbUrl = comment_root.find_element_by_xpath(
            ".//a[contains(@href,'/')]").get_attribute('href')

        comment_time = comment_root.find_element_by_tag_name(
            'abbr').get_attribute('data-tooltip-content')
        comment_time = datetime.strptime(comment_time, datetime_format)
        comments.loc[index] = (
            index, username, fbuid, fbUrl, comment_time, order_count, comment_content)

    post_and_comments_html = browser.find_element_by_xpath(
        "//div[@data-testid='newsFeedStream']").get_attribute('outerHTML')
    postDatas.at[postDatas['link'] == postUrl, 'html'] = post_and_comments_html

    # 有兩種形式
    if browser.find_elements_by_class_name('_3w8y') != []:
        tag = browser.find_elements_by_class_name('_3w8y')
    else:
        tag = browser.find_elements_by_tag_name('p')

    wine_main = [tag[i].text for i in range(len(tag))]  # 抓取商品內容主文
    # 抓<p>標籤第一行的"wineID"
    index_data = wine_main[0]
    wine_id = index_data[index_data.find("-")+1:index_data.find(">")]
    comments["wineID"] = wine_id

    # 抓<p>標籤第一行的"publishDate(團購發布年月)"、"crawlDate(爬取時間)"
    year = index_data[1:5]
    month = index_data[index_data.find("/")+1:index_data.find("月")]
    publish_date = datetime.strptime(year+'-'+month, '%Y-%m')
    crawl_day = datetime.now().strftime('%Y-%m-%d %H:%M')

    comments["publishDate"] = publish_date
    comments["crawlDate"] = crawl_day

    # 過濾掉非數字留言
    comments["orderCount"] = comments["orderCount"].apply(
        lambda s: pd.to_numeric(s, errors='coerce'))
    df = comments.dropna()
    df = df[df.orderCount != 0]
    df = df.drop_duplicates(subset=['orderCount', 'fbURL'], keep="first")
    df = df.groupby('fbURL', as_index=False).max()
    return df, year, month, wine_id
