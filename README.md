# tweet-media-archive

```
$ python tweet_media_archive.py -h | fold -sw 80
usage: tweet_media_archive.py [-h] [--debug] -u USERNAME [--exclude_video]
                              [--exclude_image] [-o OUTPUT]
                              [--min_datetime MIN_DATETIME]
                              [--max_datetime MAX_DATETIME]

Gets a list of URLs for images and videos of a twitter user. The URL list can
then be passed to curl or wget to batch download. To note, twitter only allows
a maximum of 35 iterations, which means probably not everything will be
archived.

Examples:
- List all videos by user "tkmiz" from now until 28 Dec 2017, 10.34pm
  ./tweet_media_archive.py -u tkmiz --exclude_image --min_datetime="2017-12-28
22:34:00"

- List everything by user "MowtenDoo" and save it to a text file
  ./tweet_media_archive.py -u Mowtendoo -o example.txt

optional arguments:
  -h, --help            show this help message and exit
  --debug               Enables debug mode, which prints out the results in a
CSV format of "{tweet date time}, {tweet id}, {image/video url}" for debugging
purposes.
  -u USERNAME, --username USERNAME
                        twitter username.
  --exclude_video       Excludes videos from the result.
  --exclude_image       Excludes images from the result.
  -o OUTPUT, --output OUTPUT
                        Directs output to a file. If unspecified, the output
will be redirected to stdout.
  --min_datetime MIN_DATETIME
                        Minimum date. Format: YYYY-MM-DD hh:mm:ss
  --max_datetime MAX_DATETIME
                        Maximum date. Format: YYYY-MM-DD hh:mm:ss
```


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


### License

GPLv3
