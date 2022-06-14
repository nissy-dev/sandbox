from src.dataset.read_data import read_clean_data
from src.features.base import Feature, get_arguments
from src.features.constant import DATASET_PATH, FEATURE_PATH, SIGNAL_BATCH_SIZE, SHIFT_PERIODS


class LagFeatures(Feature):
    def create_features(self, train, test):
        # train
        train_g = train['clean_signal'].to_frame()
        train_batch_num = int(train_g.shape[0]/SIGNAL_BATCH_SIZE)
        for p in SHIFT_PERIODS:
            for col in ['clean_signal']:
                for i in range(train_batch_num):
                    start = i * SIGNAL_BATCH_SIZE
                    end = (i+1) * SIGNAL_BATCH_SIZE
                    train_g.loc[start:end, col + '_shifted_' + str(p)] = \
                        train_g[col][start:end].shift(periods=p, fill_value=0)
                self.train[col + '_shifted_' + str(p)] = train_g[col + '_shifted_' + str(p)].values

        # test
        test_g = train['clean_signal'].to_frame()
        test_batch_num = int(test_g.shape[0]/SIGNAL_BATCH_SIZE)
        for p in SHIFT_PERIODS:
            for col in ['clean_signal']:
                for i in range(test_batch_num):
                    start = i * SIGNAL_BATCH_SIZE
                    end = (i+1) * SIGNAL_BATCH_SIZE
                    test_g.loc[start:end, col + '_shifted_' + str(p)] = \
                        test_g[col][start:end].shift(periods=p, fill_value=0)
                self.test[col + '_shifted_' + str(p)] = test_g[col + '_shifted_' + str(p)].values


if __name__ == '__main__':
    args = get_arguments()
    train, test = read_clean_data(DATASET_PATH)
    featurizer = LagFeatures(feat_dir=FEATURE_PATH)
    if featurizer.train_path.exists() and featurizer.test_path.exists() and not args.force:
        print(featurizer.name, 'has already created.')
    else:
        featurizer.run(train, test).save()
