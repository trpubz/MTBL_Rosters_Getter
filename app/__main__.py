import json
import os

from mtbl_driverkit.mtbl_driverkit import dk_driver_config, TempDirType
from app.sources.TRPFrontOffice import Team
from bs4 import BeautifulSoup
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

# set global variables
lg_rosters_base_url = "https://fantasy.espn.com/baseball/league/rosters?leagueId="
lg_id = "10998"
extract_path = "/Users/Shared/BaseballHQ/resources/extract"
rosters: list = list()
teams: list = list()


# function to open web driver and get rosters
def fetch_rosters(url: str):
    driver = dk_driver_config(invoking_module_path=(TempDirType.APP, __file__), headless=True)[0]
    driver.get(url)
    # print("successfully navigated to " + url)
    driver.implicitly_wait(3)
    roster_element_class_name: str = "rosterTable"  # sometimes modified by host website
    # wait for the roster elements to load
    try:
        WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.CLASS_NAME, roster_element_class_name)))
        roster_elements = driver.find_elements(By.CLASS_NAME, roster_element_class_name)
    except Exception as e:
        exit(f"Could not locate Roster Tables.  Error: {e}")

    for ros in roster_elements:
        rosters.append(ros.get_attribute("outerHTML"))
    # print("successfully pulled rosters in memory")
    # Save the list to a temp file
    with open("temp_raw_rosters.json", 'w') as f:
        json.dump(rosters, f)

    driver.quit()


def parse_rosters(path: str, lg_mngrs_file_name: str = "lg_managers.json"):
    # load a local .json file for the league managers
    manager_keys: list
    with open(os.path.join(path, lg_mngrs_file_name), "r") as f:
        manager_keys = json.load(f)["data"]  # store only the data and not the schema
        f.close()
        # print("successfully loaded " + lgMngrsFileName + " for lgrstrs instantiation")

    # if the rosters list is empty, load it from the temp file
    global rosters  # declaring global here quiets the UnboundLocalError
    if len(rosters) == 0:
        with open("temp_raw_rosters.json", 'r') as f:
            rosters = json.load(f)
            f.close()
            # print("successfully loaded rosters from temp file")

    for ros in rosters:
        soup = BeautifulSoup(ros, "lxml")  # lxml is faster than html.parser
        team_name: str = soup.find("span", class_="teamName truncate").text.replace("  ", " ")
        # find the teamAbbreviation from the manager_keys matching the teamName
        abbrv: str = next(
            (team["teamAbbreviation"] for team in manager_keys if team["teamName"] == team_name),
            None)
        tm: Team = Team(abbrv=abbrv)  # create a new Team object

        players = soup.find("tbody").find_all("tr")
        for plyr in players:
            # if a position is empty, skip the row
            if plyr.find_all("td")[1].text == "Empty":
                continue

            pos: str = plyr.find_all("td")[0].text  # position is the first data in the row
            img_tag = plyr.find("div", class_="player-headshot").find("img")
            pid_link: str = ""
            # the playerid link (pid_link) can sometimes be stored in the 'src' tag or in a
            # 'data-src' tag
            if img_tag.get("data-src") is not None:
                pid_link = img_tag.get("data-src")
            elif img_tag.get("src") is not None:
                pid_link = img_tag.get("src")
            pid: str = ""
            try:
                pid = pid_link.partition(".png")[0].rpartition("/")[2]
            except AttributeError as ae:
                print(ae, f"{pid_link}")
            # TODO: handle players with no mugshot
            # if pid == "nomug":
            #     continue
            tm.addPlayer(pos=pos, pid=pid)
        teams.append(tm)


def save_json(path: str, fileName: str = "lg_rosters.json") -> bool:
    json_teams: json = []
    for tm in teams:
        json_teams.append(tm.__dict__)

    with open(os.path.join(path, fileName), "w+") as f:
        json.dump(json_teams, f, indent=2)
        f.close()
        # print(f"successfully saved {fileName} to {dirPath}")
        return True


def main():
    print("\n---starting Rosters Getter---\n")
    # retrieve rosters and store them in global rosters list
    fetch_rosters(lg_rosters_base_url + lg_id)
    parse_rosters(path=extract_path)

    goodSave = save_json(path=extract_path)
    if goodSave:
        # delete the temp file
        os.remove("temp_raw_rosters.json")

    print("\n---Rosters Getter complete---")


if __name__ == '__main__':
    main()
