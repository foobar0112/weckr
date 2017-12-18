import os
import click as c
import time as t
import vlc
import xml.etree.ElementTree as Et
import urllib.request
from datetime import datetime
from dateutil.parser import parse

v = False
# TODO: complete list of supported extensions
formats = ['mp3', 'wav', 'opus', 'wma', 'ogg']


def validate_time(ctx, param, val: str) -> (int, int):
    """
    callback for validation of inserted time. time should be in format h:m
    :param ctx:
    :param param:
    :param val: value
    :return: tuple (h,m) of hour and minute
    """
    try:
        h, m = map(int, val.split(':', 2))
        if 0 < h > 23 or 0 < m > 59:
            raise c.BadParameter('This is not a valid time.')
        return h, m
    except ValueError:
        raise c.BadParameter('h:m format for time parameter --time is required.')


def validate_news_time(ctx, param, val: int) -> int:
    """
    callback for validation of news delay time. should be positive integer
    :param ctx:
    :param param:
    :param val: value
    :return: news delay time
    """
    if val is int and val < 0:
        raise c.BadParameter('This is not a valid news delay time.')
    return val


@c.command()
@c.argument('sound_file',
            type=c.Path(exists=True, resolve_path=True))
@c.option('-t', '--time',
          prompt='Alarm time',
          help='Takes alarm time (h:m).',
          callback=validate_time)
@c.option('-n', '--news',
          help='Includes latest DLF news (default: 5 min delay).',
          is_flag=True)
@c.option('-N', '--news-time',
          help='Includes latest DLF news with specific time delay (in min).',
          type=int,
          callback=validate_news_time)
@c.option('-v', '--verbose',
          help='Toggles verbose mode.',
          is_flag=True)
def weckr(sound_file: str, time: (int, int), news: bool, news_time: int, verbose: bool) -> None:
    """
    command line alarm clock takes audio file or directory of audio files
    """

    # handle options
    global v
    v = verbose

    if news_time is not None:
        news = True
    else:
        news_time = 5

    news_echo = ''
    if news:
        news_echo = ' and the ' + c.style('news', fg='white')
        if v:
            news_echo += ' after ' + str(news_time) + ' min'

    # check path
    ext = ''
    if os.path.isfile(sound_file):
        ext = get_ext(sound_file)
    else:
        for (root, dirs, files) in os.walk(sound_file):
            count = len([f for f in files if os.path.splitext(f)[1][1:] in formats])
            if count == 0:
                c.echo(c.style('Error:', bold=True, fg='red') +
                       ' The directory ' + c.style(sound_file, fg='blue') +
                       ' doesn\'t contain any audio files.')
                exit(1)
            else:
                num = datetime.now().day % count
                verb('Chose file number ' + str(num) + ' in directory: ' + c.style(sound_file, fg='blue'))
                sound_file = os.sep.join([root, files[num]])
                ext = get_ext(sound_file)
                break

    # compute sleep
    h = time[0]
    m = time[1]

    now = datetime.now()
    hh = h - now.hour
    mm = m - now.minute

    if mm == 0 and hh == 0:
        hh = 24
    else:
        if mm < 0:
            mm += 60
            hh -= 1
        if hh < 0:
            hh += 24

    # announce sleep
    c.echo(
        'I\'ll wake you up at ' + c.style(str(h) + ':' + str(m).zfill(2), bold=True, fg='white') +
        ' playing ' + c.style(os.path.basename(sound_file), fg='blue') + news_echo + ' in less then ' +
        c.style(str(hh) + ' h ' + str(mm) + ' min', bold=True, fg='white'))

    verb('Now I\'m going to sleep. You also should do so.')

    # finally sleep
    t.sleep((hh * 60 + mm) * 60 - now.second)

    # wake up
    verb('*yawning*')
    c.echo(c.style('Wake up!!', bold=True, bg='red', fg='white', blink=True))

    # play background sound
    play_sound(sound_file, ext, 60)

    # play news if wanted
    if news:
        verb('Going to play news in ' + c.style(str(news_time), fg='white') + ' min.')
        t.sleep(news_time * 60)
        play_news()

    input("Press ENTER to stop me...")


def play_sound(sound_path: str, ext: str, fade: int) -> None:
    """
    triggers sounds
    :param sound_path: path to main sound file
    :param ext: file extension of sound file
    :param fade: time in seconds to fade in sound
    """
    if ext != '':
        verb('Playing file: ' + c.style(os.path.basename(sound_path), fg='blue'))

        s = vlc.MediaPlayer(sound_path)
        s.play()

        for vol in range(0, 100):
            s.audio_set_volume(vol)
            t.sleep(fade / 100)
            verb('Increasing volume to: ' + str(vol) + '%')


def play_news() -> None:
    """
    fetches DLF news XML and play latest (of full hour) news
    """
    resp = urllib.request.urlopen('http://www.deutschlandfunk.de/podcast-nachrichten.1257.de.podcast.xml')
    xml = resp.read().decode('utf-8')
    root = Et.fromstring(xml).find('channel')
    for item in root.findall('item'):
        if parse(item.find('pubDate').text).time().minute == 0:
            news_url = item.find('link').text
            n = vlc.MediaPlayer(news_url)
            n.audio_set_volume(100)
            n.play()
            break


def get_ext(sound: str) -> str:
    """
    gets files extension if valid
    :param sound:
    :return:
    """
    ext = os.path.splitext(sound)[1][1:]
    if ext not in formats:
        c.echo(c.style('Error:', bold=True, fg='red') +
               ' The audio file extension ' + c.style(ext, fg='white') +
               ' is not supported. Please use one of these: ' + ', '.join(formats) + '.')
        exit(1)
    return ext


def verb(msg: str) -> None:
    """
    helper function for printing verbose messages
    :param msg: message
    """
    if v:
        c.echo(msg)
