import unittest
from sklearn.cross_validation import cross_val_score
from sklearn.datasets import load_boston, load_iris
from sklearn.metrics import roc_auc_score, make_scorer
from sklearn.preprocessing import LabelBinarizer
from sklearn.preprocessing.label import label_binarize
import pandas as pd

from xgboost_tools import XGBoostRegressor, XGBoostClassifier


def roc_auc_avg_score(y_true, y_score):
    y_bin = label_binarize(y_true, classes=sorted(set(y_true)))
    return roc_auc_score(y_bin, y_score)


class TestXGBoost(unittest.TestCase):
    def test_regressor(self):
        boston = load_boston()
        est = XGBoostRegressor(num_rounds=50, objective='reg:linear')

        scores = cross_val_score(estimator=est, X=boston.data, y=boston.target, cv=3)

        print(scores.mean(), scores.std())

    def test_classifier(self):
        iris = load_iris()
        est = XGBoostClassifier(num_rounds=50, objective='multi:softprob', num_class=3)

        scorer = make_scorer(roc_auc_avg_score, needs_proba=True)

        scores = cross_val_score(estimator=est, X=iris.data, y=iris.target, cv=3, scoring=scorer)

        print(scores.mean(), scores.std())

    def test_classifier_shifted_labels(self):
        iris = load_iris()
        est = XGBoostClassifier(num_rounds=50, objective='multi:softprob', num_class=3)

        scorer = make_scorer(roc_auc_avg_score, needs_proba=True)

        scores = cross_val_score(estimator=est, X=iris.data, y=iris.target+1, cv=3, scoring=scorer)

        print(scores.mean(), scores.std())

    def test_classifier_bin(self):
        iris = load_iris()
        target_bin = LabelBinarizer().fit_transform(iris.target).T[0]
        est = XGBoostClassifier(num_rounds=50, objective='reg:logistic')

        scores = cross_val_score(estimator=est, X=iris.data, y=target_bin, cv=3, scoring='roc_auc')

        print(scores.mean(), scores.std())

    def test_feature_importance(self):
        iris = load_iris()
        est = XGBoostClassifier(num_rounds=50, objective='multi:softprob', num_class=3)
        est.fit(pd.DataFrame(iris.data, columns=iris.feature_names), iris.target)

        print(est.get_fscore())