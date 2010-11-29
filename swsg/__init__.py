__version__ = '0.3.0'


class NoninstalledPackage(Exception):
    'raised if a required python package is not installed'
    def __init__(self, package_name):
        self.package_name = package_name

    def __str__(self):
        return 'the package {0!r} is not installed'.format(self.package_name)

    def __repr__(self):
        return '{0}({1})'.format(self.__class__.__name__, self.package_name)
