from setuptools import setup, find_packages

setup(
    name="pyremote",
    version="2.0.0",
    description="轻量级跨平台远程控制工具（开源项目）",
    long_description=open("docs/README.md", encoding="utf-8").read(),
    long_description_content_type="text/markdown",
    author="PyRemote Team",
    author_email="pyremote@example.com",
    url="https://github.com/your-username/PyRemote",  # 替换为实际GitHub地址
    packages=find_packages(),
    include_package_data=True,
    entry_points={
        "console_scripts": [
            "pyremote = pyremote.main:main",  # 命令行入口：直接运行pyremote
        ]
    },
    install_requires=open("requirements.txt", encoding="utf-8").read().splitlines(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Topic :: System :: Remote Access",
    ],
    python_requires=">=3.8",
    keywords="remote-control, python, open-source, cross-platform",
)