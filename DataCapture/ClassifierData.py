import os
import random
import gdown
import shutil

def getGestureData():
    url = "https://drive.google.com/file/d/1LO09E76gO0XLZo1u_siOlfkxZ-gcqmTj/view?usp=sharing"
    output = "test.zip"
    gdown.download(url, output, quiet=False, fuzzy=True)
    shutil.unpack_archive('test.zip', '.')
    os.remove('test.zip')

def getDataSubset():
    if not os.path.isdir('AllCroppedData'):
        print('Please download dataset and move class folders into <AllCroppedData>:\n'
              'All cropped <link to all cropped data>\n')
        return False
    Classes = os.listdir('AllCroppedData')
    
    def make(path):
        try:
            os.mkdir(path)
        except:
            pass
    make('Data')
    for Class in Classes:
        make('Data/'+Class)
        files = os.listdir('AllCroppedData/'+Class)
        random.shuffle(files)
        for i in range(min(len(files), 450)):
            os.rename('AllCroppedData/'+Class+'/'+files[i],
                      'Data/'+Class+'/'+files[i])
    return True

if __name__=="__main__":
    getGestureData()
