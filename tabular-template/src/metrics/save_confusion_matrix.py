import seaborn as sns
import matplotlib.pyplot as plt
from sklearn.metrics import confusion_matrix


def save_confusion_matrix(y_true, y_pred, file_path):
    cm = confusion_matrix(y_true, y_pred)
    sns.heatmap(cm, annot=True, map='Reds')
    plt.savefig(file_path)
