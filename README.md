# tweet-media-archive
[![FOSSA Status](https://app.fossa.io/api/projects/git%2Bgithub.com%2Faltbdoor%2Ftweet-media-archive.svg?type=shield)](https://app.fossa.io/projects/git%2Bgithub.com%2Faltbdoor%2Ftweet-media-archive?ref=badge_shield)


Requires [Python 3.6.x](https://www.python.org/),
[BeautifulSoup4](https://www.crummy.com/software/BeautifulSoup/)
and optionally [Selenium-Python](https://www.seleniumhq.org/).

```
$ python tweet_media_archive.py -h | fold -sw 80
usage: tweet_media_archive.py [-h] [--debug] -u USERNAME [--exclude_gif]
                              [--exclude_image] [-o OUTPUT]
                              [--min_datetime MIN_DATETIME]
                              [--max_datetime MAX_DATETIME] [--include_video]
                              [--engine_driver_type {chrome,firefox}]
                              [--binary_path BINARY_PATH]
                              [--driver_path DRIVER_PATH]

Gets a list of URLs for images, GIFs and possibly videos of a twitter user. The
URL list can then be passed to curl or wget to batch download. To note, twitter
only allows a maximum of 35 iterations, which means probably not everything
will be archived.

The script is only able to scrape for videos with the help of a web browser,
and Selenium web driver, which means you need to have either Google
Chrome/Chromium or Mozilla Firefox installed, and also their respective
WebDrivers.

Examples:
- List all GIFs by user "tkmiz" from now until 28 Dec 2017, 10.34pm
  ./tweet_media_archive.py -u tkmiz --exclude_image --min_datetime="2017-12-28
22:34:00"

- List everything by user "MowtenDoo" and save it to a text file
  ./tweet_media_archive.py -u Mowtendoo -o example.txt

- List only videos by user "Mowtendoo" with Chrome.
  ./tweet_media_archive.py -u Mowtendoo --exclude_image --exclude_gif
--include_video --engine_driver_type=chrome --binary_path="C:\Program Files
(x86)\Google\Application\chrome.exe" --driver_path=".\drivers\chromedriver.exe"

optional arguments:
  -h, --help            show this help message and exit
  --debug               Enables debug mode, which prints out the results in a
CSV format of "{tweet date time}, {tweet id}, {image/GIF url}" for debugging
purposes.
  -u USERNAME, --username USERNAME
                        twitter username.
  --exclude_gif         Excludes GIFs from the result.
  --exclude_image       Excludes images from the result.
  -o OUTPUT, --output OUTPUT
                        Directs output to a file. If unspecified, the output
will be redirected to stdout.
  --min_datetime MIN_DATETIME
                        Minimum date. Format: YYYY-MM-DD hh:mm:ss
  --max_datetime MAX_DATETIME
                        Maximum date. Format: YYYY-MM-DD hh:mm:ss
  --include_video       Includes videos from the result.
  --engine_driver_type {chrome,firefox}
                        The engine driver type. Defaults to "chrome".
  --binary_path BINARY_PATH
                        The binary path to the browser executable.
  --driver_path DRIVER_PATH
                        The driver path to the browser driver executable.
```


### Video support notes

The script is able to scrape for twitter videos with the help of Selenium, but
you have to set up:

- A web browser
    - [Google Chrome v59 and above](https://developers.google.com/web/updates/2017/04/headless-chrome)
    - [Chromium v59 and above](https://chromium.woolyss.com/) works too
    - [Mozilla Firefox v56 and above](https://developer.mozilla.org/en-US/Firefox/Headless_mode)
- The browser's WebDriver
    - [ChromeDriver](https://sites.google.com/a/chromium.org/chromedriver/home) for Chrome or Chromium
    - [GeckoDriver](https://github.com/mozilla/geckodriver/) for Firefox

I have personally tested on Windows 10, Python 3.6.5 with Mozilla Firefox
v60.0.2 and Chromium v66.0.3359.117. It works, but its rather slow since the
browser has to load the page and wait for the video to be loaded in the DOM.

I wanted to implement [PhantomJS](https://github.com/ariya/phantomjs) as well,
but it [does not support the video element](https://github.com/ariya/phantomjs/issues/10839),
and more importantly, the [development work has stopped](https://github.com/ariya/phantomjs/issues/15344).


### Example output

```
$ python ./tweet_media_archive.py -u tkmiz --min_datetime="2017-12-28 22:34:00" | head -10
https://pbs.twimg.com/media/DfcYtVgVAAAXmIr.jpg:orig
https://pbs.twimg.com/media/DfXmWOmVAAAbh5t.jpg:orig
https://pbs.twimg.com/media/DfSNmraVMAA5jJO.jpg:orig
https://pbs.twimg.com/media/DfQ8Wa5UYAAkBZs.jpg:orig
https://pbs.twimg.com/media/De8pczoU8AAyGM7.jpg:orig
https://pbs.twimg.com/media/De3eReGUEAART06.jpg:orig
https://pbs.twimg.com/media/Dey2_ksUYAEsSgv.jpg:orig
https://pbs.twimg.com/media/DenYDMDVMAMJ70B.jpg:orig
https://pbs.twimg.com/media/DenKVHeU0AA9XFO.jpg:orig
https://pbs.twimg.com/media/DeSdVITVMAE9qCQ.jpg:orig
```


### Thanks

- To the following resources, so I did not have to crack my head on decoding how twitter works on browser.
    - https://github.com/anuragrana/Python-Scripts/blob/master/tweets_scrapper.py
    - https://github.com/Foo-Manroot/tweet-feed/blob/master/scraper.py
    - https://foo-manroot.github.io/post/scraping/twitter/2017/09/05/scraping-twitter.html
- For the post that started it all.
    - https://archive.rebeccablacktech.com/g/thread/66258138


### License

GPLv3


[![FOSSA Status](https://app.fossa.io/api/projects/git%2Bgithub.com%2Faltbdoor%2Ftweet-media-archive.svg?type=large)](https://app.fossa.io/projects/git%2Bgithub.com%2Faltbdoor%2Ftweet-media-archive?ref=badge_large)