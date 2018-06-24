#!/bin/usr/env python

import argparse
import datetime
import json
import os
import sys
import urllib.parse
import urllib.request

from bs4 import BeautifulSoup


def run_scrape(
    debug=False, username='',
    exclude_gif=False, exclude_image=False, include_video=False,
    output=None,
    min_datetime=None, max_datetime=None,
    engine_driver_type='chrome', binary_path='', driver_path='',
):
    wrapper_class = None
    engine_driver = None

    if include_video:
        from wrappers.extended import TweetExtendedVideoWrapper, EngineDriver
        wrapper_class = TweetExtendedVideoWrapper

        engine_driver = EngineDriver(engine_driver_type, binary_path, driver_path)
        engine_driver.start()
    else:
        from wrappers.basic import TweetWrapper
        wrapper_class = TweetWrapper

    first_run = False
    soup = None
    next_pointer = None

    original_stdout = None

    if output is not None:
        original_stdout = sys.stdout
        sys.stdout = open(output, 'w')

    def soup_non_retweet_match(tag):
        return (
            tag.name == 'li' and
            tag.get('data-item-type') == 'tweet' and
            not tag.div.has_attr('data-retweet-id')
        )

    def dump_to_output(url_list, debug=False, id=None, timestamp=None):
        for item in url_list:
            if debug:
                print(f'{timestamp}, {id}, {item}')
            else:
                print(item)

    while True:
        if first_run is False:
            first_run = True

            url = f'https://twitter.com/{username}/media'
            r = urllib.request.urlopen(url)

            soup = BeautifulSoup(r.read(), 'html.parser')

            next_pointer = soup.select_one('div[data-min-position]')
            next_pointer = next_pointer.get('data-min-position')

        else:
            url = f'https://twitter.com/i/profiles/show/{username}/media_timeline'
            params = {
                'include_available_features': 1,
                'include_entities': 1,
                'reset_error_state': 'false',
                'max_position': next_pointer,
            }
            params = urllib.parse.urlencode(params)

            r = urllib.request.urlopen(f'{url}?{params}')
            json_data = json.loads(r.read())

            next_pointer = json_data.get('min_position')
            soup = BeautifulSoup(json_data.get('items_html'), 'html.parser')

        is_less_than_min_datetime = False
        tweet_list = soup.find_all(soup_non_retweet_match)

        for tweet in tweet_list:
            tweet_wrapper = wrapper_class(soup=tweet.div, username=username)
            is_tweet_within_date_range = True

            if min_datetime is not None and tweet_wrapper.timestamp < min_datetime:
                is_tweet_within_date_range = False
                is_less_than_min_datetime = True

            if max_datetime is not None and tweet_wrapper.timestamp > max_datetime:
                is_tweet_within_date_range = False

            if is_tweet_within_date_range:
                if not exclude_image:
                    images = tweet_wrapper.get_all_image_url()
                    dump_to_output(
                        images,
                        debug=debug,
                        id=tweet_wrapper.id,
                        timestamp=tweet_wrapper.get_formatted_timestamp(),
                    )

                if not exclude_gif:
                    gifs = tweet_wrapper.get_all_gif_url()
                    dump_to_output(
                        gifs,
                        debug=debug,
                        id=tweet_wrapper.id,
                        timestamp=tweet_wrapper.get_formatted_timestamp(),
                    )

                if include_video:
                    videos = tweet_wrapper.get_all_video_url(engine_driver)
                    dump_to_output(
                        videos,
                        debug=debug,
                        id=tweet_wrapper.id,
                        timestamp=tweet_wrapper.get_formatted_timestamp(),
                    )

            sys.stdout.flush()

            if is_less_than_min_datetime:
                break

        if not next_pointer or is_less_than_min_datetime:
            break

    if engine_driver:
        engine_driver.stop()

    sys.stdout.close()
    if output is not None:
        sys.stdout = original_stdout


# ========================================

def parse_args():
    parser = argparse.ArgumentParser(
        description=(
            'Gets a list of URLs for images, GIFs and possibly videos of a twitter user. '
            'The URL list can then be passed to curl or wget to batch download. '
            'To note, twitter only allows a maximum of 35 iterations, which means '
            'probably not everything will be archived.'
            '\n\n'
            'The script is only able to scrape for videos with the help of a web browser, '
            'and Selenium web driver, which means you need to have either '
            'Google Chrome/Chromium or Mozilla Firefox installed, and also their '
            'respective WebDrivers.'
            '\n\n'
            'Examples: \n'
            '- List all GIFs by user "tkmiz" from now until 28 Dec 2017, 10.34pm \n'
            '  ./%(prog)s -u tkmiz --exclude_image --min_datetime="2017-12-28 22:34:00" \n'
            '\n'
            '- List everything by user "MowtenDoo" and save it to a text file \n'
            '  ./%(prog)s -u Mowtendoo -o example.txt \n'
            '\n'
            '- List only videos by user "Mowtendoo" with Chrome. \n'
            '  ./%(prog)s -u Mowtendoo --exclude_image --exclude_gif --include_video '
            '--engine_driver_type=chrome --binary_path="C:\\Program Files (x86)\\Google\\Application\\chrome.exe" '
            '--driver_path=".\\drivers\\chromedriver.exe"'
        ),
        formatter_class=argparse.RawTextHelpFormatter,
    )
    parser.add_argument(
        '--debug', action='store_true',
        help=(
            'Enables debug mode, which prints out the results in a CSV format of '
            '"{tweet date time}, {tweet id}, {image/GIF url}" for debugging purposes.'
        ),
    )
    parser.add_argument(
        '-u', '--username', type=str, required=True,
        help='twitter username.',
    )

    parser.add_argument(
        '--exclude_gif', action='store_true',
        help='Excludes GIFs from the result.',
    )
    parser.add_argument(
        '--exclude_image', action='store_true',
        help='Excludes images from the result.',
    )

    parser.add_argument(
        '-o', '--output', type=str, default=None,
        help=(
            'Directs output to a file. If unspecified, the output will be '
            'redirected to stdout.'
        ),
    )

    def arg_date_type(d):
        try:
            return datetime.datetime.strptime(d, '%Y-%m-%d %H:%M:%S')
        except ValueError:
            msg = f'Not a valid date: "{d}".'
            raise argparse.ArgumentTypeError(msg)

    parser.add_argument(
        '--min_datetime', type=arg_date_type, default=None,
        help='Minimum date. Format: YYYY-MM-DD hh:mm:ss',
    )
    parser.add_argument(
        '--max_datetime', type=arg_date_type, default=None,
        help='Maximum date. Format: YYYY-MM-DD hh:mm:ss',
    )

    parser.add_argument(
        '--include_video', action='store_true',
        help='Includes videos from the result.',
    )
    parser.add_argument(
        '--engine_driver_type', type=str,
        choices=('chrome', 'firefox'), default='chrome',
        help='The engine driver type. Defaults to "chrome".',
    )
    parser.add_argument(
        '--binary_path', type=str, default=None,
        help='The binary path to the browser executable.',
    )
    parser.add_argument(
        '--driver_path', type=str, default=None,
        help='The driver path to the browser driver executable.',
    )

    args = parser.parse_args()
    if args.include_video:
        if args.binary_path is None or args.driver_path is None:
            msg = (
                '--binary_path and --driver_path are both required '
                'if --include_video is used.'
            )
            raise argparse.ArgumentTypeError(msg)

        for path in (args.binary_path, args.driver_path, ):
            if not os.path.exists(path):
                msg = f'File not found for the path "{path}"'
                raise argparse.ArgumentTypeError(msg)

    return args


if __name__ == '__main__':
    args = parse_args()
    args = vars(args)

    run_scrape(**args)
