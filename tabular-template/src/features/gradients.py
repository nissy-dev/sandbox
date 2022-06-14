import numpy as np


from src.dataset.read_data import read_data
from src.features.base import Feature, get_arguments
from src.features.constant import DATASET_PATH, FEATURE_PATH, N_GRADS, SIGNAL_BATCH_SIZE


class SignalGradients(Feature):
    def create_features(self, train, test):
        # train
        train_g = train['signal'].copy()
        train_batch_num = int(train_g.shape[0]/SIGNAL_BATCH_SIZE)
        for i in range(N_GRADS):
            for j in range(train_batch_num):
                start = j * SIGNAL_BATCH_SIZE
                end = (j+1) * SIGNAL_BATCH_SIZE
                train_g[start:end] = np.gradient(train_g[start:end].values)
            self.train['grad_' + str(i+1)] = train_g

        # test
        test_g = test['signal'].copy()
        test_batch_num = int(test_g.shape[0]/SIGNAL_BATCH_SIZE)
        for i in range(N_GRADS):
            for j in range(test_batch_num):
                start = j * SIGNAL_BATCH_SIZE
                end = (j+1) * SIGNAL_BATCH_SIZE
                test_g[start:end] = np.gradient(test_g[start:end].values)
            self.test['grad_' + str(i+1)] = test_g


if __name__ == '__main__':
    args = get_arguments()
    train, test, _ = read_data(DATASET_PATH)
    featurizer = SignalGradients(feat_dir=FEATURE_PATH)
    if featurizer.train_path.exists() and featurizer.test_path.exists() and not args.force:
        print(featurizer.name, 'has already created.')
    else:
        featurizer.run(train, test).save()
