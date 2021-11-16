import os

for root, directory, files in os.walk('./temperatura'):
    for file in files:
        filename = file.split('_')[1][:-4] + '.tif'
        os.rename(os.path.join(root,file),os.path.join(root,filename))
