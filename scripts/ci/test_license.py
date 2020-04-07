import os


_IGNORE_SUBDIRS = ['__pycache__', 'vendored_sdks', 'site-packages', 'env']


def main():
    home = '/home/vsts/work/1/s/'

    for d, sd, files in os.walk(home):
        print('-' * 10, d)

        for i, x in enumerate(sd):
            if x in _IGNORE_SUBDIRS or x.startswith('.'):
                print(x)


if __name__ == '__main__':
    main()
