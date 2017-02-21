import copy
from nilearn._utils import CacheMixin
from sklearn.base import BaseEstimator, clone
from sklearn.externals.joblib import Memory
from sklearn.utils.metaestimators import if_delegate_has_method


def _cached_call(estimator, method, *args, **kwargs):
    func = getattr(estimator, method)
    param_dict = estimator.get_params().keys()
    for param in kwargs:
        if param in param_dict:
            value = kwargs.pop(param)
            estimator.set_params(**{param: value})
    return func(*args, **kwargs)


# memory_level = 1 -> fit is cached
# memory_level = 2 -> everything is cached
class CachedEstimator(BaseEstimator, CacheMixin):
    def __init__(self, estimator, memory=Memory(cachedir=None),
                 ignore=None,
                 memory_level=1, ignored_params=None):
        self.estimator = estimator
        self.ignore = ignore
        self.memory = memory
        self.memory_level = memory_level
        self.ignored_params = ignored_params

    def score(self, X, y=None):
        """Call score with cache.

        Parameters
        ----------
        X : array-like, shape = [n_samples, n_features]
            Input data, where n_samples is the number of samples and
            n_features is the number of features.

        y : array-like, shape = [n_samples] or [n_samples, n_output], optional
            Target relative to X for classification or regression;
            None for unsupervised learning.

        Returns
        -------
        score : float

        """
        return self._cache(_cached_call,
                           func_memory_level=2,
                           ignore=self.ignore)(self.estimator_,
                                               'score',
                                               X, y)

    @if_delegate_has_method(delegate=('estimator_', 'estimator'))
    def predict(self, X):
        """Call predict with cache.

        Parameters
        -----------
        X : indexable, length n_samples
            Must fulfill the input assumptions of the
            underlying estimator.

        """
        return self._cache(_cached_call,
                           func_memory_level=2,
                           ignore=self.ignore)(self.estimator_,
                                               'predict',
                                               X)

    @if_delegate_has_method(delegate=('estimator_', 'estimator'))
    def predict_proba(self, X):
        """Call predict_proba with cache.

        Parameters
        -----------
        X : indexable, length n_samples
            Must fulfill the input assumptions of the
            underlying estimator.

        """
        return self._cache(_cached_call,
                           func_memory_level=2,
                           ignore=self.ignore)(self.estimator_,
                                               'predict_proba',
                                               X)

    @if_delegate_has_method(delegate=('estimator_', 'estimator'))
    def predict_log_proba(self, X):
        """Call predict_log_proba with cache.
        Parameters
        -----------
        X : indexable, length n_samples
            Must fulfill the input assumptions of the
            underlying estimator.

        """
        return self._cache(_cached_call,
                           func_memory_level=2,
                           ignore=self.ignore)(self.estimator_,
                                               'predict_log_proba',
                                               X)

    @if_delegate_has_method(delegate=('estimator_', 'estimator'))
    def decision_function(self, X):
        """Call decision_function with cache.
        Parameters
        -----------
        X : indexable, length n_samples
            Must fulfill the input assumptions of the
            underlying estimator.

        """
        return self._cache(_cached_call,
                           func_memory_level=2,
                           ignore=self.ignore)(self.estimator_,
                                               'decision_function',
                                               X)

    @if_delegate_has_method(delegate=('estimator_', 'estimator'))
    def transform(self, X):
        """Call transform with cache.

        Parameters
        -----------
        X : indexable, length n_samples
            Must fulfill the input assumptions of the
            underlying estimator.

        """
        return self._cache(_cached_call,
                           func_memory_level=2,
                           ignore=self.ignore)(self.estimator_,
                                               'transform',
                                               X)

    @if_delegate_has_method(delegate=('estimator_', 'estimator'))
    def inverse_transform(self, Xt):
        """Call inverse_transform with cache.

        Parameters
        -----------
        Xt : indexable, length n_samples
            Must fulfill the input assumptions of the
            underlying estimator.

        """
        return self._cache(_cached_call,
                           func_memory_level=2,
                           ignore=self.ignore)(self.estimator_,
                                               'inverse_transform',
                                               Xt)

    def _cache(self, func, func_memory_level=1, shelve=False, **kwargs):
        param_dict = self.estimator.get_params()
        ignored_param_dict = {param: param_dict[param]
                              for param in self.ignored_params}
        res = CacheMixin._cache(self, func,
                                func_memory_level=func_memory_level,
                                shelve=shelve,
                                **ignored_param_dict,
                                **kwargs)
        return res

    def fit(self, X, y):
        """Call fit with cache.

        Parameters
        ----------
        X : array-like, shape = [n_samples, n_features]
            Input data, where n_samples is the number of samples and
            n_features is the number of features.

        y : array-like, shape = [n_samples] or [n_samples, n_output], optional
            Target relative to X for classification or regression;
            None for unsupervised learning.
        """
        self.estimator_ = clone(self.estimator)
        # self.estimator_.__getstate__ = self._getstate
        self.estimator_ = self._cache(_cached_call,
                                      func_memory_level=1,
                                      ignore=self.ignored_params)(
            self.estimator_, 'fit', X, y)
        return self
    #
    # def _getstate(self):
    #     print('Monkey patch')
    #     state = self.estimator_.__dict__
    #     if self.ignored_attributes:
    #         for attribute in self.ignored_attributes:
    #             state.pop(attribute, None)
    #     return state


        # def __setattr__(self, name, value):
        #     if name in ['memory', 'memory_level', 'ignore',
        #                 'estimator', 'estimator_']:
        #         super().__setattr__(name, value)
        #     else:
        #         if hasattr(self.estimator, name):
        #             setattr(self.estimator, name, value)
        #             if hasattr(self, 'estimator_'):
        #                 setattr(self.estimator_, name, value)
        #         else:
        #             super().__setattr__(name, value)
        #
        # def __getattr__(self, name):
        #     if name in ['memory', 'memory_level', 'ignore',
        #                 'estimator', 'estimator_']:
        #         return super().__getattr__(name)
        #     else:
        #         if hasattr(self.estimator_, name):
        #             return getattr(self.estimator_, name)
        #         elif hasattr(self.estimator, name):
        #             return getattr(self.estimator, name)
        #         else:
        #             return super().__getattr__(name)