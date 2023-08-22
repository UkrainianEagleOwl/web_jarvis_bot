from setuptools import setup, find_packages

setup(
    name='jarvis_assistant_bot',
    version='2.0',
    description='Welcome to Jarvis, your personal assistant! Jarvis is here to help you stay organized and manage your contacts, reminders, notes, and files efficiently.',
    author='UkrainianEagleOwl',
    url='https://github.com/UkrainianEagleOwl/web_jarvis_bot/tree/main',
    packages=find_packages(),
    include_package_data=True,
    
    entry_points={
        'console_scripts': [
            'Jarvis=src.main:main',
        ],
    },
    install_requires=[
        'prettytable',
        'prompt_toolkit',
        'colorama',
        'cryptography',
        'openai',
        'keyboard',
        'names',
        'websockets',
        'aiofiles'
    ],
)
