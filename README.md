# Vortex Antidetect Browser

![logo](./db/assets/mini_logo.png)  

## Join my Telegram channel:  
CHANNEL: [fastfoodsofts](https://t.me/fastfoodsofts)  

## 💻 Requirements: 
- Python 3.11 or higher  
- Any office program which works with .xlsx files (Microsoft Office, LibreOffice, OpenOffice, etc.)

## 🛠️ Installation:  
1. **Clone the repository into desired folder**  
   ```bash
   git clone https://github.com/deusexratio/vortex_antidetect_browser
   ```
   Or download it as .zip and unpack into desired folder
2. **Run install.bat on Windows or install.sh on Unix\MacOS**  

## ⚙️ Getting Started  
1. Click on the shortcut created on your desktop or double-click on run.bat (for Windows) or run.sh (for Unix\MacOS)
in the root folder of software
2. Head over to user_files folder, open "profiles.xlsx", fill out accordingly "Profiles" sheet
* You can leave Fingerprint and Profile Directory empty, it will be generated automatically  
* Proxy also can be blank or put in any format, conversion is automatic
### !!! Basically, the only required column is "Name", PLEASE make sure that all names are unique as they are used as identifier for profiles across different functions of this software.
3. In the "Wallets" sheet you can fill your seed phrases and private keys, they will be imported to database, then you can use that to import it automatically into extensions in every profile (now only Rabby and Phantom is added)  
Later you can delete them from database if you are afraid of data leak
4. If you need to export cookies from AdsBrowser, fill out accordingly names for new profiles and ads IDs in the profiles_ads.xlsx table  
   (for now I left only discord.com, x.com, google.com, outlook.com)  
5. Download desired extensions as .zip and unpack them in separate folders in user_files/extensions

6. In the main menu of Vortex click on "Import Settings" button.  
Button descriptions:
* 
        "Import profiles to database from profiles.xlsx" - Imports profiles. You should see success in the console. This for now is also used for changing proxy.
*       "Export selected cookies from AdsBrowser profiles" - Launch process that will export cookies from your 
         AdsBrowser profiles (need it to be launched and API enabled)
* 
        "Import cookies from JSONs in user_files/cookies" - Cookies stored in json files in user_files/cookies
* 
        "Import wallets to database for profiles from profiles.xlsx" - Import seed phrases and private keys from "Wallets" sheet
* 
        "Flush all seed phrases and private keys from database" - This deletes all your private data from database
* 
        "Fetch all extension ids to database" - This function is needed because your local extension ID will always differ from ID in Chrome Web Store
* 
        "Clear selected extensions cache" - This is needed when you want to delete your extension data from profiles
6.1. Press "Import profiles to database from profiles.xlsx" button  
6.2. Press "Export selected cookies from AdsBrowser profiles", wait for cookies extraction and then press "Import cookies from JSONs in user_files/cookies"  
Or just skip this step if you don't need to export your cookies  
6.3. Press "Import wallets to database for profiles from profiles.xlsx" if you filled your wallets data in "Wallets" sheet  
6.4. Press "Fetch all extension ids to database" if you have put your extensions in user_files/extensions. This needs to be done before coming to next steps.  

7. Press "Import seed phrases and private keys"
8. Select desired method and input password and simultaneous threads (not more than 3 recommended for first launch)
9. Relaunch app to view imported profiles

### Congratulations, you are all set up! You can launch any profile by double-clicking on it

