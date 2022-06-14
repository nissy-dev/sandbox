from src.dataset.read_data import read_data
from src.features.base import Feature, get_arguments
from src.features.constant import DATASET_PATH, FEATURE_PATH, SIGNAL_BATCH_SIZE, ROLLING_WINDOWS


class RollingStats(Feature):
    def create_features(self, train, test):
        # train
        signal_df = train['signal'].to_frame()
        train_batch_num = int(signal_df.shape[0]/SIGNAL_BATCH_SIZE)
        for window in ROLLING_WINDOWS:
            for i in range(train_batch_num):
                start = i * SIGNAL_BATCH_SIZE
                end = (i+1) * SIGNAL_BATCH_SIZE
                s = signal_df['signal'][start:end]
                signal_df.loc[start:end, 'roll_mean_' + str(window)] = s.rolling(window=window, min_periods=1).mean()
                signal_df.loc[start:end, 'roll_std_' + str(window)] = s.rolling(window=window, min_periods=1).std()
                signal_df.loc[start:end, 'roll_min_' + str(window)] = s.rolling(window=window, min_periods=1).min()
                signal_df.loc[start:end, 'roll_max_' + str(window)] = s.rolling(window=window, min_periods=1).max()
                signal_df.loc[start:end, 'roll_range_' + str(window)] = \
                    signal_df['roll_max_' + str(window)][start:end] - signal_df['roll_min_' + str(window)][start:end]
                signal_df.loc[start:end, 'roll_q10_' + str(window)] = s.rolling(window=window, min_periods=1).quantile(0.10)
                signal_df.loc[start:end, 'roll_q25_' + str(window)] = s.rolling(window=window, min_periods=1).quantile(0.25)
                signal_df.loc[start:end, 'roll_q50_' + str(window)] = s.rolling(window=window, min_periods=1).quantile(0.50)
                signal_df.loc[start:end, 'roll_q75_' + str(window)] = s.rolling(window=window, min_periods=1).quantile(0.75)

            self.train['roll_mean_' + str(window)] = signal_df['roll_mean_' + str(window)]
            self.train['roll_std_' + str(window)] = signal_df['roll_std_' + str(window)]
            self.train['roll_min_' + str(window)] = signal_df['roll_min_' + str(window)]
            self.train['roll_max_' + str(window)] = signal_df['roll_max_' + str(window)]
            self.train['roll_range_' + str(window)] = signal_df['roll_range_' + str(window)]
            self.train['roll_q10_' + str(window)] = signal_df['roll_q10_' + str(window)]
            self.train['roll_q25_' + str(window)] = signal_df['roll_q25_' + str(window)]
            self.train['roll_q50_' + str(window)] = signal_df['roll_q50_' + str(window)]
            self.train['roll_q75_' + str(window)] = signal_df['roll_q75_' + str(window)]

        # test
        signal_df = test['signal'].to_frame()
        test_batch_num = int(signal_df.shape[0]/SIGNAL_BATCH_SIZE)
        for window in ROLLING_WINDOWS:
            for i in range(test_batch_num):
                start = i * SIGNAL_BATCH_SIZE
                end = (i+1) * SIGNAL_BATCH_SIZE
                s = signal_df['signal'][start:end]
                signal_df.loc[start:end, 'roll_mean_' + str(window)] = s.rolling(window=window, min_periods=1).mean()
                signal_df.loc[start:end, 'roll_std_' + str(window)] = s.rolling(window=window, min_periods=1).std()
                signal_df.loc[start:end, 'roll_min_' + str(window)] = s.rolling(window=window, min_periods=1).min()
                signal_df.loc[start:end, 'roll_max_' + str(window)] = s.rolling(window=window, min_periods=1).max()
                signal_df.loc[start:end, 'roll_range_' + str(window)] = \
                    signal_df[start:end]['roll_max_' + str(window)] - signal_df[start:end]['roll_min_' + str(window)]
                signal_df.loc[start:end, 'roll_q10_' + str(window)] = s.rolling(window=window, min_periods=1).quantile(0.10)
                signal_df.loc[start:end, 'roll_q25_' + str(window)] = s.rolling(window=window, min_periods=1).quantile(0.25)
                signal_df.loc[start:end, 'roll_q50_' + str(window)] = s.rolling(window=window, min_periods=1).quantile(0.50)
                signal_df.loc[start:end, 'roll_q75_' + str(window)] = s.rolling(window=window, min_periods=1).quantile(0.75)

            self.test['roll_mean_' + str(window)] = signal_df['roll_mean_' + str(window)]
            self.test['roll_std_' + str(window)] = signal_df['roll_std_' + str(window)]
            self.test['roll_min_' + str(window)] = signal_df['roll_min_' + str(window)]
            self.test['roll_max_' + str(window)] = signal_df['roll_max_' + str(window)]
            self.test['roll_range_' + str(window)] = signal_df['roll_range_' + str(window)]
            self.test['roll_q10_' + str(window)] = signal_df['roll_q10_' + str(window)]
            self.test['roll_q25_' + str(window)] = signal_df['roll_q25_' + str(window)]
            self.test['roll_q50_' + str(window)] = signal_df['roll_q50_' + str(window)]
            self.test['roll_q75_' + str(window)] = signal_df['roll_q75_' + str(window)]


if __name__ == '__main__':
    args = get_arguments()
    train, test, _ = read_data(DATASET_PATH)
    featurizer = RollingStats(feat_dir=FEATURE_PATH)
    if featurizer.train_path.exists() and featurizer.test_path.exists() and not args.force:
        print(featurizer.name, 'has already created.')
    else:
        featurizer.run(train, test).save()
