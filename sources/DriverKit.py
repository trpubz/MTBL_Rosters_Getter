# DriverKit.py
# by pubins.taylor
# created 10MAY22
# edited 18MAY23
# v1.0
# Houses the generics for Selenium WebDriver for multiple uses
import os

from selenium import webdriver
from selenium.webdriver.common.desired_capabilities import DesiredCapabilities
from selenium.webdriver.chrome.service import Service as ChromeService
from webdriver_manager.chrome import ChromeDriverManager


def DKDriverConfig(dirDownload: os.path = "root", headless=True) -> webdriver:
    """
    Handles redundant webdriver config management by passing the desired options as arguments.
    :param dirDownload: type os.path (string).  The driver will download files, like a .csv, to this directory.
    :param headless: boolean.  Indicates whether to draw the webdriver window.
    :return: selenium.webdriver
    """
    options = webdriver.ChromeOptions()
    prefs = {"download.default_directory": dirDownload}
    # example: prefs = {"download.default_directory" : "C:\Tutorial\down"};
    options.add_experimental_option("prefs", prefs)
    if headless==True:
        options.add_argument("--headless")
    # Set the load strategy so that it does not wait for adds to load
    caps = DesiredCapabilities.CHROME
    caps["pageLoadStrategy"] = "none"
    # ChromeDriverManager().install() downloads latest version of chrome driver to avoid compatibility issues
    driver = webdriver.Chrome(options=options, service=ChromeService(ChromeDriverManager().install()), desired_capabilities=caps)

    return driver


def DKDirBuilder(dirDownload: str = "root") -> os.path:
    """
    Builds a directory on the user preference.
    :param dirDownload: String representation of the desired directory to download.  If nothing passed,
    defaults to the project's root directory.
    :return: the os.path which is a string
    """

    outputPath: os.path

    if dirDownload == "root":
        projectRoot = os.path.dirname(__file__)
        outputPath = projectRoot + "/csvs"
    elif dirDownload.startswith("C:\\") or dirDownload.startswith("/Users"):
        outputPath = dirDownload
    else:
        raise NotADirectoryError()

    return outputPath



