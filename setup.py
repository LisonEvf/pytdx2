from setuptools import setup, find_packages

setup(
    name="pytdx2",
    version="0.1.0",
    author="LisonEvf",
    author_email="lisonevf@gmail.com",
    description="A Python client for TDX stock data with MCP server",
    long_description=open("README.md", encoding='utf-8').read(),
    long_description_content_type="text/markdown",
    packages=find_packages(),
    install_requires=[
        'pandas',
        'numpy',
        'mcp[cli]'
    ],
    entry_points={
        'console_scripts': [
            'mcp-server-tdx=tdx_mcp.mcpServer:main',
        ],
    },
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
)
