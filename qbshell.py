if __name__ == '__main__':
    import sys
    from os import path as P

    sys.path.append(P.join(P.abspath(P.dirname(__file__)), 'resources', 'lib'))

    from qobuz.shell import loop

    loop()
