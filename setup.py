from setuptools import setup

setup(
    name='TorrentSearcher',
    version='0.1',
    packages=['src', 'src.base'],
    url='https://github.com/omerbenamram/torrent_searcher',
    license='',
    author='Omer',
    author_email='omerbenamram@gmail.com',
    description='A Simple Torrent Searcher', requires=['requests', 'logbook', 'BeautifulSoup4', 'html5lib', 'lxml',
                                                       'humanfriendly']
)
