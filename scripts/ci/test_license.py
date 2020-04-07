import os


_IGNORE_SUBDIRS = ['__pycache__', 'vendored_sdks', 'site-packages', 'env']


def main():
    home = '/home/vsts/work/1/s/'

    for d, sd, files in os.walk(home):
        print('-' * 30, d, '-' * 30)
        print(sd)

        # for i, x in enumerate(sd):
        #     if x in _IGNORE_SUBDIRS or x.startswith('.'):
        #         print(x)

        py_files = [os.path.join(d, p) for p in files if p.endswith('.py')]
        print(py_files)


if __name__ == '__main__':
    main()
