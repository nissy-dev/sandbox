import numpy as np
import lightgbm as lgb
import matplotlib.pyplot as plt


from src.metrics.score import score_fn


class LGBMRunner:
    def __init__(self, seed):
        self.seed = seed

    def metric(self, preds, dtrain):
        labels = dtrain.get_label()
        assert len(labels) == len(preds)
        print(labels.shape)
        print(preds.shape)
        preds = np.argmax(preds, axis=0)
        return ('MacroF1Metric', score_fn(labels, preds), True)

    def train(self, X_train, y_train, X_valid, y_valid, config):
        train_data = lgb.Dataset(X_train, y_train)
        valid_data = lgb.Dataset(X_valid, y_valid)
        model_params = {
            'objective': config.objective,
            'learning_rate': config.lr,
            'num_class': config.num_class,
            'num_iterations': config.num_iterations,
            'max_depth': config.max_depth,
            'num_leaves': config.num_leaves,
            'random_state': self.seed,
            'num_threads': config.num_threads,
        }
        model = lgb.train(model_params, train_set=train_data, valid_sets=valid_data,
                          early_stopping_rounds=config.early_stopping_rounds, feval=self.metric)
        return model, model.best_iteration

    def predict(self, model, X_test, proba=False):
        pred_proba = model.predict(X_test, num_iteration=model.best_iteration)
        return pred_proba if proba else np.argmax(pred_proba, axis=0)

    def save_plot_feature_importance(self, model, file_path):
        lgb.plot_importance(model, figsize=(12, 8), max_num_features=25)
        plt.savefig(file_path)
