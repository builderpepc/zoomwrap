from distutils.core import setup
import pathlib

here = pathlib.Path(__file__).parent.resolve()
long_description = (here / 'README.md').read_text(encoding='utf-8')

setup(
  name = 'zoomwrap',
  packages = ['zoomwrap'],
  version = '0.1',
  license='MIT',
  description = 'A module containing classes that can be easily serialized to JSON for use with Zoom\'s APIs.',   # Give a short description about your library
  author = 'builderpepc',
  author_email = 'troy.hiruka@gmail.com',
  url = 'https://github.com/builderpepc/zoomwrap',
  download_url = 'https://github.com/builderpepc/zoomwrap/archive/v0.1.tar.gz',
  keywords = ['zoom', 'zoom.us', 'zoom-api', 'bot'],
  install_requires=[
          'requests',
          'ujson', # Faster json
          'regex'
      ],
  classifiers=[
    'Development Status :: 3 - Alpha',
    'Intended Audience :: Developers',
    'Topic :: Software Development :: Build Tools',
    'License :: OSI Approved :: MIT License',
    'Programming Language :: Python :: 3',
    'Programming Language :: Python :: 3.4',
    'Programming Language :: Python :: 3.5',
    'Programming Language :: Python :: 3.6',
    'Programming Language :: Python :: 3.7',
    'Programming Language :: Python :: 3.8',
    'Programming Language :: Python :: 3.9',
  ],
  long_description=long_description,
)