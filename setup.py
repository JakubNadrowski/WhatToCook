from setuptools import setup, find_packages

setup(name='WhatToCookPackage',

      version='0.1',

      description='A Fijian Cookbook script, keeping your kitchen varied and healthy',

      author='Jakub Nadrowski',

      license='MIT',

      packages=find_packages(include=['WhatToCookPackage']),

      install_requires=['pandas', 'requests', 'beautifulsoup4', 'reportlab', 'imageio']
      )