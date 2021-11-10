import setuptools

setuptools.setup(
    name="symspellpy_ko",
    version="0.1.1",
    license='GNU General Public License v3 (GPLv3)',
    author="Heegyu Kim",
    author_email="heekue83@gmail.com",
    description="symspellpy를 한글 특성에 맞춰서 수정한 라이브러리. 자소분해를 이용해 더 정확한 오타교정을 해준다.",
    long_description=open('README.md', encoding='utf-8').read(),
    url="https://github.com/HeegyuKim/symspellpy-ko",
    packages=setuptools.find_packages(),
    include_package_data=True,
    package_data = {
        '': ["*.txt"]
    },
    classifiers=[
        # 패키지에 대한 태그
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: GNU General Public License v3 (GPLv3)",
        "Operating System :: OS Independent"
    ],
)