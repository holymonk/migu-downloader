import requests
from urllib.parse import quote
from bs4 import BeautifulSoup as BS
import bs4
from collections import namedtuple
import re

sess = requests.Session()
sess.headers.update({
    'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_12_3) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/67.0.3396.99 Safari/537.36',

})
sess.mount('http://', requests.adapters.HTTPAdapter(pool_connections=3, pool_maxsize=3, max_retries=3))
sess.mount('https://', requests.adapters.HTTPAdapter(pool_connections=3, pool_maxsize=3, max_retries=3))

SongItem = namedtuple('SongItem', 'name, singer, id')


def search_song(keyword):
    url = 'http://music.migu.cn/v2/search?type=song&keyword=' + quote(keyword)
    bs = BS(sess.get(url, headers={'Referer': 'http://music.migu.cn/v2'}).text, 'lxml')

    def parse_item(item: bs4.element.Tag):
        """
        :return SongItem(name, singer, id)
        """
        mid = item.attrs['mid']
        name = item.select_one('.song-name-text').text.strip()
        singer = item.select_one('.song-singer').text
        if singer:
            singer = re.sub(r'\s+', ' ', singer).strip()
        return SongItem(name, singer, mid)

    return [parse_item(div) for div in bs.select('#js_songlist div.songlist-item.single-item')]


def get_url_and_lyric(song_id):
    detail = sess.get('http://music.migu.cn/v2/async/audioplayer/playurl/' + song_id,
                      headers={
                          'Referer': 'http://music.migu.cn/v2/player/audio',
                          'X-Requested-With': 'XMLHttpRequest'}
                      ).json()
    return detail['songAuditionUrl'], detail['dynamicLyric']


def download_song(url, dst):
    resp = sess.get(url, timeout=20, stream=True)
    if resp.ok:
        with open(dst, 'wb') as fp:
            for chunk in resp.iter_content(chunk_size=256):
                fp.write(chunk)
    else:
        resp.raise_for_status()
