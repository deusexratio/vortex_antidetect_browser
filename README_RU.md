# Vortex Антидетект Браузер  

![logo](./db/assets/mini_logo.png)  

## Присоединяйтесь к моему Telegram-каналу:  [fastfoodsofts](https://t.me/fastfoodsofts)  

## 💻 Требования:  
- Python 3.11 или выше  
- Любая офисная программа, работающая с .xlsx файлами (Microsoft Office, LibreOffice, OpenOffice и др.)  

## 🛠️ Установка:  
1. **Клонируйте репозиторий в нужную папку**  
   ```bash
   git clone https://github.com/deusexratio/vortex_antidetect_browser
   ```
   Или скачайте его в виде .zip-архива и распакуйте в нужную папку  
2. **Запустите install.bat на Windows или install.sh на Unix\MacOS**  

## ⚙️ Начало работы  
1. Нажмите на ярлык, созданный на рабочем столе, или дважды кликните по файлу run.bat (для Windows) или run.sh (для Unix\MacOS) в корневой папке программы. После этого создадутся необходимые папки и файлы для импорта.  
2. Перейдите в папку user_files, откройте "profiles.xlsx" и заполните лист "Profiles"  
   * Поля "Fingerprint" и "Profile Directory" можно оставить пустыми — они будут сгенерированы автоматически  
   * Поле "Proxy" также можно оставить пустым или заполнить в любом формате — конвертация произойдет автоматически  
   
###   **!!! Единственная обязательная колонка — "Name". Убедитесь, что все имена уникальны, так как они используются в качестве идентификаторов профилей в различных функциях программы.**  
3. В листе "Wallets" можно указать seed-фразы и приватные ключи — они будут импортированы в базу данных. После этого можно автоматически импортировать их в расширения для каждого профиля (на данный момент поддерживаются Rabby и Phantom). Позже их можно удалить из базы данных, если опасаетесь утечки данных.  
4. Если требуется экспортировать cookies из AdsBrowser, заполните таблицу profiles_ads.xlsx, указав названия новых профилей и ID объявлений  
   (на данный момент поддерживаются только discord.com, x.com, google.com, outlook.com).  
5. Скачайте нужные расширения в формате .zip и распакуйте их в отдельные папки в user_files/extensions.  

6. В главном меню Vortex нажмите кнопку "Import Settings".  
   
   **Описание кнопок:**  
   * **"Import profiles to database from profiles.xlsx"** – Импортирует профили. В консоли должно появиться сообщение об успешном завершении. Также используется для изменения прокси.  
   * **"Export selected cookies from AdsBrowser profiles"** – Запускает процесс экспорта cookies из профилей AdsBrowser (требуется запущенный AdsBrowser и активный API).  
   * **"Import cookies from JSONs in user_files/cookies"** – Импортирует cookies из JSON-файлов в user_files/cookies.  
   * **"Import wallets to database for profiles from profiles.xlsx"** – Импортирует seed-фразы и приватные ключи из листа "Wallets".  
   * **"Flush all seed phrases and private keys from database"** – Удаляет все приватные данные из базы данных.  
   * **"Fetch all extension ids to database"** – Добавляет в базу данных ID установленных локально расширений (отличаются от ID в Chrome Web Store).  
   * **"Clear selected extensions cache"** – Очищает кэш данных расширений в профилях.  

6.1. Нажмите "Import profiles to database from profiles.xlsx".  
6.2. Нажмите "Export selected cookies from AdsBrowser profiles", дождитесь завершения экспорта и затем нажмите "Import cookies from JSONs in user_files/cookies".  
(Или пропустите этот шаг, если экспорт cookies не требуется.)  
6.3. Нажмите "Import wallets to database for profiles from profiles.xlsx", если заполняли данные о кошельках в листе "Wallets".  
6.4. Нажмите "Fetch all extension ids to database", если добавляли расширения в user_files/extensions. Это необходимо перед следующим шагом.  

7. Нажмите "Import seed phrases and private keys".  
8. Выберите нужный метод, введите пароль и укажите количество одновременных потоков (не более 3 рекомендуется для первого запуска).  
9. Перезапустите приложение, чтобы увидеть импортированные профили.  

### 🎉 Поздравляем, настройка завершена! Теперь можно запускать любой профиль двойным кликом.  