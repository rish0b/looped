from setuptools import setup, find_packages

setup(
    name="post",
    version="0.1.0",  
    author="rish0b",  
    author_email="rishabravikumar@gmail.com", 
    description="Post delivers seamless collaboration between AI and humans, right to your inbox.",
    long_description=open("README.md").read(),
    long_description_content_type="text/markdown",
    url="https://github.com/rish0b/post",  
    packages=find_packages(), 
    install_requires=[
        "requests",
    ],
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.6",
)
