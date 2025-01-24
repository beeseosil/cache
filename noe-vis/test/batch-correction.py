import os
import numpy as np
import pandas as pd

import matplotlib.pyplot as plt
import seaborn as sns

from sklearn.preprocessing import PowerTransformer
from sklearn.preprocessing import OneHotEncoder
from pycombat import Combat

transformer=PowerTransformer()
coder=OneHotEncoder()
stabiliser=Combat()

long_column=["Site","Region","Value"]

root_path="o:/yuninze/code/nih.go.kr/noe-vis/res"
xa=pd.read_feather(os.path.join(root_path,"koges.f"))
xb=pd.read_feather(os.path.join(root_path,"bicwalzs.f"))
xo=pd.concat([xa,xb],axis=0).sort_values("site").reset_index(drop=True) 
# xo.index.is_monotonic_increasing

xs=xo.site.to_numpy(dtype="U8")
x=xo.loc[:,[q for q in xo.columns if q[-1].isnumeric()]].dropna(axis=1)
xn=np.asarray(x.columns.to_list(),dtype="U64")
x=x.to_numpy()

# x_1 -> bool
xc_sex=np.asarray(coder.fit_transform(xo.sex.to_numpy().reshape(-1,1)).todense())[:,[0]]
xc_age=np.concatenate([
		transformer.fit_transform(xo.loc[xo.site=="BICWALZS",["age"]].to_numpy().reshape(-1,1)),
		transformer.fit_transform(xo.loc[xo.site=="KoGES",   ["age"]].to_numpy().reshape(-1,1))
	],
	axis=0
)

xc=np.concatenate([xc_sex,xc_age],axis=1)

xt=transformer.fit_transform(x)

xts=stabiliser.fit_transform(Y=xt,b=xs,X=None,C=xc)

xt_df=pd.DataFrame(data=xt,columns=xn)
xts_df=pd.DataFrame(data=xts,columns=xn)

xts_df_annot=xts_df.assign(site=xs)
xts_df_annot_long=xts_df_annot.melt("site").set_axis(long_column,axis=1)

xt_df_annot=xt_df.assign(site=xs)
xt_df_annot_long=xt_df_annot.melt("site").set_axis(long_column,axis=1)

beautifier=lambda q:q[:q.rfind("_")].replace("_"," ").title()

fg,ax=plt.subplots(2,1,figsize=(4,9))

sns.boxplot(xt_df_annot_long,x="Region",y="Value",hue="Site",whis=(1,99),fliersize=.2,formatter=beautifier,ax=ax[0])
sns.boxplot(xts_df_annot_long,x="Region",y="Value",hue="Site",whis=(1,99),fliersize=.2,formatter=beautifier,ax=ax[1])

fg.subplots_adjust(wspace=.01,hspace=.01)

plt.show(block=0)
