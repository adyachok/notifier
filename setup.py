# -*- coding: utf-8 -*-
#!/usr/bin/env python

from setuptools import setup

setup(name='EyeNotifier',
      version='1.3',
      description='Python Eye Care Utility',
      author='András Gyácsok',
      author_email='atti.dyachok@gmail.com',
      packages=['eye_notifier'],
      package_dir={'eye_notifier': 'src/eye_notifier'},
      data_files=[('eye_notifier/img', ['img/bell.png',
                                        'img/money_increase.png',
                                        'img/ying_yang.png']),
                  ('eye_notifier/music', ['music/be-gentle-with-yourself.mp3',
                                          'music/drum-patterns-march-1.mp3'])],
      entry_points = {
        'console_scripts': ['eye-notify=eye_notifier.eye_notify:main'],
    }
     )
