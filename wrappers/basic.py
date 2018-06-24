import datetime
import re


class TweetWrapper(object):
    soup = None
    username = None
    id = None
    timestamp = None

    background_image_id_re = re.compile(r'tweet_video_thumb\/(.+?).jpg')

    def __init__(self, soup, username):
        self.soup = soup
        self.username = username

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
        gifs = self.soup.select('div.PlayableMedia--gif div.PlayableMedia-player')

        for g in gifs:
            g_id = re.search(self.background_image_id_re, g.get('style'))
            if g_id:
                g_id = g_id.group(1)
                url_list.append(f'https://video.twimg.com/tweet_video/{g_id}.mp4')

        return url_list
