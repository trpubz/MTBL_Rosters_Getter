import json

from DriverKit import DKDriverConfig
from TRPFrontOffice import Team

from bs4 import BeautifulSoup
from selenium.webdriver.common.by import By

rosters: list = list()
teams: list = list()


def TRPGetRosters(url: str):
    driver = DKDriverConfig()
    driver.get(url)
    driver.implicitly_wait(3)
    rosterElements = driver.find_elements(By.CLASS_NAME, "jsx-1671979099.rosterTable")
    for ros in rosterElements:
        rosters.append(ros.get_attribute("outerHTML"))
    driver.close()


def TRPFillRosters():
    for ros in rosters:
        soup = BeautifulSoup(ros, "lxml")
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


def TRPJSONSave(directory: str):
    jsonTeams: json = []
    for tm in teams:
        jsonTeams.append(tm.__dict__)

    with open(directory + "rosters.json", "w+") as f:
        json.dump(jsonTeams, f, indent=2)
        f.close()


if __name__ == '__main__':
    TRPGetRosters('https://fantasy.espn.com/baseball/league/rosters?leagueId=10998')
    TRPFillRosters()
    TRPJSONSave(directory="/Users/Shared/BaseballHQ/regseason")
