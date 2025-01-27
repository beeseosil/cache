import os
import numpy as np
import pandas as pd
import streamlit as st

import util
import deta

from types import SimpleNamespace

repo_path="./res"
dog="dog"
grouper="cohort"

title="Analysis on Quantitized Data of Brain MR Images"

st.set_page_config(page_title=title,page_icon=None)
st.markdown(f"### {title}")

st.markdown('''
<style>
    .stTabs [data-baseweb="tab-list"] button [data-testid="stMarkdownContainer"] p {font-size:1.4rem;}
</style>
''',unsafe_allow_html=True)

transform_method={
    "None":"no transformation",
    "Log Transform":"log transformed",
    "Batch Correction":"pyCombat (covariate: gender, age)",
    "Divide by Intracranial Volume":"divided by intracranial volume",
}

noe,noeSite,noeCatName,noeVarName,noeVolName=deta.get_var()
noeImage=deta.get_noe_image(repo_path)

div_control_surface=st.container(border=True)

with div_control_surface:
    div_control_switch=st.container()
    
    with div_control_switch:
    
        msCenter=st.columns(1)[0]
        with msCenter:
            selectedUpper=st.multiselect(
                f"Cohort ({len(noeSite)})",
                noeSite,
                default=noeSite,
                max_selections=len(noeSite),
                help="Only variables existing on selected cohort(s) are shown, or included"
            )
    
    noe,noeSite,noeCatName,noeVarName,noeVolName=deta.get_var(noe.loc[noe.loc[:, grouper].map(lambda q:q in selectedUpper),:].dropna(axis=1))
    
    div_control_surface=st.container()
    with div_control_surface:
        transform_method_select=st.columns(1)[0]
        with transform_method_select:
            transform_method_selected=st.radio("Preprocess Method",(transform_method.keys()),horizontal=True)

        switchErabi,switchKesi=st.columns(2)
        with switchErabi:
            erabi=st.toggle("Show Prominent Regions Only",value=False,help="List regions frequently mentioned in reseraches (백질, 회백질, 뇌실, 전두엽 등)")
        with switchKesi:
            trim=st.toggle("Trim Outliers by [.001, .999]",value=False)
        
        how=transform_method[transform_method_selected]
        noe=deta.transform(noe,how,noeVarName,noeVolName)
        noe,noeSite,noeCatName,noeVarName,noeVolName=deta.get_var(noe)
        
        if erabi:
            noeVarName=[q for q in noeImage.keys() if q!="placeholder"]
            noeVolName=noeVarName
        if trim:
            noe=deta.trim(noe,noeVolName)
        
    div_feature_select_surface=st.container()
    with div_feature_select_surface:
        ddLeft,ddCenter,ddRight=st.columns(3)
        with ddLeft:
            noeCatName=noeCatName[:-1] if len(selectedUpper)==1 else noeCatName
            selectedLeft=st.selectbox(
                f"Group ({len(noeCatName)})",
                noeCatName,
                format_func=util.sanitise,
                key="l"
            )
        with ddCenter:
            selectedCenter=st.selectbox(
                f"X ({len(noeVarName)})",
                noeVarName,
                format_func=util.sanitise,
                key="c"
            )
        with ddRight:
            selectedRight=st.selectbox(
                f"Y ({len(noeVarName)})",
                noeVarName,
                index=3,
                format_func=util.sanitise,
                key="r"
            )
        
Selected=SimpleNamespace()

for select in zip(
    ("left","center","right"),
    (selectedLeft,selectedCenter,selectedRight)
):
    setattr(
        Selected,
        select[0],
        (select[1].lower(),f"{util.sanitise(select[1])}")
    )

page_description,page_volumetry,page_about=st.tabs(
    ["Overview","Per-region Values","About"]
)

with page_description:
    canvas=st.container(border=True)
    with canvas:
        vs=util.isVs(noe.loc[:,Selected.left[0]])
        for selected in (Selected.center,Selected.right):
            st.markdown(f"#### {selected[1]}")
            q,w,e,r=st.columns(4)
            for a in zip((q,w,e,r),("mean","median","std","count")):
                if a[1]!="count":
                    a[0].metric(a[1].title(),f"{noe[selected[0]].agg(a[1]):.2f}")
                else:
                    a[0].metric(a[1].title(),f"{noe[selected[0]].agg(a[1]):0}")
            
            noeImageEach=util.getNoeImage(noeImage,selected)
            
            boxplotLayoutProportion=[7.8, 3.2, .1] if erabi else 1
            
            boxplotImageDivider=st.columns(boxplotLayoutProportion)
            with boxplotImageDivider[0]:
                boxplotLeft=util.multiBox(
                    noe,
                    Selected.left,
                    selected,
                    vs=vs
                )
                
                boxplotTitle=boxplotLeft[0]
                if vs:
                    st.markdown(
                        f"##### Boxplot: {boxplotTitle[0]}<br><sub>{boxplotTitle[1]}, {boxplotTitle[2]}</sub>",
                        unsafe_allow_html=True
                    )
                
                else:
                    st.markdown(
                        f"##### Boxplot: {boxplotTitle}",
                        unsafe_allow_html=True
                    ) 
                
                st.plotly_chart(boxplotLeft[1])
            
            if erabi:
                with boxplotImageDivider[1]:
                    st.markdown("<br><br><br><br><br>",unsafe_allow_html=True)
                    st.image(noeImageEach)
            
            if vs==False:
                div_groupwise_table=st.container()
                with div_groupwise_table:
                    r=util.intergroupTt(
                        noe,
                        Selected.left,
                        selected,
                        star=True
                    )
                    
                    st.markdown(
                        f"##### Groupwise T-statistics: {r[0]}<br><sub>* p<0.05, ** <0.01, *** <0.001, or Not Significant</sub>",
                        unsafe_allow_html=True
                    )
                    
                    st.dataframe(
                        r[1].style.map(util.sign),
                        on_select="ignore",
                        use_container_width=True
                    )
            
            st.divider()
        
        graph_center=st.columns(1)[0]
        with graph_center:
            try:
                scatterCenter=util.scatterTrajectory(
                    noe=noe,
                    c=Selected.left,
                    x=Selected.center,
                    y=Selected.right,
                )
                scatterCenterTitle=scatterCenter[0]
            
            except Exception as err:
                st.exception(err)
            
            else:
                st.markdown(f"##### Scatter Plot with Trajectory<br><sub>{scatterCenterTitle}</sub>",unsafe_allow_html=True)
                st.plotly_chart(scatterCenter[1])

with page_volumetry:
    div_volumetry_plot=st.container(border=True)
    with div_volumetry_plot:
    
        util.claim(f"NoeVolName.size={len(noeVolName)}")
        
        decomposition_vol_name=[q for q in noeVolName if not q.startswith("icv")]
        
        decomposition_plot_title=f"##### Principal Component Analysis<br><sub>{len(decomposition_vol_name)} volume parameters, {how}</sub>"
        
        st.markdown(decomposition_plot_title,unsafe_allow_html=True)
        
        decomposed=util.lap(util.decompose,noe=noe,c=Selected.left,y=decomposition_vol_name)
        
        st.pyplot(
            decomposed[0],
            use_container_width=True,
            transparent=True
        )
        
        st.divider()
        
        violin_plot_title=f"##### Batch Effect<br><sub>{len(decomposition_vol_name)} volume parameters, {how}</sub>"
        
        st.markdown(violin_plot_title,unsafe_allow_html=True)
        
        st.pyplot(
            util.lap(
                util.draw_violin,
                deta=deta.transform(noe,"scale",noeVarName,decomposition_vol_name),
                value_column=decomposition_vol_name
            )[0],
            use_container_width=True,
            transparent=True
        )
        
        decomposer=decomposed[1]

with page_about:
    about=st.container(border=True)
    with about:
        st.markdown("#### Parameters")
    
        st.image(os.path.join(repo_path,dog))
        
        st.table(
            pd.DataFrame(data=decomposer.components_.T,index=decomposition_vol_name,columns=["PC1","PC2"])
        )
        
        st.json({q[0]:q[1] for q in zip(
            (
                "Site-Cohort",
                "Categorical",
                "Contiguous",
                "Volumetry",
                "Noe Images",
            ),
            (
                noeSite,
                noeCatName,
                noeVarName,
                noeVolName,
                noeImage,
            )
        )})

foot=st.container(border=False)
with foot:
    st.markdown("""
        **© 2025 <https://www.nih.go.kr>**
    """,unsafe_allow_html=True)
