import os
import sys
import argparse
import logging
import time
import vlc
import datetime

import xml.etree.ElementTree as Et
import urllib.request
from dateutil.parser import parse

formats = ['mp3', 'wav', 'opus', 'wma', 'ogg']


def weckr(sound_file: str, wakeup_time: datetime.time, news: bool, news_time: int, music_fade: int,
          music_max: int) -> None:
    """
    command line alarm clock takes audio file or directory of audio files
    """

    if news_time is not None:
        news = True
    else:
        news_time = 5

    news_echo = ''
    if news:
        news_echo = ' and the ' + 'news'
        # if v:
        news_echo += ' after ' + str(news_time) + ' min'

    # TODO check if sound_file is playable

    # compute sleep
    now = datetime.datetime.now()
    alarm_time = datetime.datetime.combine(now.date(), wakeup_time)
    if alarm_time < now:
        alarm_time += datetime.timedelta(days=1)
    delta = alarm_time - now

    # announce sleep
    log.debug('I\'ll wake you up at ' + str(alarm_time.hour) + ':' + str(alarm_time.minute).zfill(2) +
              ' playing ' + os.path.basename(sound_file) + news_echo + ' in less then ' +
              str(delta.seconds // 3600) + ' h ' + str((delta.seconds // 60) % 60 + 1) + ' min')

    log.info('Now I\'m going to sleep. You also should do so.')

    # finally sleep
    time.sleep(delta.total_seconds())

    # wake up
    log.info('*yawning*')
    log.debug('Wake up!!')

    # play background sound
    play_sound(sound_file, music_fade, music_max)

    # play news if wanted
    if news:
        log.info('Going to play news in ' + str(news_time) + ' min.')
        time.sleep(news_time * 60 - 5)
        play_news(5, 40, music_max)

    input("\nPress ENTER to stop")


def play_sound(sound_path: str, music_fade: int, music_max: int) -> None:
    """
    triggers sounds
    :param sound_path: path to main sound file
    :param music_fade: time in seconds to fade in sound
    :param music_max: maximum voulme level
    """
    log.debug('Playing file: ' + os.path.basename(sound_path))

    global vlc_music
    vlc_music = vlc.MediaPlayer(sound_path)
    vlc_music.play()

    for vol in range(0, music_max):
        vlc_music.audio_set_volume(vol)
        time.sleep(music_fade / 100)
        log.info('Increasing volume to: ' + str(vol) + '%')


def play_news(news_fade: int, music_volume: int, music_max: int) -> None:
    """
    fetches DLF news XML and play latest (of full hour) news
    """
    resp = urllib.request.urlopen('http://www.deutschlandfunk.de/podcast-nachrichten.1257.de.podcast.xml')

    log.debug('\nFetched news XML successfully.')

    xml = resp.read().decode('utf-8')
    root = Et.fromstring(xml).find('channel')
    for item in root.findall('item'):
        if parse(item.find('pubDate').text).time().minute == 0:
            news_url = item.find('link').text
            for vol in range(music_max, music_volume, -1):
                if vlc_music:
                    vlc_music.audio_set_volume(vol)
                    time.sleep(news_fade / 100)
                    log.info('Decrease volume to: ' + str(vol) + '%')
            vlc_news = vlc.MediaPlayer(news_url)
            log.debug("now playing news")
            vlc_news.audio_set_volume(100)
            vlc_news.play()
            while vlc_news.get_state() != vlc.State.Ended:
                time.sleep(100)
            for vol in range(music_volume, music_max):
                if vlc_music:
                    vlc_music.audio_set_volume(vol)
                    time.sleep(news_fade / 100)
                    log.info('Increasing volume to: ' + str(vol) + '%')
            break


def get_ext(sound: str) -> None:
    """
    gets files extension if valid
    :param sound:
    :return:
    """
    ext = os.path.splitext(sound)[1][1:]
    if ext not in formats:
        log.warning('Error:' +
                    ' The audio file extension ' + ext +
                    ' is not supported. Please use one of these: ' + ', '.join(formats) + '.')
        exit(1)


def main():
    global log
    log = logging.getLogger(__name__)

    parser = argparse.ArgumentParser(description="weckr: a CLI alarm clock with unicorn features ")
    parser.add_argument("-v", "--verbose", dest="verbose_count",
                        action="count", default=0,
                        help="increases log verbosity for each occurence.")
    parser.add_argument("-t",
                        "--time",
                        help="Alarm time",
                        required=True,
                        type=lambda d: datetime.datetime.strptime(d, '%H:%M').time())
    parser.add_argument("-n", "--news", help="Includes latest DLF news (default: 5 min delay).",
                        action="store_true")
    parser.add_argument("-N",
                        "--news-time",
                        help="Includes latest DLF news with specific time delay (in min).",
                        type=lambda n: int(n) if int(n) > 0 else 0)
    parser.add_argument("-m",
                        "--max-volume",
                        help="set the maximum volume of music",
                        type=lambda n: int(n) if int(n) > 0 and int(n) < 100 else 50)
    parser.add_argument("-f",
                        "--fade-time",
                        help="time the music is fading",
                        type=lambda n: int(n) if int(n) > 0 else 30)
    parser.add_argument('sound_file',
                        type=str)

    if len(sys.argv) == 1:
        parser.print_help()
        sys.exit(1)

    args = parser.parse_args()

    # handler = logging.FileHandler('weckr.log')
    # handler.setLevel(logging.INFO)
    # formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    # handler.setFormatter(formatter)
    # log.addHandler(handler)

    output = logging.StreamHandler()
    output_formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
    output.setFormatter(output_formatter)
    log.addHandler(output)

    log.setLevel(max(3 - args.verbose_count, 0) * 10)

    try:
        weckr(args.sound_file, args.time, args.news, args.news_time, args.fade_time, args.max_volume)
    except KeyboardInterrupt:
        log.debug("Exiting by interrupt")


if __name__ == "__main__":
    main()
