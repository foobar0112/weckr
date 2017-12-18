import os
import click as c
import time as t
import threading
import vlc
import xml.etree.ElementTree as Et
import urllib.request
from datetime import datetime
from dateutil.parser import parse

v = False
# TODO: complete list of supported extensions
formats = ['mp3', 'wav', 'opus', 'wma', 'ogg']


def verb(msg: str) -> None:
    if v:
        c.echo(msg)


def validate_time(ctx, param, val: str) -> (int, int):
    """
    callback for validation of inserted time. time should be in format h:m
    :param w:
    :param p:
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
            n.play()
            break


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

        play_news()
    else:
        file_path = ''
        num = -1
        for (root, dirs, files) in os.walk(sound_path):
            num = datetime.now().day % len([f for f in files if os.path.splitext(f)[1][1:] in formats])
            file_path = os.sep.join([root, files[num]])

        verb('Playing file number ' + str(num) + ' in directory: ' + c.style(file_path, fg='blue'))


@c.command()
@c.option('-t', '--time',
          prompt='Alarm time',
          help='alarm time (hh:mm)',
          callback=validate_time)
@c.option('-s', '--sound',
          prompt='Sound file',
          help='sound file (intended to be a bit longer…)',
          type=c.Path(exists=True, resolve_path=True))
@c.option('-n', '--news',
          help='includes latest DLF news (after 5 minutes)',
          is_flag=True)
@c.option('-N', '--news-time',
          help='includes latest DLF news after N minutes',
          type=int)
@c.option('-v', '--verbose',
          help='toggles verbose mode',
          is_flag=True)
def weckr(time: (int, int), sound: str, news: bool, news_time: int, verbose: bool) -> None:
    """
    command line alarm clock
    """

    global v
    v = verbose

    if news_time >= 0:
        news = True
    else:
        news_time = 5

    ext = ''

    if os.path.isfile(sound):
        ext = os.path.splitext(sound)[1][1:]
        if ext not in formats:
            c.echo(c.style('Error:', bold=True, fg='red') +
                   ' The audio file extension ' + c.style(ext, fg='white') +
                   ' is not supported. Please use one of these: ' + ', '.join(formats) + '.')
            exit(1)
    else:
        for (root, dirs, files) in os.walk(sound):
            if len([f for f in files if os.path.splitext(f)[1][1:] in formats]) == 0:
                c.echo(c.style('Error:', bold=True, fg='red') +
                       ' The directory ' + c.style(sound, fg='blue') +
                       ' doesn\'t contain any audio files.')
                exit(1)

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

    c.echo(
        'I\'ll wake you up at ' + c.style(str(h) + ':' + str(m).zfill(2), bold=True, fg='white') +
        ' playing ' + c.style(os.path.basename(sound), fg='blue') + ' in less then ' +
        c.style(str(hh) + ' h ' + str(mm) + ' min', bold=True, fg='white'))
    verb('Now I\'m going to sleep. You also should do so.')

    # t.sleep((hh * 60 + mm) * 60 - now.second)

    verb('*yawning*')
    c.echo(c.style('Wake up!!', bold=True, bg='red', fg='white', blink=True))

    play_sound(sound, ext, 60)

    if news:
        news_thread = threading.Timer(news_time * 60, play_news())
        news_thread.start()

    input("Press ENTER to stop me...")
