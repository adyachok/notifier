#!/usr/bin/env python

from distutils.core import setup

setup(name='Notifier',
      version='1.0',
      description='Python Eye Care Utility',
      author='András Gyácsok',
      author_email='atti.dyachok@gmail.com',
      url='https://www.python.org/sigs/distutils-sig/',
      packages=['notifier'],
      package_dir={'notifier': 'src/notifier'},
      data_files=[('img', ['img/*.png']),
                  ('music', ['music/*.mp3'])],
      entry_points = {
        'console_scripts': ['notify=notify:main'],
    }
     )
