import gc
from os import path, getcwd

import hydra
import numpy as np
import pandas as pd


from src.cv import prepare_cv
from src.metrics import score_fn, save_confusion_matrix
from src.dataset import read_data, read_clean_data, reduce_mem_usage
from src.features import load_features
from src.mlflow import MlflowWriter
from src.models import LGBMRunner


@hydra.main(config_path="config.yaml")
def main(cfg):
    # mlflow
    writer = MlflowWriter(experiment_name='ion-baseline')
    writer.log_params_from_omegaconf_dict(cfg)

    # load dataset
    data_path = path.normpath(path.join(hydra.utils.get_original_cwd(), cfg.data.data_path))
    train_raw, test_raw, submission = read_data(data_path)
    train_clean, test_clean = read_clean_data(data_path)
    feat_path = path.normpath(path.join(hydra.utils.get_original_cwd(), cfg.data.feat_path))
    train_feat, test_feat = load_features(feat_path, cfg.data.features)
    train = reduce_mem_usage(pd.concat([train_raw, train_clean['clean_signal'], train_feat], axis=1))
    test = reduce_mem_usage(pd.concat([test_raw, test_clean['clean_signal'], test_feat], axis=1))
    del train_raw, test_raw, train_clean, test_clean, train_feat, test_feat
    gc.collect()

    # setup cv
    all_ignore_cols = cfg.all.ignore_cols + [cfg.all.target] + [cfg.cv.group]
    all_columns = [col for col in train.columns if col not in all_ignore_cols]
    writer.log_param('all_features', all_columns)

    # cv
    test_preds = []
    y_valid_preds = np.zeros(len(train))
    scores = {}
    cv = prepare_cv(cfg.cv.method, cfg.cv.n_splits, train, cfg.all.target, cfg.cv.group, seed=1234)
    for fold, (train_idx, valid_idx) in enumerate(cv):
        print('Start fold {}!'.format(fold+1))
        X_train, X_valid = train.loc[train_idx, all_columns], train.loc[valid_idx, all_columns]
        y_train, y_valid = train.loc[train_idx, cfg.all.target], train.loc[valid_idx, cfg.all.target]

        # training
        lgbm_runner = LGBMRunner(cfg.all.seed)
        model, _ = lgbm_runner.train(X_train, y_train, X_valid, y_valid, cfg.model)
        fi_path = path.join(getcwd(), 'fold_{}_fi.png'.format(fold+1))
        lgbm_runner.save_plot_feature_importance(model, fi_path)
        writer.log_artifact(fi_path)

        # validation
        y_valid_pred = lgbm_runner.predict(model, X_valid)
        macro_f1_score = np.mean(score_fn(y_valid, y_valid_pred))
        scores[f'fold_{fold+1}'] = macro_f1_score
        ct_path = path.join(getcwd(), 'fold_{}_ct.png'.format(fold+1))
        save_confusion_matrix(y_valid, y_valid_pred, ct_path)
        writer.log_artifact(ct_path)
        y_valid_preds[valid_idx] = y_valid_pred

        # test prediction
        pred_test_proba = lgbm_runner.predict(model, test[all_columns], proba=True)
        test_preds.append(pred_test_proba)

    # save log
    # save scores
    writer.log_metrics(scores)
    writer.log_metric('cv_score', np.mean(list(scores.values())))
    # save confusion matrix
    all_ct_path = path.join(getcwd(), 'all_ct.png')
    save_confusion_matrix(train[cfg.all.target], y_valid_preds, all_ct_path)
    writer.log_artifact(all_ct_path)
    # save other data
    writer.log_artifact(path.join(getcwd(), '.hydra/config.yaml'))
    writer.log_artifact(path.join(getcwd(), 'main.log'))


if __name__ == "__main__":
    main()
