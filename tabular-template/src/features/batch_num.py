from src.dataset.read_data import read_data
from src.features.base import Feature, get_arguments
from src.features.constant import DATASET_PATH, FEATURE_PATH, SIGNAL_BATCH_SIZE


class BatchNumber(Feature):
    def create_features(self, train, test):
        self.train['batch_num'] = train.index // SIGNAL_BATCH_SIZE
        self.test['batch_num'] = test.index // SIGNAL_BATCH_SIZE


if __name__ == '__main__':
    args = get_arguments()
    train, test, _ = read_data(DATASET_PATH)
    featurizer = BatchNumber(feat_dir=FEATURE_PATH)
    if featurizer.train_path.exists() and featurizer.test_path.exists() and not args.force:
        print(featurizer.name, 'has already created.')
    else:
        featurizer.run(train, test).save()
