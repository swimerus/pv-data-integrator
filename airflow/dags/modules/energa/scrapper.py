import atexit
import time
from datetime import datetime
import os
import json

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.firefox.options import Options
from selenium.webdriver.support.ui import Select
from selenium.common.exceptions import NoSuchElementException


from modules.utils import util


class Scrapper:
    def __init__(self):
        self.energa_username = util.get_config_param('energa_username')
        self.energa_password = util.get_config_param('energa_password')
        self.url_login = util.get_config_param('energa_login_url')
        self.download_directory = f'{util.get_config_param("file_dir")}/energa/org_files'
        self.summary_directory = f'{util.get_config_param("file_dir")}/energa'
        self.first_date_with_data = util.get_config_param('first_date_with_data')

        self._ENERGY_PRODUCED = 'energy_produced'
        self._ENRGY_USED = 'energy_used'

        self._prepare_browser()
        self._login()

        atexit.register(self._close)

    def _prepare_browser(self):
        options = Options()
        
        options.add_argument('--no-sandbox')
        options.add_argument('--window-size=1920,1080')
        options.add_argument('--headless')
        options.add_argument('--disable-gpu')
        options.page_load_strategy = 'eager'
        options.set_preference('browser.download.folderList', 2)
        options.set_preference(
            'browser.download.manager.showWhenStarting', False)
        options.set_preference('browser.download.dir', self.download_directory)
        options.set_preference('browser.helperApps.neverAsk.saveToDisk', 'application/x-gzip')

        self.driver = webdriver.Remote(
            "http://host.docker.internal:4444/wd/hub", options=options)

    def _login(self):
        self.driver.get(self.url_login)

        time.sleep(3)
        
        self.driver.find_element(By.ID, "loginRadio").click()
        self.driver.find_element(
            By.ID, "j_username").send_keys(self.energa_username)
        self.driver.find_element(
            By.ID, "j_password").send_keys(self.energa_password)
        self.driver.find_element(By.NAME, "loginNow").click()

    def _close(self):
        self.driver.quit()

    def _delete_file_if_exists(self, path):
        if os.path.exists(path):
            os.remove(path)

    def _rename_file(self, org_filename, current_date):

        old_name = f'{self.download_directory}/{org_filename}.xls'

        dt = current_date.replace('-', '')
        name = org_filename.replace(' ', '_')

        now = datetime.now().strftime("%Y%m%d%H%M%S")
        new_name = f'{self.download_directory}/{dt}_{name}_{now}.xls'

        self._delete_file_if_exists(new_name)
        os.rename(old_name, new_name)

    def _navigate_to_day_before(self):
        self.driver.find_element(By.ID, 'buttonPrev').click()
        time.sleep(0.3)

        return self.driver.find_element(By.ID, 'dayDate').get_attribute('value')

    def _navigate_to_date(self, date):
        current_date = self.driver.find_element(
            By.ID, 'dayDate').get_attribute('value')

        while current_date != date:
            current_date = self._navigate_to_day_before()
            print(self.driver.find_element(
                By.ID, 'dayDate').get_attribute('value'))


    def _is_data_present(self):
        try: 
            self.driver.find_element(By.CLASS_NAME, 'chart-info')
            return False
        except NoSuchElementException:
            return True

    def scrape_details(self, to_date, from_date='2022-08-09', energy_type=None):
        self.driver.find_element(By.LINK_TEXT, 'Zużycie').click()
        time.sleep(1)

        self.driver.find_element(
            By.XPATH, '//ul[@id="tabMenu"]/li/div').click()
        time.sleep(1)

        self._navigate_to_date(to_date)
        current_date = to_date

        energy_types_and_files = {'Oddana A-': 'Raport A- 30610346',
                                  'Pobrana A+': 'Raport A+ 30610346'}

        if energy_type == self._ENERGY_PRODUCED:
            energy_types_and_files.pop('Pobrana A+')
        if energy_type == self._ENRGY_USED:
            energy_types_and_files.pop('Oddana A-')

        while current_date != from_date:
            select = Select(self.driver.find_element(
                By.ID, 'meterobjecttochart'))

            for et in energy_types_and_files:
                select.select_by_visible_text(et)

                time.sleep(4)

                if self._is_data_present():                
                    self.driver.find_element(
                        By.XPATH, '//img[@title="Pobierz .xls z prezentowanych danych"]').click()
                    time.sleep(6)

                    self._rename_file(
                        org_filename=energy_types_and_files[et], current_date=current_date)
                
            current_date = self._navigate_to_day_before()

    def scrape_summary(self):
        self.driver.find_element(By.LINK_TEXT, 'Licznik').click()
        time.sleep(1)

        used = self.driver.find_element(By.ID, 'right').find_elements(By.TAG_NAME, 'tr')[
            0].find_element(By.CLASS_NAME, 'last').text
        used = used.replace(' ', '')
        used = used.replace(',', '.')

        used_snapshot_time = self.driver.find_element(
            By.CLASS_NAME, 'first').find_elements(By.TAG_NAME, 'div')[1].text

        produced = self.driver.find_element(By.ID, 'right').find_elements(By.TAG_NAME, 'tr')[
            2].find_element(By.CLASS_NAME, 'last').text
        produced = produced.replace(' ', '')
        produced = produced.replace(',', '.')

        produced_snaphot_time = self.driver.find_element(
            By.CLASS_NAME, 'first').find_elements(By.TAG_NAME, 'div')[1].text

        summary = {}
        summary['scraping_time'] = str(datetime.now())
        summary['used'] = {
            'snaphot_time': used_snapshot_time, 'value': float(used)}
        summary['produced'] = {
            'snaphot_time': produced_snaphot_time, 'value': float(produced)}

        with open(f'{self.summary_directory}/summary.json', 'a') as f:
            json.dump(summary, f)
            f.write("\n")

        return summary
