from setuptools import setup, find_packages

setup(
    name='telegrambotlib',
    version='0.1.0',
    description='Библиотека для создания Telegram-ботов',
    author='Ваше Имя',
    packages=find_packages(where='src'),
    package_dir={'': 'src'},
    install_requires=[
        'requests'
    ],
    python_requires='>=3.7',
)
