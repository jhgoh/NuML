#!/usr/bin/env python3

import pandas as pd
import numpy as np
#from sklearn.utils import shffle

import torch
from torch.utils.data import Dataset, DataLoader
from torch.autograd import Variable
from sklearn.model_selection import train_test_split ## <- split datasets

import matplotlib.pyplot as plt

#from tqdm import tqdm_notebook ## <- draws a progress bar
from tqdm import tqdm as tqdm_notebook

## Check environment to use GPU or not
device = 'cpu'
if torch.cuda.is_available():
    print("GPU Acceleration Available")
    torch.set_default_tensor_type('torch.cuda.FloatTensor')
    dtype = torch.cuda.FloatTensor
    torch.cuda.manual_seed_all(0)
    pin_memory = True
    device = 'cuda'
else:
    dtype = torch.FloatTensor
    pin_memory = False

## Load datasets - use pandas to load csv, shuffle, join columns
df1 = pd.read_csv("signal.csv")
df2 = pd.read_csv("background.csv")

df1['category'] = 1
df2['category'] = 0

df = df1.append(df2, ignore_index=True).sample(frac=1)
for col in ["entry", "event", "En1", "En2"]:
   df = df.drop(col,1)

## Split datasets by train(0.6), validation(0.3), test(0.1)
df_train, df_test = train_test_split(df, test_size=0.4)
df_valid, df_test = train_test_split(df_test, test_size=1./4)

## Define pytorch dataset
class NuDataset(Dataset):
    def __init__(self, df_in):
        self.nColumns = df_in.shape[1]
        x = df_in.values[:,0:-1].reshape(-1,self.nColumns-1)
        y = df_in.values[:,-1:].reshape((-1,1))
        
        self.data = torch.from_numpy(x)
        self.labels = torch.from_numpy(y)
        self.size = len(df_in)

    def __len__(self):
        return self.size
      
    def getNColumns(self):
        return self.nColumns

    def __getitem__(self, idx):
        return self.data[idx], self.labels[idx]

dset_train = NuDataset(df_train)
dset_valid = NuDataset(df_valid)
dset_test = NuDataset(df_test)

## Just to check what is stored inside
print (dset_train[0:5])
print (dset_train.getNColumns())

## And the data loader
train_loader = DataLoader(dataset=dset_train,
                          batch_size=1024, shuffle=False, num_workers=2)
valid_loader = DataLoader(dataset=dset_valid,
                          batch_size=1024, shuffle=False, num_workers=2)

## Define the model put the number of input variables in the constructor
class Model(torch.nn.Module):
    def __init__(self, input_size):
        super(Model, self).__init__()
        
        self.model = torch.nn.Sequential(
            torch.nn.Linear(input_size, 128, bias=True),
            torch.nn.ReLU(),
            torch.nn.Linear(128, 128, bias=True),
            torch.nn.ReLU(),
            torch.nn.Linear(128, 1, bias=True),
            torch.nn.Sigmoid()
        )
        
    def forward(self, x):
        return self.model(x)

## Make model instance
model = Model(dset_train.getNColumns()-1)

## Enable GPU acceleration if available
if device == 'cuda': model.cuda()
  
## Define the loss function. BCELoss works for the Binary Classification
crit = torch.nn.BCELoss()
if device == 'cuda': crit.cuda()

## Adam optimizer is the first one to try
optm = torch.optim.Adam(model.parameters(), lr=1E-3)
#optm = torch.optim.SGD(model.parameters(), lr=1E-2)

losses_train, losses_valid = [], []
bestModel = None
bestEpoch = -1

## Start training & evaluations
## tqdm_notebook(some_iterator) draws a nice progress bar in the notebook.
for epoch in tqdm_notebook(range(100)):
  model = model.train() ## Turn on training mode
  loss_train = [] ## we will take average of training loss in this epoch
  for i, (inputs, labels) in enumerate(train_loader, 0):
    inputs, labels = Variable(inputs), Variable(labels)
    inputs = inputs.float().to(device) # Send to the GPU
    labels = labels.float().to(device) # Send to the GPU
    optm.zero_grad()
    
    outputs = model(inputs)
    
    loss = crit(outputs.view(-1), labels.view(-1)) ## had to reshape results
    loss.backward()
    optm.step()
    
    loss_train.append(loss.data.item())
    
  ## Keep the running loss
  loss_train = sum(loss_train)/len(loss_train) if len(loss_train) > 0 else 0
  losses_train.append(loss_train)
  
  ## Turn on evaluation mode for the validation set
  model = model.eval()
  y_pred = model(dset_valid.data.float().to(device))
  loss = crit(y_pred, dset_valid.labels.float().to(device))
  losses_valid.append(loss.data.item())
  
  if bestEpoch < 0 or losses_valid[bestEpoch] > loss.data.item():
    bestModel = model.state_dict()
    bestEpoch = epoch

print (bestEpoch, losses_valid[bestEpoch])

plt.loglog()
plt.plot(losses_train, "r", label="training")
plt.plot(losses_valid, "b", label="validation")
plt.plot([bestEpoch], [losses_valid[bestEpoch]], 'g*', markersize=15,
          label=("epoch=%d loss=%.3f" % (bestEpoch, losses_valid[bestEpoch])))
plt.legend()
plt.show()
#plt.savefig("learning.png")

model.load_state_dict(bestModel)
model = model.eval()

from sklearn.metrics import roc_curve, accuracy_score, auc

y_pred = model(dset_test.data.float().to(device)).cpu().detach().numpy()
print ("Accuracy=", accuracy_score(dset_test.labels, np.where(y_pred>0.5,1,0)))
#print (dset_test.labels.numpy())
fpr, tpr, thr = roc_curve(dset_test.labels.numpy().reshape(-1,), y_pred.reshape(-1,))
roc_auc = auc(fpr, tpr)

plt.plot([0,1], [0,1], 'r--')
plt.plot(fpr, tpr, 'b', label='AUC=%03f' % roc_auc)
plt.legend()
plt.show()
#plt.savefig("roc.png")

