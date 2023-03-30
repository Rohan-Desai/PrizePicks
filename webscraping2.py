from selenium import webdriver
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.support import expected_conditions as EC
import copy
PATH = "/Users/rohandesai/Desktop/PrizePicks Bot/chromedriver.exe"
s = Service(PATH)
propProf = webdriver.Chrome(service = s)
prizePicks = webdriver.Chrome(service = s)
#PrizePicks Credentials
USERNAME_PRIZEPICKS =
PASSWORD_PRIZEPICKS = 

#login to bookmaker
propProf.get("https://prop-professor.herokuapp.com")
propProf.implicitly_wait(40)

table = propProf.find_element(By.TAG_NAME, "tbody")
propProf.implicitly_wait(15)


#parse a certian amount of rows in table and store values in propContainer
#data stored in Props struct
rowsToParse = 50
TARGET_VAL = 54.3
class Prop:
    pass
#Prints players containd in prop Container
def printProps(propContainer):
    for prop in propContainer:
        print(prop.player, "|", prop.league, "|", prop.stat, "|", prop.type, "|", prop.probability)

propContainer = []
playerContainer = []
for rows in table.find_elements(By.TAG_NAME, "tr"):
    currRow = rows.find_elements(By.TAG_NAME, "td")
    currProp = Prop()
    currProp.player = currRow[0].text.strip()
    currProp.league = currRow[1].text.strip()
    currProp.stat = currRow[2].text.strip()
    currProp.type = currRow[3].text.strip()
    currProp.probability = currRow[12].text.strip()
    if(float(currProp.probability) < TARGET_VAL):
        break
    if((currProp.player not in playerContainer)):
        propContainer.append(currProp)
        playerContainer.append(currProp.player)
printProps(propContainer)
if len(propContainer) < 5:
    print("No Valid Parlay")
    exit(1)

convertCodeToVal = {
    "PTS": "Points",
    "REB": "Rebounds",
    "AST": "Assists",
    "PRA": "Pts+Rebs+Asts",
    "FS" : "Fantasy Score",
    "3PM": "3-PT Made",
    "PR": "Pts+Rebs",
    "PA": "Pts+Asts",
    "RA": "Rebs+Asts",
    "FTM": "Free Throws Made",
    "STOCKS": "Blcks+Stls",
    "STL" : 'Steals',
    "TO" : 'Turnovers',
    "SOG" : "Shots On Goal",
    "GOAL" : "Goals",
    "SAVE" : "Goalie Saves",
    "GA8" : "Goals Allowed in First 8 Minutes", 
    "GA" : "Goals Allowed",
    "GA7" : "Goals Allowed in First 7 Minutes",
    "BLK" : "Blocked Shots", 
    "GA9" : "Goals Allowed in First 9 Minutes",
}

def selectLeague(targetLeague):        
    leagues = prizePicks.find_element(By.CLASS_NAME, "league-navigation")
    prizePicks.implicitly_wait(20)
    allLeagues =  leagues.find_elements(By.CLASS_NAME, "league")
    prizePicks.implicitly_wait(20)
    print(targetLeague)
    for league in allLeagues:
        name = league.find_element(By.CLASS_NAME, "name")
        #print(name.text, "|", end = '')
        if(name.text == targetLeague):
            element = WebDriverWait(prizePicks, 20).until(EC.presence_of_element_located((By.XPATH, "//div[@class = 'league'][position()=4]")))
            prizePicks.implicitly_wait(20)
            print("found league:" , name.text)
            prizePicks.execute_script("arguments[0].click();",league)
            prizePicks.implicitly_wait(20)
            #league.click()
            print("successful League Select")
            return True
    return False
        
def selectStat(targetStat): 
    statuh = prizePicks.find_element(By.CLASS_NAME, "stat-navigation")
    stats = statuh.find_element(By.CLASS_NAME, "stat-container")
    allStats = stats.find_elements(By.CSS_SELECTOR, ".stat")
    print(convertCodeToVal[targetStat])
    for stat in allStats:
        #print(stat.text, "|", end = '')
        if(stat.text == convertCodeToVal[targetStat]):
            print("found stat:" , stat.text)
            prizePicks.execute_script("arguments[0].click();",stat)
            print("successful stat Select")
            return True
    return False

def selectPlayer(targetPlayer):
    Players = prizePicks.find_element(By.ID, "projections")
    prizePicks.implicitly_wait(20)
    allPlayers = Players.find_elements(By.CLASS_NAME, "projection")
    prizePicks.implicitly_wait(20)
    for player in allPlayers:
        if(player.find_element(By.CLASS_NAME, "name").text == targetPlayer):
            clickablePlayer = player.find_element(By.CLASS_NAME, "name")
            prizePicks.execute_script("arguments[0].click();",clickablePlayer)
            print("successful projection select")
            print()
            return True
    return False

def selectPicks(targetPlayer, targetLeague, targetStat):
    if selectLeague(targetLeague):
        prizePicks.implicitly_wait(20)
        if selectStat(targetStat):
            prizePicks.implicitly_wait(20)
            if selectPlayer(targetPlayer):
                prizePicks.implicitly_wait(20)
                return True
    return False

#login to prizepicks
prizePicks.get("https://app.prizepicks.com/")
WebDriverWait(prizePicks, 10).until(EC.element_to_be_clickable((By.CLASS_NAME, "close")))
#exit popup
prizePicks.find_element(By.CLASS_NAME, "close").click()
#click login button
prizePicks.find_element(By.XPATH, "//button[@class='sc-crXcEl iRmYPz login']").click()
prizePicks.implicitly_wait(15)
#find input fields and input credentials
prizePicks.find_element(By.XPATH, "//input[@id='email-input']").send_keys(USERNAME_PRIZEPICKS)
password = prizePicks.find_element(By.CLASS_NAME, "password-input")
password.find_element(By.TAG_NAME, "input").send_keys(PASSWORD_PRIZEPICKS)
prizePicks.find_element(By.ID, "submit-btn").click()
prizePicks.implicitly_wait(15)

successfulLays = 0
finalParlay = []
for parlays in propContainer:
    if successfulLays == 5:
        break
    try:
        if not selectPicks(parlays.player, parlays.league, parlays.stat):
            print(parlays.player, " does not exist")
        else:
            finalParlay.append(parlays)
            successfulLays += 1
    except:
        print(parlays.player, " does not exist ERRROR")
print("Final Parlay is:")
printProps(finalParlay)

theLen = len(prizePicks.find_elements(By.CLASS_NAME, "over"))
selectIndex = 0
for i in range(0, theLen, 2):
    if (finalParlay[selectIndex].type == "Over"):
        over = prizePicks.find_elements(By.CLASS_NAME, "over")[i+1]
        prizePicks.execute_script("arguments[0].click();",over)
    if (finalParlay[selectIndex].type == "Under"):
        under = prizePicks.find_elements(By.CLASS_NAME, "under")[i+1]
        prizePicks.execute_script("arguments[0].click();",under)
    selectIndex += 1
betUnit = 5
unitField = WebDriverWait(prizePicks, 10).until(EC.element_to_be_clickable((By.XPATH, "//input[@type='number']")))
unitField.clear()
unitField.send_keys('5')

containerPE = prizePicks.find_element(By.CLASS_NAME,"place-entry-button-container")
placeEntry = containerPE.find_element(By.TAG_NAME, "button")
print(placeEntry.text)
while(True):
    pass
