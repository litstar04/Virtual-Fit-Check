import pandas as pd
import numpy as np
from sklearn.impute import SimpleImputer
import numpy as np
import pandas as pd
from sklearn.preprocessing import StandardScaler
from sklearn.metrics.pairwise import euclidean_distances
import os
clothing_num_data=pd.read_csv('img_details.csv')
metrics=clothing_num_data.drop(["image_name"], axis=1)
clothes=clothing_num_data.drop(list(metrics.columns),axis=1)
from sklearn.impute import SimpleImputer
imputer1 = SimpleImputer(strategy="median")
# imputer2 = SimpleImputer(strategy="median")
imputer1.fit(metrics)
# imputer2.fit(clothes)
X=imputer1.transform(metrics)
# clothes = imputer2.transform(clothes)
metrics_f=pd.DataFrame(
    X,
    columns=metrics.columns,
    index=metrics.index
)
from sklearn.base import BaseEstimator, TransformerMixin

# column index
leg_length,torso_length,shoulder_width,hip_width = 0,1,2, 3

class CombinedAttributesAdder(BaseEstimator, TransformerMixin):
    def __init__(self, val=True): # no *args or **kargs
        self.val = val
    def fit(self, X, y=None):
        return self  # nothing else to do
    def transform(self, X):
        # Height(cm)	Waist	Chest	Gender	Complexion
        # HWC=X[:, Height]  + X[:, Waist] + X[:, Chest]
        leg_torso= X[:,leg_length] / X[:,torso_length]
        leg_shoulder=X[:,leg_length] / X[:,shoulder_width]
        leg_hip=X[:,leg_length] / X[:,hip_width]
        torso_shoulder=X[:,torso_length] / X[:,shoulder_width]
        torso_hip=X[:,torso_length] / X[:,hip_width]
        shoulder_hip=X[:,shoulder_width] / X[:,hip_width]
        # rooms_per_household = X[:, rooms_ix] / X[:, households_ix]
        # population_per_household = X[:, population_ix] / X[:, households_ix]
        new_features = np.c_[
            leg_torso,
            leg_shoulder,
            leg_hip,
            torso_shoulder,
            torso_hip,
            shoulder_hip
        ]
        return np.c_[new_features] if self.val else X


        # if self.val:
        #     return np.c_[X, leg_torso]
        # else:
        #     return self

attr_adder = CombinedAttributesAdder()
metrics_extra_attribs = attr_adder.transform(metrics_f.values)
metrics_real_attribs = pd.DataFrame(
    metrics_extra_attribs,
    columns=["leg_torso","leg_shoulder","leg_hip","torso_shoulder","torso_hip","shoulder_hip"])
def final_func(path):
  #imports dataset
  clothing_num_data=pd.read_csv(path)
  # clothing_num_data.insert(0, 'ID', range(1, len(clothing_num_data) + 1))
  metrics=clothing_num_data.drop(["image_name"], axis=1)
  clothes=clothing_num_data.drop(list(metrics.columns),axis=1)
  # print(metrics)
  # print(clothes)



  #Simple Imputer for median calculations
  imputer1 = SimpleImputer(strategy="median")
  imputer1.fit(metrics)
  X=imputer1.transform(metrics)
  metrics_f=pd.DataFrame(
      X,
      columns=metrics.columns,
      index=metrics.index
  )
  # print(metrics_f,'\n')



  # ratio calculated
  attr_adder = CombinedAttributesAdder()
  metrics_extra_attribs = attr_adder.transform(metrics_f.values)
  metrics_real_attribs = pd.DataFrame(
      metrics_extra_attribs,
      columns=["leg_torso","leg_shoulder","leg_hip","torso_shoulder","torso_hip","shoulder_hip"])
  # metrics_extra_attribs.head()
  # print(metrics_real_attribs,'\n')


  scaler = StandardScaler()
  final_metrics = scaler.fit_transform(metrics_real_attribs)
  # print("final_metrics",final_metrics)
  dataset_f = pd.DataFrame(
    final_metrics,
    columns=["leg_torso","leg_shoulder","leg_hip","torso_shoulder","torso_hip","shoulder_hip"])
  # print(dataset_f)
  return dataset_f,clothes,scaler
dataset_f,clothes,scaler=final_func('img_details.csv')
final_dataset=dataset_f
print(clothes.iloc[78].values)
final_dataset.drop('group_no.',axis=1)
import pandas as pd
import matplotlib.pyplot as plt

from sklearn.preprocessing import StandardScaler
from sklearn.cluster import KMeans
kmeans = KMeans(n_clusters=4)
kmeans.fit(final_dataset)
final_dataset['group_no.']=kmeans.labels_