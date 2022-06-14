import numpy as np
import matplotlib.pyplot as plt
from catboost import CatBoostClassifier, Pool

from src.metrics.score import score_fn


class MacroF1Metric(object):
    def get_final_error(self, error, weight):
        return error / (weight + 1e-38)

    def is_max_optimal(self):
        return True

    def evaluate(self, approxes, target, weight):
        best_class = np.argmax(approxes, axis=0)
        f1score = score_fn(best_class, target)
        return f1score, 0

        accuracy_sum = 0
        weight_sum = 0

        for i in range(len(target)):
            w = 1.0 if weight is None else weight[i]
            weight_sum += w
            accuracy_sum += w * (best_class[i] == target[i])

        return accuracy_sum, weight_sum


class CatBoostRunner:
    def __init__(self, seed):
        self.seed = seed

    def train(self, X_train, y_train, X_valid, y_valid, config):
        train_data = Pool(X_train, y_train)
        valid_data = Pool(X_valid, y_valid)
        model_params = {
            'learning_rate': config.lr,
            'num_iterations': config.num_iterations,
            'random_state': self.seed,
            'eval_metric': MacroF1Metric()
        }
        model = CatBoostClassifier(**model_params)
        model.fit(train_data, eval_set=valid_data, early_stopping_rounds=config.early_stopping_rounds,
                  use_best_model=True)
        return model

    def predict(self, model, X_test, proba=False):
        pred = model.predict(Pool(X_test))
        pred_proba = model.predict_proba(Pool(X_test))
        return pred_proba if proba else pred

    def save_plot_feature_importance(self, model, file_path):
        return
        # lgb.plot_importance(model, figsize=(12, 8), max_num_features=25)
        # plt.savefig(file_path)
