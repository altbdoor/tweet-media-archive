import os
import time

from selenium import webdriver
from selenium.common.exceptions import NoSuchElementException

from wrappers.basic import TweetWrapper


class EngineDriver(object):
    engine = 'chrome'
    driver = None
    binary_path = ''
    driver_path = ''
    max_search_retry = 20

    def __init__(self, engine, binary_path, driver_path):
        self.engine = engine
        self.binary_path = binary_path
        self.driver_path = driver_path

    def start(self):
        if self.engine == 'chrome':
            from selenium.webdriver.chrome.options import Options
            options = Options()

            options.set_headless(headless=True)
            options.add_argument('--disable-gpu')
            options.add_argument('--log-level=3')
            options.add_argument('--mute-audio')
            options.add_experimental_option('prefs', {
                'profile.managed_default_content_settings.images': 2,
            })
            options.binary_location = self.binary_path

            driver = webdriver.Chrome(
                chrome_options=options,
                executable_path=self.driver_path,
            )

        elif self.engine == 'firefox':
            from selenium.webdriver.firefox.firefox_binary import FirefoxBinary
            from selenium.webdriver.firefox.options import Options

            options = Options()
            options.set_headless(headless=True)
            options.add_argument('--disable-gpu')

            profile = webdriver.FirefoxProfile()
            profile.set_preference('permissions.default.image', 2)
            profile.set_preference('media.volume_scale', '0.0')
            profile.set_preference('media.autoplay.enabled', False)

            binary = FirefoxBinary(self.binary_path)
            driver = webdriver.Firefox(
                firefox_profile=profile,
                firefox_options=options,
                firefox_binary=binary,
                executable_path=self.driver_path,
                log_file=os.devnull,
            )

        driver.set_window_size(1920, 1080)
        self.driver = driver

    def stop(self):
        self.driver.quit()

    def get_driver(self):
        return self.driver

    def load_url(self, url):
        self.driver.get(url)

    def search_element_by_xpath(self, xpath):
        counter = 0
        element = None

        while True:
            try:
                element = self.driver.find_element_by_xpath(xpath)
            except NoSuchElementException:
                pass

            counter += 1
            if counter >= self.max_search_retry or element is not None:
                self.driver.execute_script('return window.stop();')
                break
            else:
                time.sleep(0.5)

        return element


class TweetExtendedVideoWrapper(TweetWrapper):
    def get_all_video_url(self, engine_driver):
        url_list = []
        videos = self.soup.select('div.PlayableMedia--video div.PlayableMedia-player')

        if len(videos) > 0:
            engine_driver.load_url(f'https://mobile.twitter.com/{self.username}/status/{self.id}/video/1')
            video = engine_driver.search_element_by_xpath('//video')
            if video:
                url_list.append(video.get_attribute('src'))

        return url_list
