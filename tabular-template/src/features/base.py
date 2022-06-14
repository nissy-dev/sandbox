

import time
import argparse
from abc import ABCMeta, abstractmethod
from pathlib import Path
from contextlib import contextmanager

import pandas as pd


@contextmanager
def timer(name):
    t0 = time.time()
    print(f'[{name}] start')
    yield
    print(f'[{name}] done in {time.time() - t0:.0f} s')


class Feature(metaclass=ABCMeta):
    def __init__(self, feat_dir='.', suffix=''):
        self.name = self.__class__.__name__
        self.train = pd.DataFrame()
        self.test = pd.DataFrame()
        self.dir = feat_dir
        self.suffix = suffix
        self.train_path = Path(self.dir) / f'{self.name}_train.ftr'
        self.test_path = Path(self.dir) / f'{self.name}_test.ftr'

    def run(self, train, test):
        with timer(self.name):
            self.create_features(train, test)
            suffix = '_' + self.suffix if self.suffix else ''
            self.train.columns = self.train.columns + suffix
            self.test.columns = self.test.columns + suffix
        return self

    @abstractmethod
    def create_features(self, train, test):
        raise NotImplementedError

    def save(self):
        self.train.to_feather(str(self.train_path))
        self.test.to_feather(str(self.test_path))
        print('{} columns were created.'.format(len(self.train.columns)))


def get_arguments():
    parser = argparse.ArgumentParser()
    parser.add_argument('--force', '-f', action='store_true',
                        help='Overwrite existing files')
    return parser.parse_args()
