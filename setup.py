from setuptools import setup, find_packages
setup(
    name='disk-memory-detect',
    version='0.1.0',
    packages=find_packages(),
    author='banfeb',
    description='用于检测磁盘存储变化的项目',
    long_description=open('README.md', encoding='utf-8').read(),
    long_description_content_type='text/markdown',
    install_requires=[
        "psutil",
        "mmh3",],
    entry_points={
        'console_scripts': [
            "dmd = dmd.cli.main:main",
        ]
    }
)