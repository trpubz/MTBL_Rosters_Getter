import json
import os

from sources.DriverKit import DKDriverConfig
from sources.TRPFrontOffice import Team

from bs4 import BeautifulSoup
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

# set global variables
lgRostersBaseURL = "https://fantasy.espn.com/baseball/league/rosters?leagueId="
dirPath = "/Users/Shared/BaseballHQ/resources/extract"
lgID = "10998"
rosters: list = list()
teams: list = list()


# function to open web driver and get rosters
def TRPGetRosters(url: str):
    driver = DKDriverConfig()
    driver.get(url)
    print("successfully navigated to " + url)
    driver.implicitly_wait(3)
    rosterElementClassName: str = "rosterTable"  # sometimes modified by host website
    # wait for the roster elements to load
    try:
        WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.CLASS_NAME, rosterElementClassName)))
        rosterElements = driver.find_elements(By.CLASS_NAME, rosterElementClassName)
    except Exception as e:
        exit(f"Could not locate Roster Tables.  Error: {e}")

    for ros in rosterElements:
        rosters.append(ros.get_attribute("outerHTML"))
    print("successfully pulled rosters in memory")
    # Save the list to a temp file
    with open("tempRawRosters.json", 'w') as f:
        json.dump(rosters, f)

    driver.quit()


def TRPFillRosters(path: str, lgMngrsFileName: str = "lgmngrs.json"):
    # load a local .json file for the league managers
    managerKeys: list
    with open(os.path.join(path, lgMngrsFileName), "r") as f:
        managerKeys = json.load(f)["data"]  # store only the data and not the schema
        f.close()
        print("successfully loaded " + lgMngrsFileName + " for lgrstrs instantiation")

    # if the rosters list is empty, load it from the temp file
    global rosters  # declaring global here quiets the UnboundLocalError
    if len(rosters) == 0:
        with open("tempRawRosters.json", 'r') as f:
            rosters = json.load(f)
            f.close()
            print("successfully loaded rosters from temp file")

    for ros in rosters:
        soup = BeautifulSoup(ros, "lxml")  # lxml is faster than html.parser
        teamName: str = soup.find("span", class_="teamName truncate").text
        # find the teamAbbreviation from the managerKeys matching the teamName
        abbrv: str = next((team["teamAbbreviation"] for team in managerKeys if team["teamName"] == teamName), None)
        tm: Team = Team(abbrv=abbrv) # create a new Team object

        players = soup.find("tbody").find_all("tr")
        for plyr in players:
            # if a position is empty, skip the row
            if plyr.find_all("td")[1].text == "Empty":
                continue

            pos: str = plyr.find_all("td")[0].text # position is the first data in the row
            pidLink: str = plyr.find("div", class_="player-headshot").find("img").get("src")
            pid: str = pidLink.partition(".png")[0].rpartition("/")[2]
            # TODO: handle players with no mugshot
            # if pid == "nomug":
            #     continue
            tm.addPlayer(pos=pos, pid=pid)
        teams.append(tm)


def TRPJSONSave(path: str, fileName: str = "lgrstrs.json") -> bool:
    jsonTeams: json = []
    for tm in teams:
        jsonTeams.append(tm.__dict__)

    with open(os.path.join(path, fileName), "w+") as f:
        json.dump(jsonTeams, f, indent=2)
        f.close()
        print(f"successfully saved {fileName} to {dirPath}")
        return True


def main():
    print("\n---starting rosters getter---\n")
    # retrieve rosters and store them in global rosters list
    TRPGetRosters(lgRostersBaseURL + lgID)
    TRPFillRosters(path=dirPath)

    goodSave = TRPJSONSave(path=dirPath)
    if goodSave:
        # delete the temp file
        os.remove("tempRawRosters.json")

    print("\n---rosters getter complete---")


if __name__ == '__main__':
    main()
