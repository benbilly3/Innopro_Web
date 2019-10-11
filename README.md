
# Innopro_Web-Crawler 

成品網址：https://innopro.herokuapp.com/session/

Selenium :臉書團購網站留言、貼文、社團成員爬蟲

Django:後端網路架構

## 專案初始設定：

1. 欲初始化專案先建立虛擬環境 `virtualenv venv` （Python 版本3.6 以上），之進入虛擬環境 `source venv/bin/activate` ， 安裝相關套件 `pip install requirements.txt`
2. Django 專案目錄為 `Innopro` 資料夾，`cd Innopro`

3. Run server: `python manage.py runserver` 即可跑起伺服器（預設為 Innopro.settings.development 設定檔），如果要使用 production 設定檔的話，執行 `python manage.py runserver --settings=Innopro.settings.production` 執行其他指令時亦同，如 `python manage.py migrate --settings=Innopro.settings.production` 會將資料庫變動寫入 production 的環境當中，多 Settings 檔的設定請參考[此篇文章](https://simpleisbetterthancomplex.com/tips/2017/07/03/django-tip-20-working-with-multiple-settings-modules.html)



