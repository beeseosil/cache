import os
import numpy as np
import pandas as pd
import streamlit as st

import util

from sklearn.preprocessing import OneHotEncoder,PowerTransformer,StandardScaler
from pycombat import Combat
from scipy.stats import zscore
from PIL.Image import open

ind=['C_ID','epid','session_id','R_ID','session','ck_dcode','AS_DATA_CLASS','AS_EDATE']
exotic=["cretn_tr1","cretn_tr2"]
grouper="cohort"

@st.cache_data
def read(deta_path="./res/")->pd.DataFrame:
    deta_path=[q.path for q in os.scandir(deta_path) if q.name.endswith(".f")]
    
    return pd.concat(
        [pd.read_feather(deta_path) for deta_path in deta_path],
        axis=0
    ).drop(ind,axis=1)

@st.cache_data
def get_col(deta)->tuple:
    deta_site=deta.loc[:, grouper].unique().tolist()
    deta_categorical_col=[*deta.select_dtypes(int).columns.to_list(), grouper]
    deta_contigous_col=deta.select_dtypes(float).columns.to_list()
    deta_vol_col=[q for q in deta_contigous_col if q[-1].isnumeric() and q not in exotic]
    
    return deta_site,deta_categorical_col,deta_contigous_col,deta_vol_col

@st.cache_data
def get_var(deta=None)->tuple:
    # reading discrete feathers induces forced type inferring
    
    if deta is None:
        deta=read()
    
    deta.index=range(deta.shape[0])
    
    deta_site,deta_categorical_col,deta_contigous_col,deta_vol_col=get_col(deta)
    
    return deta,deta_site,deta_categorical_col,deta_contigous_col,deta_vol_col

@st.cache_data
def transform(
    deta,
    how,
    deta_contigous_col,
    deta_vol_col
)->pd.DataFrame:

    if how=="log transformed":
        transformer=PowerTransformer()
        final=pd.concat([
            deta.loc[:, grouper],
            deta.select_dtypes("int"),
            pd.DataFrame(
                transformer.fit_transform(deta.loc[:,deta_contigous_col]),
                columns=deta_contigous_col
            )
        ],axis=1)
    
    elif how=="scale":
        transformer=StandardScaler()
        final=pd.concat([
            deta.loc[:, grouper],
            deta.select_dtypes("int"),
            pd.DataFrame(
                transformer.fit_transform(deta.loc[:,deta_vol_col]),
                columns=deta_vol_col
            )
        ],axis=1)
    
    elif how=="batch correction (covariate: gender, age)":
        coder=OneHotEncoder()
        transformer=PowerTransformer()
        stabiliser=Combat()
    
        Xo=deta
        
        X=deta.loc[:,deta_vol_col].to_numpy()
        
        Xv=np.asarray(deta_vol_col,dtype="U32")
        
        Xb=deta.loc[:, grouper].to_numpy(dtype="U16")
        
        Xc_sex=np.asarray(coder.fit_transform(Xo.gender.to_numpy().reshape(-1,1)).todense())[:,[0]]
        Xc_age=np.concatenate([
            transformer.fit_transform(Xo.loc[Xo.loc[:,grouper]=="BICWALZS", "age"].to_numpy().reshape(-1,1)),
            transformer.fit_transform(Xo.loc[Xo.loc[:,grouper]=="KoGES", "age"].to_numpy().reshape(-1,1))
        ],
            axis=0,
        )
        
        util.claim("Combat: Xc",coder.get_feature_names_out())
        Xc=np.concatenate([Xc_sex,Xc_age],axis=1,dtype="f4")
        
        Xt=transformer.fit_transform(X)
        Xts=stabiliser.fit_transform(Xt,Xb,None,Xc)
        
        final=pd.concat([
            deta.loc[:, grouper],
            deta.select_dtypes("int"),
            pd.DataFrame(data=Xts,columns=Xv)
        ],axis=1)
    
    elif how=="divided by intracranial volume":
        deta_vol_col_no_icv=[q for q in deta_vol_col if not q.__contains__("icv")]
        icv=[q for q in deta.columns if q.__contains__("icv")][0]
        
        final=pd.concat([
            deta.loc[:, grouper],
            deta.select_dtypes("int"),
            deta.loc[:,deta_vol_col].apply(
                lambda q:q.div(q.at[icv]),
                axis=1
            ).drop(icv,axis=1).set_axis(deta_vol_col_no_icv,axis=1)
        ],axis=1)
    
    else:
        final=deta
    
    return final

@st.cache_data
def get_noe_image(deta_path)->dict:
    return {q.name.replace(".png",""):open(q.path) for q in os.scandir(deta_path) if q.name.endswith(".png")}

@st.cache_data
def trim(
    deta,
    deta_vol_col,
    gizun=.001
)->pd.DataFrame:
    '''Took 569 ± 23.9 ms '''
    deta_vol_col=[q for q in deta.columns if q in deta_vol_col]
    
    _lim=lambda q:(q.quantile(gizun), q.quantile(1-gizun))
    lim:dict=deta[deta_vol_col].apply(_lim).to_dict("list")
    
    for col in lim.keys():
        _arr=deta.loc[:,col].to_numpy(dtype=np.float32)
        
        _arrLower=_arr<lim[col][0]
        _arrUpper=_arr>lim[col][1]
        
        _arr[_arrLower]=np.nan
        _arr[_arrUpper]=np.nan
        
        deta.loc[:,col]=_arr
    
    return deta
