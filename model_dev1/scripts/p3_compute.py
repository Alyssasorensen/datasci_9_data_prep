import pandas as pd
import pickle
import joblib

from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler
from sklearn.dummy import DummyClassifier
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import mean_squared_error, r2_score, classification_report, confusion_matrix
from xgboost import XGBClassifier, XGBRegressor
from sklearn.model_selection import train_test_split, GridSearchCV

# Importing the cleaned sample of 100 data
df = pd.read_csv('model_dev1/data/processed/warehouse_and_retail_sales_data.csv')


# Dropping rows with missing values
df.dropna(inplace=True)
len(df)

# Defining the features and the target variable ('retail_transfers')
X = df.drop('retail_transfers', axis=1)  # Features (all columns except 'retail_transfers') all numebrs
y = df['retail_transfers']               # Target variable (retail_transfers) all numbers


# Initializing the StandardScaler
scaler = StandardScaler()
scaler.fit(X)          # Fitting the scaler to the features
pickle.dump(scaler, open('model_dev1/models/scaler.sav', 'wb'))  # Saving the scaler for later use

# Fitting the scaler to the features and transform
X_scaled = scaler.transform(X)

# Splitting the scaled data into training, validation, and testing sets
X_train, X_temp, y_train, y_temp = train_test_split(X_scaled, y, test_size=0.3, random_state=42)
X_val, X_test, y_val, y_test = train_test_split(X_temp, y_temp, test_size=0.5, random_state=42)

# Checking the size of each set
(X_train.shape, X_val.shape, X_test.shape)

# Pkle the X_train for later use in explanation
pickle.dump(X_train, open('model_dev1/models/X_train.sav', 'wb'))
# Pkle X.columns for later use in explanation
pickle.dump(X.columns, open('model_dev1/models/X_columns.sav', 'wb'))





##### Create a baseline model using DummyClassifier
# Initialize the DummyClassifier
dummy = DummyClassifier(strategy='most_frequent')
# Train the model on the training set
dummy.fit(X_train, y_train)
dummy_acc = dummy.score(X_val, y_val)



##### Create a Logistic Regression model
# Initialize the Logistic Regression model
log_reg = LogisticRegression()
# Train the model on the training set
log_reg.fit(X_train, y_train)
# Predict on the validation set
y_val_pred = log_reg.predict(X_val)
# Evaluate the model
log_reg_acc = log_reg.score(X_val, y_val)
log_reg_mse = mean_squared_error(y_val, y_val_pred)
log_reg_r2 = r2_score(y_val, y_val_pred)
# Print confusion matrix
print(confusion_matrix(y_val, y_val_pred))
# Display the classification report
print(classification_report(y_val, y_val_pred))
# Print the results
print('Baseline accuracy:', dummy_acc)
print('Logistic Regression accuracy:', log_reg_acc)
print('Logistic Regression MSE:', log_reg_mse)
print('Logistic Regression R2:', log_reg_r2)




####### Now lets use a different model, XGBoost
# Initialize the XGBoost classifier
xgboost = XGBClassifier()
# Train the model on the training set
xgboost.fit(X_train, y_train)
# Predict on the validation set
y_val_pred = xgboost.predict(X_val)
# Evaluate the model
xgboost_acc = xgboost.score(X_val, y_val)
xgboost_mse = mean_squared_error(y_val, y_val_pred)
xgboost_r2 = r2_score(y_val, y_val_pred)
# Print confusion matrix
print(confusion_matrix(y_val, y_val_pred))
# Display the classification report
print(classification_report(y_val, y_val_pred))
# Print the results
print('Baseline accuracy:', dummy_acc)
print('Logistic Regression accuracy:', log_reg_acc)
print('Logistic Regression MSE:', log_reg_mse)
print('Logistic Regression R2:', log_reg_r2)
print('XGBoost accuracy:', xgboost_acc)
print('XGBoost MSE:', xgboost_mse)
print('XGBoost R2:', xgboost_r2)



### now lets perform hyperparameter tuning on XGBoost
# Define the grid of hyperparameters
param_grid = {
    # there are 3 hyperparameters we want to tune:
    # and each hyperparameter has a list of values we want to try that need to be the same length
    # across all hyperparameters
    'learning_rate': [0.1, 0.01, 0.001], # learning rate is the step size shrinkage used to prevent overfitting
    'n_estimators': [100, 200, 300], # number of trees
    'max_depth': [3, 4, 5], # maximum depth of each tree
}

# Initialize the XGBoost classifier
xgboost = XGBClassifier()
# Initialize GridSearch
grid_search = GridSearchCV(estimator=xgboost, param_grid=param_grid, cv=3, n_jobs=-1)
# Fit the estimator
grid_search.fit(X_train, y_train)
# Predict on the validation set
y_val_pred = grid_search.predict(X_val)
# Evaluate the model
grid_search_acc = grid_search.score(X_val, y_val)
grid_search_mse = mean_squared_error(y_val, y_val_pred)
grid_search_r2 = r2_score(y_val, y_val_pred)
# Print confusion matrix
print(confusion_matrix(y_val, y_val_pred))
# Display the classification report
print(classification_report(y_val, y_val_pred))
# Print the results
print('Baseline accuracy:', dummy_acc)
print('Logistic Regression accuracy:', log_reg_acc)
print('XGBoost Model 1 accuracy:', xgboost_acc)
print('XGBoost Model 2 accuracy:', grid_search_acc)



# Print the best parameters and the best score
print(grid_search.best_params_)
print(grid_search.best_score_)



### now lets use the best parameters to train a new model
# Initialize the XGBoost classifier
xgboost = XGBClassifier(learning_rate=0.1, max_depth=4, n_estimators=100)
# Train the model on the training set
xgboost.fit(X_train, y_train)
# Predict on the test set
y_test_pred = xgboost.predict(X_test)
# Evaluate the model
xgboost_acc = xgboost.score(X_test, y_test)


## save the model
pickle.dump(xgboost, open('model_dev1/models/xgboost.sav', 'wb'))