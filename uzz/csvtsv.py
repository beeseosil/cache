
import sys

argument=sys.argv

csvfile=argument[1] if len(argument)>=2 else "/home/yuninze/res/phenotype/phenotype-quantified-processed.csv"
tsvfile=csvfile + ".tsv"

with open(csvfile,encoding="utf-8") as _csvfile, open(tsvfile,newline="\n",encoding="utf-8",mode="w") as _tsvfile:
	_tsvfile_data=[]
	for line in _csvfile:
		truncated_line=line.replace(",","\t").replace(" ","-")
		_tsvfile_data.append(truncated_line)
		
	for line in _tsvfile_data:
		if _tsvfile_data.index(line)==0:
			line="\t".join([f"{q}" for q in line.split("\t")])
		_tsvfile.write(line)
		print(line)
