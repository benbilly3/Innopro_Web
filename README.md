<<<<<<< HEAD
# Innopro

## 專案初始設定：

1. 欲初始化專案先建立虛擬環境 `virtualenv venv` （Python 版本3.6 以上），之進入虛擬環境 `source venv/bin/activate` ， 安裝相關套件 `pip install requirements.txt`
2. Django 專案目錄為 `Innopro` 資料夾，`cd Innopro`
3. 確認環境變數是否存在與正確，把 Facebook 帳號密碼依序填入 `config.json` 檔中，可複製一份 `config_example.json` ，再將檔名改成 `config.json` 即可，環境中有 DEV 的部分為開發環境的變數。
4. Run server: `python manage.py runserver` 即可跑起伺服器（預設為 Innopro.settings.development 設定檔），如果要使用 production 設定檔的話，執行 `python manage.py runserver --settings=Innopro.settings.production` 執行其他指令時亦同，如 `python manage.py migrate --settings=Innopro.settings.production` 會將資料庫變動寫入 production 的環境當中，多 Settings 檔的設定請參考[此篇文章](https://simpleisbetterthancomplex.com/tips/2017/07/03/django-tip-20-working-with-multiple-settings-modules.html)

## 團購流程與程式執行邏輯

## 資料庫與欄位設定
=======
# Innopro_Web-Crawler Selenium 臉書留言、貼文、社團成員爬蟲

應用於臉書團購網站開發
>>>>>>> c0d3eb78c7009d5d66775f18c056eb557a20eb00
