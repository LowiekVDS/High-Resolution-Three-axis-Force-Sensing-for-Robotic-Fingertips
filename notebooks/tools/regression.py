import numpy as np
import os
import dill
from sklearn.linear_model import LinearRegression, Ridge, ARDRegression
from sklearn.metrics import mean_squared_error
from sklearn.model_selection import train_test_split
from sklearn.compose import ColumnTransformer, make_column_transformer
from sklearn.pipeline import make_pipeline, make_union
from sklearn.preprocessing import PolynomialFeatures, FunctionTransformer
from sklearn import set_config
from sklearn.multioutput import MultiOutputRegressor, RegressorChain
from sklearn.compose import TransformedTargetRegressor
from sklearn.base import BaseEstimator, TransformerMixin

def save_taxel_models(taxel_models, subdir, name):
    
    while '/' in name:
        subdir = os.path.join(subdir, name.split('/')[0])
        name = name.split('/')[-1]
        
    save_path = os.path.join(os.getcwd(), '..', 'models', subdir)

    if not os.path.exists(save_path):
        os.makedirs(save_path)
        
    with open(os.path.join(save_path, name), 'wb') as f:
        dill.dump(taxel_models, f)
        
set_config(display='diagram')

POLY_DEGREE = True

def calculate_RMSE(y_true, y_pred):

    N = y_true.shape[0]
    
    mse_custom = np.sum((y_true - y_pred)**2, axis=0) / N
    mse_custom = np.sqrt(mse_custom)
    
    return np.mean(mse_custom)
  
def calculate_NMSE(y_true, y_pred):

    N = y_true.shape[0]
    
    mse_custom = np.sum((y_true - y_pred) ** 2, axis=0) / N    

    max = np.max(y_pred, axis=0)
    min = np.min(y_pred, axis=0)
    
    diff = max - min
    
    for i in range(len(mse_custom)):
        mse_custom[i] = mse_custom[i] / diff[i]
        
    mse_custom = np.sum(mse_custom) / len(mse_custom)
    
    return mse_custom

class PowerTransformer(BaseEstimator, TransformerMixin):
    def __init__(self, power=-1):
        self.power = power
    
    def fit(self, X, y=None):
        return self  # No fitting necessary for this transformer
    
    def transform(self, X):
        return np.power(X, self.power)

def create_regression_pipeline_and_fit(X, Y, debug = True, preserve_time=False, alpha=1, degree=3):
  
  X_train, X_test, y_train, y_test = train_test_split(X, Y, test_size=0.2, shuffle=True)

  pipeline = make_pipeline(
    PolynomialFeatures(degree=degree, include_bias=True), 
    LinearRegression(fit_intercept=False) # Should not fit the intercept since "include_bias=True" in PolynomialFeatures actually does this by adding 1 as a feature
  )
  
  pipeline.fit(X_train, y_train)

  if debug:
    
    print("Score: ", pipeline.score(X_test, y_test))
    print("MSE: ", mean_squared_error(y_test, pipeline.predict(X_test)))
  
  return pipeline, X_train, X_test, y_train, y_test

class CombinedModel:
  
  def __init__(self, component_models) -> None:
    self.component_models = component_models
    
  def predict(self, X):
    
    predictions = []
    
    for i, model in enumerate(self.component_models):

      predictions.append(model.predict(X[:, i].reshape(-1, 1))[:, 0])
    
    return np.array(predictions).T
  
from sklearn.ensemble import HistGradientBoostingRegressor
from sklearn.metrics import mean_squared_error
from sklearn.model_selection import train_test_split, GridSearchCV
from sklearn.ensemble import HistGradientBoostingRegressor
  
def create_gradient_tree_and_fit(X, Y):

    X_train, X_test, y_train, y_test = train_test_split(X, Y, test_size=0.2, shuffle=True)

    reg = HistGradientBoostingRegressor()

    param_grid = {
      "max_depth": [1, 2, 4, 6],
      "learning_rate": np.linspace(0.01, 0.2, 5),
    }
    
    gridsearch = GridSearchCV(reg, param_grid=param_grid, verbose=10, return_train_score=True, n_jobs=8)

    gridsearch.fit(X_train, y_train)  
    
    print("Score: ", gridsearch.best_estimator_.score(X_test, y_test))
    
    return gridsearch.best_estimator_