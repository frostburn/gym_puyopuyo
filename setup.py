from setuptools import Extension, setup

core = Extension(
    'puyocore',
    sources=['puyocore.c'],
)


if __name__ == '__main__':
    setup(
        setup_requires=['setuptools>=34.0', 'setuptools-gitver'],
        gitver=True,
        ext_modules=[core],
    )
