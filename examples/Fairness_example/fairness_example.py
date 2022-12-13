import pandas as pd

# Read Dataset
df = pd.read_csv('../../datasets/bodyPerformance.csv').rename({'class': 'y_true'}, axis=1)
print('Dataset Shape {}'.format(df.shape))




df['age_range'] = df['age'].apply(lambda x: '20-29' if (x >= 20 and x < 30)
                                  else ('30-39' if (x >= 30 and x < 40)
                                        else ('40-49' if (x >= 40 and x < 50)
                                              else ('50-59' if (x >= 50 and x < 60)
                                                    else '60-inf'))))

# Set 'age_range' columns in first position
df = df[df.columns.tolist()[-1:] +  df.columns.tolist()[:-1]]


from sklearn.preprocessing import LabelEncoder

lb_gen = LabelEncoder()
lb_age_range = LabelEncoder()
lb_y = LabelEncoder()
df['gender'] = lb_gen.fit_transform(df['gender'])
df['age_range'] = lb_age_range.fit_transform(df['age_range'])
df['y_true'] = lb_y.fit_transform(df['y_true'])



from sklearn.model_selection import train_test_split
X = df[df.columns.drop('y_true')]
y = df['y_true']
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.3, random_state=123)


from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import accuracy_score, classification_report

# Random Forest
model = RandomForestClassifier(n_estimators=20, bootstrap=True, criterion='gini', max_depth=10, random_state=123)
model.fit(X_train, y_train)

# Evaluation Metrics
y_train_pred = model.predict(X_train)
y_test_pred = model.predict(X_test)
print('Train Accuracy: {}'.format(accuracy_score(y_true=y_train, y_pred=y_train_pred)))
print('Test Accuracy: {}'.format(accuracy_score(y_true=y_test, y_pred=y_test_pred)))
print('Test Metrics:\n{}'.format(classification_report(y_true=y_test, y_pred=y_test_pred)))



x_cols = df.columns.drop('y_true').tolist()
# Calculate predictions
df['y_predict'] = model.predict(df[x_cols])


df['age_range'] = lb_age_range.inverse_transform(df['age_range'])
df['gender'] = lb_gen.inverse_transform(df['gender'])
df['y_true'] = lb_y.inverse_transform(df['y_true'])
df['y_predict'] = lb_y.inverse_transform(df['y_predict'])




from xaiographs.fairness import Fairness

f = Fairness(destination_path='./xaiographs_web_files')

f.fit_fairness(df=df,
               sensitive_cols=['age_range', 'gender'],
               target_col='y_true',
               predict_col='y_predict')
