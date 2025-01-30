import numpy as np
import dask.array as da
import zarr

from time import time

res_path="/home/yuninze/res/did/uiop.raw"
store_path=res_path+".zarr"

snp_known_length=37_637_567
iid_known_length=120

iid=[]
genotype=[]

t0=time()
with open(res_path,newline="\n") as snp_iid:
    snp=np.asarray(snp_iid.readline().split()[6:],dtype="U64")

    for l in snp_iid:
        line=l.split()
        iid.append(line[1].split("_")[0])

        genotype.append(
            list(map(lambda q:int(q)+1 if q.isnumeric() else 0,line[6:]))
        )

        iid_known_length-=1
        print(f"At: {iid[-1]}, {iid_known_length} Remaining {'  '*5}",end="\r")
print(f"Parsing Took {(time()-t0)/60:.1f} min {'  '*5}")

t0=time()
iid=da.from_array(np.asarray(iid,dtype="U32"))
gene=da.from_array(snp)
genotype=da.from_array(np.asarray(genotype,dtype="i1"))
print(f"Array Conversion Took {(time()-t0)/60:.1f} min {'  '*5}")

storage=zarr.DirectoryStore(store_path)
group=zarr.group(store=storage)

group.create_dataset("ind",data=iid.compute())
group.create_dataset("gene",data=gene.compute())
group.create_dataset("genotype",data=genotype.compute())
