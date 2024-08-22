import os 
def split_filename(filename):
    base_name=os.path.basename(filename)
    root,ext=os.path.splitext(base_name)
    if ext=='.gz' and root.endswith('.tar'):
        root,ext2=os.path.splitext(root)
        ext=ext2+ext
    return root,ext