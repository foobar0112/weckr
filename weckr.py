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

class bcolors:
    HEADER = '\033[95m'
    OKBLUE = '\033[94m'
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'


def weckr(sound_file: str, wakeup_time: datetime.time, news_time: int, music_fade: int,
          music_max: int) -> None:
    """
    command line alarm clock takes audio file or directory of audio files
    """

    news_echo = '.'
    if news_time:
        news_echo = ' and the ' + 'news' + ' after ' + str(news_time) + ' min.'

    check_media(sound_file)

    # compute sleep
    delta = get_time_delta(wakeup_time)

    # announce sleep
    sleep_echo = 'I\'ll wake you up '
    if wakeup_time == 'now':
        sleep_echo += 'now'
    else: 
        sleep_echo += 'at ' + str(wakeup_time.hour) + ':' + str(wakeup_time.minute).zfill(2) + ' in less then ' + bcolors.WARNING + str(delta.seconds // 3600) + ' h ' + str((delta.seconds // 60) % 60 + 1) + ' min' + bcolors.ENDC
              
    sleep_echo += ' playing ' + bcolors.BOLD + os.path.basename(sound_file) + bcolors.ENDC + news_echo
    
    log.debug(sleep_echo)

    log.info('Now I\'m going to sleep. You also should do so.')

    # finally sleep
    time.sleep(delta.total_seconds())

    # wake up
    log.info('*yawning*')
    log.debug(bcolors.FAIL + 'Wake up!!' + bcolors.ENDC)

    # play background sound
    play_sound(sound_file, music_fade, music_max)

    # play news if wanted
    if news_time:
        log.info('Going to play news in ' + str(news_time) + ' min.')
        time.sleep(news_time * 60 - 5)
        play_news(10, 40, music_max)
    else:
        log.info('No news will be played.')

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
        time.sleep(music_fade * 60 / 100)
        log.debug('Increasing volume to: ' + str(vol) + '%')


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


def get_time_delta(wakeup_time: datetime.time):
    """
    computes how long to wait till wake up
    :return: datetime.timedelta
    """
    now = datetime.datetime.now()
    if wakeup_time == 'now':
        return now - now
    alarm_time = datetime.datetime.combine(now.date(), wakeup_time)
    if alarm_time < now:
        alarm_time += datetime.timedelta(days=1)
    return alarm_time - now


def check_media(sound_file: str):
    """
    check if sound_file is playable
    :param sound_file:
    :return:
    """
    test_vlc = vlc.MediaPlayer(sound_file)
    if test_vlc.will_play():
        log.error("Media file is not playable")
        sys.exit(2)


def init_log():
    global log
    log = logging.getLogger(__name__)

    output = logging.StreamHandler()
    output_formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
    output.setFormatter(output_formatter)
    log.addHandler(output)


def init_parser():
    parser = argparse.ArgumentParser(description="weckr: a CLI alarm clock with unicorn features ")
    parser.add_argument("-v", "--verbose", dest="verbose_count",
                        action="count", default=0,
                        help="increases log verbosity for each occurence.")
    parser.add_argument("-t",
                        "--time",
                        help="Alarm time",
                        required=True,
                        type=lambda d: datetime.datetime.strptime(d, '%H:%M').time() if not d == 'now' else 'now')
    parser.add_argument("-n", "--news", help="Includes latest DLF news (default: 5 min delay).",
                        action="store_true")
    parser.add_argument("-N",
                        "--news-time",
                        help="Includes latest DLF news with specific time delay (in min).",
                        type=lambda n: int(n) if int(n) > 0 else 0)
    parser.add_argument("-m",
                        "--max-volume",
                        help="set the maximum volume of music",
                        type=lambda n: int(n) if int(n) > 0 and int(n) < 100 else 100)
    parser.add_argument("-f",
                        "--fade-time",
                        help="time the music is fading",
                        type=lambda n: int(n) if int(n) > 0 else 30)
    parser.add_argument('sound_file',
                        type=str)
    if len(sys.argv) == 1:
        parser.print_help()
        sys.exit(1)

    return parser.parse_args()


def main():
    init_log()
    args = init_parser()

    log.setLevel(max(3 - args.verbose_count, 0) * 10)

    if args.max_volume is None:
        args.max_volume = 100

    if args.fade_time is None:
        args.fade_time = 30

    if not (args.news is False and args.news_time is None):
        if args.news_time is None:
            args.news_time = 5

    try:
        weckr(args.sound_file, args.time, args.news_time, args.fade_time, args.max_volume)
    except KeyboardInterrupt:
        log.debug("Exiting by interrupt")


if __name__ == "__main__":
    main()
