import os
from azure.storage.blob import BlockBlobService
import pandas as pd

ACCOUNT_NAME = ''
ACCOUNT_KEY = ''
CONTAINER_NAME = 'raw-data'
block_blob_service = BlockBlobService(account_name=ACCOUNT_NAME, account_key=ACCOUNT_KEY)

data_folder = 'out'
generator = block_blob_service.list_blobs(CONTAINER_NAME)

excel_path = os.path.join('..','excel','TAGS.xlsx')
tags_excel = pd.read_excel(excel_path)
#tags_excel.dropna(inplace=True)
tags_=tags_excel['Tags']
type(tags_[10]) 
tags = tags_excel['Tags'].values
tags = [f.split('.')[0] for f in tags]

print(tags)

for blob in generator:
    # Using `get_blob_to_bytes`
    file_name = blob.name.split('/')[1]
    if((file_name.split('.')[0] in tags)):
        print('Downloading: '+blob.name)
        file_name = file_name.replace(':','_')

        if(not(os.path.isfile(os.path.join(data_folder,file_name)))):
            block_blob_service.get_blob_to_path(CONTAINER_NAME, blob.name,os.path.join(data_folder,file_name))
        else:
            print('File '+blob.name+' already exist... skipping')
    else:
        print("Skiping "+blob.name)

