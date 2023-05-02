"""Login module."""
import json
from typing import Dict, List

from selenium.webdriver.common.by import By
from selenium.webdriver.remote.webdriver import WebDriver
from selenium.webdriver.support import expected_conditions as ec
from selenium.webdriver.support.ui import WebDriverWait


def domain_to_url(domain: str) -> str:
    """Convert a partial domain to valid URL.

    Args:
        domain: Domain to be converted.

    Returns:
        A fully qualified URL.
    """
    if domain == ".chrome.google.com/robots.txt":
        domain = "chrome.google.com/robots.txt"
    else:
        if domain.startswith("."):
            domain = f"www{domain}"
    return f"http://{domain}"


def login_using_cookie_file(driver: WebDriver, cookie_file: str) -> None:
    """Restore auth cookies from a file.

    Does not guarantee that the user is logged in afterwards.

    Visits the domains specified in the cookies to set them, the previous page
    is not restored.

    Args:
        driver: Selenium webdriver.
        cookie_file: Existing, valid authentication cookie.
    """
    domain_cookies: Dict[str, List[object]] = {}
    with open(cookie_file) as file:
        cookies: List = json.load(file)
        # Sort cookies by domain, because we need to visit to domain to add cookies
        for cookie in cookies:
            try:
                domain_cookies[cookie["domain"]].append(cookie)
            except KeyError:
                domain_cookies[cookie["domain"]] = [cookie]

    for domain, cookies in domain_cookies.items():
        driver.get(domain_to_url(domain + "/robots.txt"))
        for cookie in cookies:
            cookie.pop("sameSite", None)  # Attribute should be available in Selenium >4
            cookie.pop("storeId", None)  # Firefox container attribute
            try:
                driver.add_cookie(cookie)
            except Exception:
                print(f"Couldn't set cookie {cookie['name']} for {domain}")


def confirm_logged_in(driver: WebDriver) -> bool:
    """Confirm that the user is logged in.

    The browser needs to be navigated to a YouTube page.

    Args:
        driver: Selenium webdrive.

    Returns:
        `True` if the user is logged in, otherwise `False`.
    """
    try:
        WebDriverWait(driver, 5).until(
            ec.element_to_be_clickable((By.ID, "avatar-btn"))
        )
        return True
    except TimeoutError:
        return False
