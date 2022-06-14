import gc
import pandas as pd


from src.dataset.read_data import read_data
from src.features.base import Feature, get_arguments
from src.features.load_features import load_features
from src.features.constant import DATASET_PATH, FEATURE_PATH, SIGNAL_BATCH_SIZE


class SignalDiff(Feature):
    def create_features(self, train, test):
        # train
        train_batch_num = int(train.shape[0]/SIGNAL_BATCH_SIZE)
        for c in [c1 for c1 in train.columns if c1 not in ['time', 'signal', 'open_channels']]:
            for j in range(train_batch_num):
                start = j * SIGNAL_BATCH_SIZE
                end = (j+1) * SIGNAL_BATCH_SIZE
                train.loc[start:end, c + '_msignal'] = train[start:end][c] - train[start:end]['signal']
            self.train[c + '_msignal'] = train[c + '_msignal']

        # test
        test_batch_num = int(test.shape[0]/SIGNAL_BATCH_SIZE)
        for c in [c1 for c1 in test.columns if c1 not in ['time', 'signal', 'open_channels']]:
            for j in range(test_batch_num):
                start = j * SIGNAL_BATCH_SIZE
                end = (j+1) * SIGNAL_BATCH_SIZE
                test.loc[start:end, c + '_msignal'] = test[start:end][c] - test[start:end]['signal']
            self.test[c + '_msignal'] = test[c + '_msignal']


if __name__ == '__main__':
    args = get_arguments()
    train_raw, test_raw, _ = read_data(DATASET_PATH)
    train_feat, test_feat = load_features(FEATURE_PATH, ['RollingStats', 'LagFeatures'])
    train = pd.concat([train_raw, train_feat], axis=1)
    test = pd.concat([test_raw, test_feat], axis=1)
    # consider memory
    del train_raw, test_raw, train_feat, test_feat
    gc.collect()
    featurizer = SignalDiff(feat_dir=FEATURE_PATH)
    if featurizer.train_path.exists() and featurizer.test_path.exists() and not args.force:
        print(featurizer.name, 'has already created.')
    else:
        featurizer.run(train, test).save()
