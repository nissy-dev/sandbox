from sklearn.model_selection import KFold, GroupKFold, StratifiedKFold, TimeSeriesSplit
from src.cv.stratified_group_kfold import StratifiedGroupKFold


def prepare_cv(cv_method, n_splits, train_df, target=None, group=None, seed=1234):
    if cv_method == "KFold":
        cv = KFold(n_splits=n_splits, shuffle=True, random_state=seed)
        return cv.split(train_df)
    elif cv_method == "TimeSeriesSplit":
        cv = TimeSeriesSplit(max_train_size=None, n_splits=n_splits)
        return cv.split(train_df)
    elif cv_method == "StratifiedKFold":
        if target is None:
            raise ValueError('{} must set target value'.format(cv_method))
        cv = StratifiedKFold(n_splits=n_splits, shuffle=True, random_state=seed)
        return cv.split(train_df, train_df[target])
    elif cv_method == "GroupKFold":
        if target is None or group is None:
            raise ValueError('{} must set target and group value'.format(cv_method))
        cv = GroupKFold(n_splits=n_splits, shuffle=True, random_state=seed)
        return cv.split(train_df, train_df[target], train_df[group])
    elif cv_method == "StratifiedGroupKFold":
        if target is None or group is None:
            raise ValueError('{} must set target and group value'.format(cv_method))
        cv = StratifiedGroupKFold(n_splits=n_splits, shuffle=True, random_state=seed)
        return cv.split(train_df, train_df[target], train_df[group])
    else:
        raise ValueError('{} is not supported.'.format(cv_method))
