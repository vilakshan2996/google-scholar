from bs4 import BeautifulSoup
import requests, lxml, json
import urllib.parse
from google.colab import auth
import gspread
from google.auth import default
import time

#Steps to find organization id, spread sheet id and sheet name are in the readme file


#to work with google sheets
auth.authenticate_user()
creds, _ = default()
gc = gspread.authorize(creds)



spreadsheet_id = "xxxxxxxxxxxxxxxxxxxxxxxxxxxxx"
sheet_name = "xxxxxxxxxxxxxxxxxxxxxxxxxxx"



sheet = gc.open_by_key(spreadsheet_id).worksheet(sheet_name)



#to store all the users
all_users = [ ]



def scrape_users():
    params = {
    "view_op": "view_org",
    "hl":"en",
    "org": "12610868586512439209"              #Here is organization id
        }

    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/106.0.0.0 Safari/537.36"
    }


    user_is_present = True
    count =0
    while user_is_present:
        html = requests.post("https://scholar.google.com/citations", params=params, headers=headers, timeout=30)
        soup = BeautifulSoup(html.text, "lxml")
        for user in soup.select(".gsc_1usr"):
            user_name = user.select_one(".gs_ai_name").text
            user_link = f'https://scholar.google.com{user.select_one(".gs_ai_pho")["href"]}'
            
            
            #if citation count is not present then it will be 0 
            try:
                user_citationCounts = user.select_one(".gs_ai_cby").text.split()[2]        
            except:
                user_citationCounts=0

            all_users.append({
                "name": user_name,
                "citationCount": user_citationCounts,
                "link": user_link   
            })
        
        #if there is a next page exists but onclick() is not present then it will be false and it will stop the loop
        try: 
            if soup.select_one(".gs_btnPR"):   
                params["after_author"] = str(soup.select_one(".gs_btnPR")["onclick"]).split("x26")[3].split("x3d")[1][:-1]
                print(params["after_author"])   #debug message to check is the loop working fine 
                params["astart"] = str(count+10)
        except:
            user_is_present = False
        

    print(json.dumps(all_users, indent=2, ensure_ascii=False))





scrape_users()


#code to work with google sheet
sheet.clear()
sheet.insert_row(list(all_users[0].keys()))        #inserting the keys of the dictionary as the headers of the sheet

for row_data in reversed(all_users):   
    while True:
        try:
            values = [row_data[key] for key in row_data.keys()]         #inserting the values of the dictionary as the rows of the sheet
            sheet.insert_row(values, index=2)
            break
        except gspread.exceptions.APIError as err:
            if err.response.status_code == 429:
            # Wait for a few seconds and retry the request
                time.sleep(5)
            else:
                raise err
            continue
            