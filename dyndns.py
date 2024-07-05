"""dyndns.py - scrape isp ip from router and update cloudflare
"""
import os
from time import sleep
from dataclasses import dataclass
from selenium import webdriver
from selenium.webdriver.firefox.options import Options
from selenium.webdriver.common.by import By
from selenium.common.exceptions import TimeoutException, WebDriverException
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver import ActionChains
from dotenv import dotenv_values  # pylint: disable=import-error

@dataclass(frozen=False, kw_only=True)
class LinksysRouter:
    """class LinksysRouter
    """
    time_out: int = 30
    rtr_url: str = "http://192.168.1.1"
    rtr_pwd: str = ""
    connection: webdriver = None

    def init_connection(self) -> None:
        """init_connection - initialize connection to web page
        """
        options = Options()
        # options.add_argument("--headless")
        self.connection = webdriver.Firefox(options=options)

        try:
            self.connection.get(self.rtr_url)
        except WebDriverException as e:
            print(f"GET failed with {e}")
            self.close_connection()
            os._exit(1)

    def close_connection(self) -> None:
        """close_connection - close connection to web page
        """
        self.connection.close()

    def wait_for_clickable(self, element: tuple) -> None:
        """wait_for_clickable - Wait for a web page element to be clickable

        Args:
            element (tuple): the element to wait for.  Ex: (By.ID, 'element')
        """
        try:
            element_clickable = EC.element_to_be_clickable(element)
            WebDriverWait(self.connection, self.time_out).until(element_clickable)
        except TimeoutException:
            print(f"Timed out waiting for element {element}")
            self.close_connection()
            os._exit(1)

    def locate_element_presence(self, element: tuple) -> None:
        """locate_element_presence - find element in a page

        Args:
            element (tuple): element to locate.  Ex: (By.ID, 'element')
        """
        try:
            element_present = EC.presence_of_element_located(element)
            WebDriverWait(self.connection, self.time_out).until(element_present)
        except TimeoutException:
            print(f"Timed out finding element {element}")
            self.close_connection()
            os._exit(1)

    def click_on_element(self, element: tuple) -> None:
        """click_on_element - click on the location of a page element
           The element my not be directly click-able but the location
           is

        Args:
            element (tuple): element location to click on
        """
        self.locate_element_presence(element)
        page_element = self.connection.find_element(element[0], element[1])
        ActionChains(self.connection)\
            .move_to_element(page_element)\
            .click()\
            .perform()


    def get_isp_ip(self) -> str:
        """get_isp_ip - connect to router web page and get isp ip address

        Returns:
            str: isp ip address
        """
        self.init_connection()
        # send the password
        pwd_input = (By.ID, 'adminPass')
        self.wait_for_clickable(pwd_input)
        pw_box = self.connection.find_element(pwd_input[0], pwd_input[1])
        pw_box.click()
        pw_box.clear()
        pw_box.send_keys(self.rtr_pwd)

        # click the submit button
        submit_btn = (By.ID, 'submit-login')
        self.wait_for_clickable(submit_btn)
        btn_submit = self.connection.find_element(submit_btn[0], submit_btn[1])
        btn_submit.click()

        # To work around page loading issues
        sleep(self.time_out)

        # wait for the Troubleshooting element to be located and click it
        trbl_icon = (By.ID, 'iconTroubleshooting')
        self.click_on_element(trbl_icon)

        sleep(10)
        # wait for the diagnostic tab to be located and click it
        diag_tab = (By.ID, 'diagnosticsTab')
        self.click_on_element(diag_tab)

        # locate the isp ip
        ip_elem = (By.ID, 'ip-addr')
        self.locate_element_presence(ip_elem)
        # and get the value
        ip_page_elem = self.connection.find_element(ip_elem[0], ip_elem[1])
        ip_addr = ip_page_elem.text

        self.close_connection()
        return ip_addr


def main():
    """Main function for dyndns.py - Utility to set Cloudflare Dynamic DNS
    """
    private = dotenv_values()  # take environment variables from .env.

    router = LinksysRouter(rtr_pwd=private['RTR_PWD'],
                           rtr_url=private['RTR_URL'],
                           time_out=int(private['RTR_TIMEOUT']))
    isp_ip = router.get_isp_ip()
    print(isp_ip)


if __name__ == "__main__":
    main()
