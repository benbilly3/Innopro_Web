# 創朝FB電商網站架構

## 程式開發工具
1. 後端語言為Python，網路開發框架為Django：https://www.djangoproject.com/ 。
2. 前端語言為Java Script、Bootstrap框架。
3. IDE選擇為VScode or Pycharm、Jupyter(方便斷句測試、筆記)。
4. VM環境為AWS。

## 專案初始設定
1. 欲初始化專案先建立虛擬環境 virtualenv venv （Python 版本3.6 以上），進入虛擬環境指令為 source venv/bin/activate ，亦可使用VScode、Pycharm等IDE開發較方便。
安裝相關套件指令為 pip install requirements.txt。若使用Django2.2版本 ，需要手動解決 Django 2.2 的 MySql 問題： 升級Django： https://docs.djangoproject.com/zh-hans/2.2/howto/upgrade-version/ 
問題解法： https://blog.csdn.net/weixin_33127753/article/details/89100552
3. Django 專案目錄為 Innopro 資料夾，指令為cd Innopro。
4. 放入config環境測定檔。把 Facebook 帳號密碼依序填入 config.json 檔中，可複製一份 config_example.json ，再將檔名改成 config.json 即可，環境中有 DEV 的部分為開發環境的變數。
5. 為做開發版本控制，執行環境分為Production(正式)、Development(開發這版本)，資料庫亦分為Innopro、Innopro-dev兩個版本。
6. Run server指令: python manage.py runserver 即可跑起伺服器（預設為 Innopro.settings.development 設定檔），如果要使用 production 設定檔的話，執行 python manage.py runserver --settings=Innopro.settings.production 執行其他指令時亦同，如 python manage.py migrate --settings=Innopro.settings.production 會將資料庫變動寫入 production 的環境當中，多 Settings 檔的設定請參考此篇文章[https://simpleisbetterthancomplex.com/tips/2017/07/03/django-tip-20-working-with-multiple-settings-modules.html](https://)

## Django開發常用指令集
1. **安裝專案套件，套件名稱與版本記於requirement.txt**：pip install -r requirements.txt
2. **執行dev版本server，內網預設為8000，可自由切換，範例為切至7000**：python manage.py runserver 7000 
3. **執行production版本server，內網預設為8000，可自由切換，範例維切至7000**：python manage.py runserver 7000 --settings=Innopro.settings.production
4. **創造app**：python manage.py startapp fbCrawler
5. **若要新增或修正model(資料庫)，須下指令產生遷徙檔**：python manage.py makemigrations fbCrawler
再將遷徙檔執行，dev資料庫會產生對應table或修正：python manage.py migrate，若要讓product資料庫遷徙，指令則為python manage.py migrate --settings=Innopro.settings.production
3. **啟動Jupyter notebook測試開發**：python manage.py shell_plus --notebook 、python manage.py shell_plus --notebook --settings=Innopro.settings.production

## 專案程式架構圖
MVC(MVT)架構
### 大架構

![](https://i.imgur.com/p7vTCG0.png)


### 主APP架構
![](https://i.imgur.com/MZ466H0.png)

### 資料庫架構
SQL關聯式資料庫
資料庫佈建於AWS-RDS服務

#### Schema
![](https://i.imgur.com/fKvbroG.jpg)

#### Table
![](https://i.imgur.com/VZFpZFz.jpg)

table對應的欄位對應於fbcrawler.model.py的verbose_name，有中文名稱對應，較好理解欄位功能。每個model皆有“Todo”標示商業邏輯用途。

![](https://i.imgur.com/oen3qy6.png)


#### Django Admin
Django有內建後台管理系統，於fbcrawler.admin.py檔控制，有資料庫GUI可於後台管理(新增、查詢、刪除)資料庫、使用者權限等等。
![](https://i.imgur.com/Zw5txEy.png)
![](https://i.imgur.com/NtR3LeM.png)


## AWS管理

### EC2基本控制
https://aws.amazon.com/tw
進入aws首頁，右上角登入主控台，之後輸入帳密。
![](https://i.imgur.com/zPNJvLP.jpg)

主控台畫面如下，選擇EC2(AWS的VM服務)：
![](https://i.imgur.com/EEEbTyZ.png)

點擊Running Instance進入VM控制畫面

![](https://i.imgur.com/1OiC97u.png)

可見VM資訊做相關設定，更多說明見AWS官網教學

![](https://i.imgur.com/OAxRoHN.png)

VM效能可自由調整，費用有差，請注意。先將Instance Status調整成stop，再依照下圖步驟調整、選擇，調整完再重啟VM。

![](https://i.imgur.com/j0hdaMB.png)
![](https://i.imgur.com/6Vq18yk.png)

### 如何更新VM網頁？

取得VM金鑰檔，之後會移交。
Linux下指令進入VM。
```
cd /Users/benbilly3/Downloads/aws
ssh -i innopro-aws-ec2.pem ubuntu@3.1.118.53
chmod 400 innopro-aws-ec2.pem

```
cd到innpro資料夾，使用git pull做更新

![](https://i.imgur.com/xSOWrvZ.png)

### 如何取得VM中的資料？
可使用Filezilla透過金鑰SFTP連線ubuntu，看log或是調整apache。
![](https://i.imgur.com/4giXg6W.jpg)
![](https://i.imgur.com/fIKzc8b.jpg)














