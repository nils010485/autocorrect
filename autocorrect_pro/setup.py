from setuptools import setup, find_packages

setup(
    name="autocorrect_pro",
    version="1.0.0",
    packages=find_packages(),
    include_package_data=True,
    package_data={
        'autocorrect_pro': ['templates/*', 'static/*'],
    },
    data_files=[
        ('templates', ['templates/faveicon.ico']),
    ],
    install_requires=[
        'flask',
        'PyQt6',
        'PyQt6-WebEngine',
        'google-generativeai',
        'anthropic',
        'openai',
        'pyperclip',
        'rich',
        'pynput'
    ],
)
