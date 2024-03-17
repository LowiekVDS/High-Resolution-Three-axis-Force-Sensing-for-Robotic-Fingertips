import numpy as np
import os
import dill
from sklearn.linear_model import LinearRegression, Ridge
from sklearn.metrics import mean_squared_error
from sklearn.model_selection import train_test_split
from sklearn.compose import ColumnTransformer, make_column_transformer
from sklearn.pipeline import make_pipeline, make_union
from sklearn.preprocessing import PolynomialFeatures
from sklearn import set_config
from sklearn.multioutput import MultiOutputRegressor, RegressorChain
from sklearn.compose import TransformedTargetRegressor

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

COUPLE_COMPONENTS = True
POLY_DEGREE = 16

def create_regression_pipeline_and_fit(X, Y, debug = True, preserve_time=False, alpha=1.0):
  
  if preserve_time:
    split = int(len(X) * 0.99)
    X_train = X[:split]
    X_test = X[split:]
    y_train = Y[:split]
    y_test = Y[split:]
  else:
    X_train, X_test, y_train, y_test = train_test_split(X, Y, test_size=0.2, shuffle=True)

  pipeline = make_pipeline(
    PolynomialFeatures(degree=POLY_DEGREE, include_bias=False), 
    # LinearRegression()
    Ridge(alpha=alpha)
  )
  
  pipeline.fit(X_train, y_train)

  if debug:
    
    print("Score: ", pipeline.score(X_test, y_test))
    print("MSE: ", mean_squared_error(y_test, pipeline.predict(X_test)))
  
  return pipeline

class CombinedModel:
  
  def __init__(self, component_models) -> None:
    self.component_models = component_models
    
  def predict(self, X):
    
    predictions = []
    
    for i, model in enumerate(self.component_models):
        
      print(model[:-1].get_feature_names_out())
        
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
      "max_depth": [1, 2, 4, 6, 8, 10],
      "learning_rate": np.linspace(0.01, 0.2, 5),
    }
    
    gridsearch = GridSearchCV(reg, param_grid=param_grid, verbose=1, return_train_score=True, n_jobs=8)

    gridsearch.fit(X_train, y_train)  
    
    print("Score: ", gridsearch.best_estimator_.score(X_test, y_test))
    
    return gridsearch.best_estimator_