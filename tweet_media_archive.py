#!/bin/usr/env python

import urllib.request
import urllib.parse
import argparse
import datetime
import json
import re
import sys

from bs4 import BeautifulSoup


class TweetWrapper(object):
    soup = None
    id = None
    timestamp = None

    background_image_id_re = re.compile(r'tweet_video_thumb\/(.+?).jpg')

    def __init__(self, soup):
        self.soup = soup

        self.id = self._get_id()
        self.timestamp = self._get_timestamp()

    def _get_id(self):
        id = self.soup.get('data-tweet-id')
        return id

    def _get_timestamp(self):
        timestamp = self.soup.select_one('span._timestamp.js-short-timestamp')
        if timestamp:
            epoch = int(timestamp.get('data-time'))
            return datetime.datetime.fromtimestamp(epoch)
        else:
            raise Exception('Unable to find timestamp in tweet!')

    def get_formatted_timestamp(self):
        return self.timestamp.strftime('%Y-%m-%d %H:%M:%S')

    def get_all_image_url(self):
        url_list = []
        images = self.soup.select('div.AdaptiveMedia-photoContainer.js-adaptive-photo')

        for i in images:
            img_url = i.get('data-image-url')
            url_list.append(f'{img_url}:orig')

        return url_list

    def get_all_gif_url(self):
        url_list = []
        gifs = self.soup.select('div.PlayableMedia-player')

        for g in gifs:
            g_id = re.search(self.background_image_id_re, g.get('style'))
            if g_id:
                g_id = g_id.group(1)
                url_list.append(f'https://video.twimg.com/tweet_video/{g_id}.mp4')

        return url_list

# ========================================


def run_scrape(
    debug=False, username='',
    exclude_gif=False, exclude_image=False,
    output=None,
    min_datetime=None, max_datetime=None,
):
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
            tweet_wrapper = TweetWrapper(tweet.div)
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

            if is_less_than_min_datetime:
                break

        if not next_pointer or is_less_than_min_datetime:
            break

    sys.stdout.close()
    if output is not None:
        sys.stdout = original_stdout


# ========================================

def parse_args():
    parser = argparse.ArgumentParser(
        description=(
            'Gets a list of URLs for images and GIFs of a twitter user. '
            'The URL list can then be passed to curl or wget to batch download. '
            'To note, twitter only allows a maximum of 35 iterations, which means '
            'probably not everything will be archived.'
            '\n\n'
            'Examples: \n'
            '- List all GIFs by user "tkmiz" from now until 28 Dec 2017, 10.34pm \n'
            '  ./%(prog)s -u tkmiz --exclude_image --min_datetime="2017-12-28 22:34:00" \n'
            '\n'
            '- List everything by user "MowtenDoo" and save it to a text file \n'
            '  ./%(prog)s -u Mowtendoo -o example.txt'
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

    return parser.parse_args()


if __name__ == '__main__':
    args = parse_args()
    args = vars(args)

    run_scrape(**args)
