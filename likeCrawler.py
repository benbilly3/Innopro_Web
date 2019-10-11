from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.common.exceptions import NoSuchElementException, StaleElementReferenceException

from datetime import datetime

import time
import math
import os
import re
import random
import pickle
import json

from Innopro.config import facebook_account, facebook_password
from util import loginToFacebook, initBrowser, getPostLinks, getPostOrderData

def likeCrawler(url):

    browser = initBrowser()
    loginToFacebook(browser, facebook_account, facebook_password)

    # 商品頁面 -> 表情頁面
    browser.get(url)

    try:
        firstRecEl = browser.find_element_by_xpath(
            "//a[contains(@href,'/ufi/reaction/profile/browser/') and contains(@ajaxify,'/ufi/reaction/profile/dialog')]")
        url = firstRecEl.get_attribute('href')
        browser.get(url)
    except Exception as e:
        if NoSuchElementException:
            print('this post has no like')
        else:
            print(e)

    # 點擊所有的 likes
    # reaction_type=1 是 like 的部分
    isLikesLoaded = False
    while(isLikesLoaded == False):
        try:
            # scroll to btn position
            seeMoreBtn = browser.find_element_by_xpath(
                "//a[contains(@href,'ufi/reaction/profile/browser/fetch/?limit=50&reaction_type=1')]")
            seeMoreBtnOffsetY = seeMoreBtn.location['y'] - 300
            browser.execute_script(
                "window.scrollTo(0, {});".format(seeMoreBtnOffsetY))
            seeMoreBtn.click()
            time.sleep(2)
        except Exception as e:
            if NoSuchElementException:
                isLikesLoaded = True
                print('All likes loaded')
            else:
                print(e)
                isLikesLoaded = True

    members = []
    likeLis = browser.find_element_by_xpath(
        "//ul[@id='reaction_profile_browser1']").find_elements_by_tag_name('li')

    for li in likeLis:
        userATag = li.find_element_by_xpath(
            ".//a[contains(@href,'facebook.com') and contains(@data-gt,'eng_tid')]")
        user_data = json.loads(userATag.get_attribute('data-gt'))
        fbuid = user_data['engagement']['eng_tid']
        fbname = userATag.text
        userData = {
            'name': fbname,
            'fbuid': fbuid
        }
        members.append(userData)

    browser.close()
    return members
