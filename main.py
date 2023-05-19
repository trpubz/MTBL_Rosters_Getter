import json
import os

from sources.DriverKit import DKDriverConfig
from sources.TRPFrontOffice import Team

from bs4 import BeautifulSoup
from selenium.webdriver.common.by import By

# set global variables
lgRostersBaseURL = "https://fantasy.espn.com/baseball/league/rosters?leagueId="

rosters: list = list()
teams: list = list()


# function to open web driver and get rosters
def TRPGetRosters(url: str):
    driver = DKDriverConfig()
    driver.get(url)
    print("successfully navigated to " + url)
    driver.implicitly_wait(3)
    rosterElementClassName = "rosterTable" # sometimes modified by host website
    rosterElements = driver.find_elements(By.CLASS_NAME, rosterElementClassName)
    for ros in rosterElements:
        rosters.append(ros.get_attribute("outerHTML"))
    print("successfully pulled rosters in global variable")
    # Save the list to a temp file
    with open("tempRawRosters.json", 'w') as f:
        json.dump(rosters, f)

    driver.close()


def TRPFillRosters(path: str, lgMngrsFileName: str = "lgmngrs.json"):
    # load a local .json file
    managerKeys: dict
    with open(os.path.join(path, lgMngrsFileName), "r") as f:
        managerKeys = json.load(f)["data"]  # store only the data and not the schema
        f.close()
        print("successfully loaded " + lgMngrsFileName)

    # if the rosters list is empty, load it from the temp file
    global rosters # declaring global here quiets the UnboundLocalError
    if len(rosters) == 0:
        with open("tempRawRosters", 'r') as f:
            rosters = json.load(f)
            f.close()
            print("successfully loaded rosters from temp file")

    for ros in rosters:
        soup = BeautifulSoup(ros, "lxml")  # lxml is faster than html.parser
        teamName = soup.find("span", class_="teamName truncate").text
        tm = Team(name=teamName)
        players = soup.find("tbody").find_all("tr")
        for plyr in players:
            pos = plyr.find_all("td")[0].text
            pidLink: str = plyr.find("div", class_="player-headshot").find("img").get("data-src")
            if pidLink is None:
                pidLink: str = plyr.find("div", class_="player-headshot").find("img").get("src")
            pid: str = pidLink.partition(".png")[0].rpartition("/")[2]
            if pid == "nomug" and plyr.find_all("td")[1].text == "Empty":
                continue
            tm.addPlayer(pos=pos, pid=pid)
        teams.append(tm)


def TRPJSONSave(path: str):
    jsonTeams: json = []
    for tm in teams:
        jsonTeams.append(tm.__dict__)

    with open(path + "lgrstrs.json", "w+") as f:
        json.dump(jsonTeams, f, indent=2)
        f.close()


if __name__ == '__main__':
    dirPath = "/Users/Shared/BaseballHQ/resources/extract"
    lgID = "10998"

    # retrieve rosters and store them in global rosters list
    TRPGetRosters(lgRostersBaseURL + lgID)
    TRPFillRosters(path=dirPath)

    TRPJSONSave(path=dirPath)
    print(f"successfully saved lgrstrs.json to {dirPath}")
