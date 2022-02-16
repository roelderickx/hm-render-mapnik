import setuptools

with open('README.md', 'r', encoding='utf-8') as fh:
    README = fh.read()

setuptools.setup(
    name="hm-render-mapnik",
    version="0.0.3",
    license='GNU General Public License (GNU GPL v3 or above)',
    author="Roel Derickx",
    author_email="hikingmap.pypi@derickx.be",
    description="Render a map for a given area to paper using mapnik",
    long_description=README,
    long_description_content_type="text/markdown",
    url="https://github.com/roelderickx/hm-render-mapnik",
    packages=setuptools.find_packages(),
    install_requires=['mapnik>=0.1'],
    python_requires='>=3.7',
    entry_points={
        'console_scripts': ['hm-render-mapnik = hm_render_mapnik.hm_render_mapnik:main']
    },
    classifiers=[
        'Environment :: Console',
        'Topic :: Scientific/Engineering :: GIS',
        'Development Status :: 5 - Production/Stable',
        'Programming Language :: Python :: 3',
        'License :: OSI Approved :: GNU General Public License (GPL)',
        'Operating System :: OS Independent',
    ],
)

