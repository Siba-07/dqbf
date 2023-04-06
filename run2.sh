dir=./uniquetc
rm -r op
mkdir op
for entry in "$dir"/*
do
    out="$(basename $entry)"
    # echo "op/$out".txt
    #gtimeout 3m python3 main.py "$entry" --verb=3 > op/"$out".txt 

    gtimeout 3m python3 main.py "$entry"  
done