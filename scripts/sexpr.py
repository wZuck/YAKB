"""Top-level KiCad S-expression iterator that respects quoted strings."""
def children(text):
    depth=0;start=None;quoted=False;escape=False
    for i,c in enumerate(text):
        if quoted:
            if escape:escape=False
            elif c=='\\':escape=True
            elif c=='"':quoted=False
            continue
        if c=='"':quoted=True
        elif c=='(':
            depth+=1
            if depth==2:start=i
        elif c==')':
            if depth==2:yield start,i+1,text[start:i+1]
            depth-=1
