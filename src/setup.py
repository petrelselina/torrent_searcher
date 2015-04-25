from setuptools import setup, find_packages

setup(
    name='TorrentSearcher',
    version='0.1',
    packages=find_packages(),
    url='https://github.com/omerbenamram/torrent_searcher',
    license='LGPL',
    author='Omer',
    author_email='omerbenamram@gmail.com',
    description='A Simple Torrent Searcher',
    setup_requires=['requests', 'logbook', 'BeautifulSoup4', 'html5lib', 'lxml',
                    'humanfriendly']
)
