import click as c
import time as t
import vlc
from datetime import datetime


def validate_time(w, p, v):
    try:
        h, m = map(int, v.split(':', 2))
        if 0 < h > 23 or 0 < m > 59:
            raise c.BadParameter('I don\'t know this time')
        return h, m
    except ValueError:
        raise c.BadParameter('time needs to be in format h:m')


@c.command()
@c.option('-t', '--time',
          prompt='alarm time',
          help='alarm time (hh:mm)',
          callback=validate_time)
@c.option('-s', '--sound',
          prompt='sound file',
          help='sound file',
          type=c.Path(exists=True, dir_okay=False, resolve_path=True))
def weckr(time, sound):
    h = time[0]
    m = time[1]

    now = datetime.now().time()
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
        'I\'ll wake you up at ' + c.style(str(h) + ':' + str(m).zfill(2), bold=True, fg='red') +
        ' playing ' + c.style(c.format_filename(sound), fg='blue') + ' in less then ' +
        c.style(str(hh) + ' h ' + str(mm) + ' min', bold=True, fg='green'))

    t.sleep((hh * 60 + mm) * 60 - now.second)

    c.echo('WAKE UP!')
    
    p = vlc.MediaPlayer('file://' + sound)
    p.play()

    input("Press ENTER to stop me...")
