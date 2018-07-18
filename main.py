from argparse import ArgumentParser
from lib import search_song, download_song, get_url_and_lyric
from os import path


def parse_args():
    parser = ArgumentParser(description='从咪咕音乐免费下载歌曲')
    parser.add_argument('-d', '--dir', help='歌曲保存目录(默认当前目录)', default='.')
    parser.add_argument('-l', '--lyric', help='下载歌词(如果有)', default=False, action='store_true')
    parser.add_argument('keyword', help='搜索关键字')
    return parser.parse_args()


if __name__ == '__main__':
    args = parse_args()
    items = search_song(args.keyword)
    print('搜索结果:')
    for i, item in enumerate(items):
        print('%d\t%s\t%s' % (i, item.name, item.singer))
    ids = input('\n要下载哪个?(多个用空格分开): ')
    for i in ids.split():
        try:
            item = items[int(i)]
            print('\t获取下载链接')
            url, lyric = get_url_and_lyric(item.id)
            print('\t正在下载', item.name)
            file_prefix = path.join(args.dir, item.name + '-' + item.singer)
            download_song(url, file_prefix + '.mp3')
            if args.lyric and lyric:
                with open(file_prefix + '.lyric', 'wt') as fp:
                    fp.write(lyric)
            print('\t完成')
        except Exception as e:
            print('\t下载失败:', e)
