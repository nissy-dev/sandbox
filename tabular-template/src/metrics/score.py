from sklearn.metrics import f1_score


def score_fn(y_true, y_preds):
    return f1_score(y_true, y_preds, average='macro')
