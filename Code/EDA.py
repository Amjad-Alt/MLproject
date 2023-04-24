# import packages
import pandas as pd
import numpy as np
import os

# plotting
import matplotlib.pyplot as plt
import seaborn as sns

# clustering
from collections import Counter
from sklearn.cluster import DBSCAN 


#============================== Joining datasets =================================

# Set the working directory to the directory containing the datasets
os.chdir("C:/Users/amjad/OneDrive/المستندات/GWU_Cources/Spring2023/Machine_Learning/MLproject/Code/data")

# Create an empty list to store the dataframes
df_list = []

# Loop through the files in the directory
for file in os.listdir():
    # Check if the file is a CSV file
    if file.endswith(".csv"):
        # Read the CSV file into a pandas dataframe
       df = pd.read_csv(file)
        # Append the dataframe to the list
       df_list.append(df)

# Concatenate the dataframes in the list
concatenated_df = pd.concat(df_list, axis=0)

# save it as one file
concatenated_df.to_csv("sounds.csv", index=False)

# ================== Join raw data of single user ============================

# Define the directory where the files are stored
data_dir = "C:/Users/amjad/OneDrive/المستندات/GWU_Cources/Spring2023/Machine_Learning/MLproject/Code/data/HAPT_Data_Set/RawData"
save_dir = "C:/Users/amjad/OneDrive/المستندات/GWU_Cources/Spring2023/Machine_Learning/MLproject/Code/data"
# Loop users
for user in range(1, 31):
    
    # Define the filenames for this user's accelerometer and gyroscope data
    acc_filenames = [f"{data_dir}/acc_exp02_user01.txt", f"{data_dir}/acc_exp02_user01.txt"]
    gyro_filenames = [f"{data_dir}/gyro_exp01_user01.txt", f"{data_dir}/gyro_exp02_user01.txt"]
    
    # Read in the accelerometer and gyroscope data for this user
    acc_data = pd.concat([pd.read_csv(f, header=None, sep=" ") for f in acc_filenames])
    gyro_data = pd.concat([pd.read_csv(f, header=None, sep=" ") for f in gyro_filenames])
    
    # Join the accelerometer and gyroscope data horizontally
    data_h = pd.concat([acc_data, gyro_data], axis=1)

    # Add column names
    data_h.columns = ['acc_x', 'acc_y', 'acc_z', 'gyro_x', 'gyro_y', 'gyro_z']
    
    # Save the joined data to a file for this user
    data_h.to_csv(f"{save_dir}/user01_data.csv", index=False)


# =============================== Simple EDA ====================================
# set seed
np.random.seed(42)

# load dataset and saperate X,y
sounds = pd.read_csv("data/sounds.csv")

# data shapes
print(f'whole dataset schema {sounds.shape}')

# check Na values
print(f'number of Na in the whole dataframe {sounds.isna().sum().sum()}')

# data head
print(sounds.head(3))

# check features types
print(f'{sounds.dtypes}')

# get the frequency of each activity to check for balanced data
activity_counts = sounds['Activity'].value_counts()

# plot the bar chart 
plt.figure(figsize=(10,5))
plt.bar(activity_counts.index, activity_counts.values)
plt.title('Activity Frequency')
plt.xlabel('Activity')
plt.ylabel('Frequency')
plt.show()

# make a copy of the main dataset 
sounds2 = sounds.copy()

# change y into numarical for the model
print(f'Activities before numarically label them {sounds2.iloc[:,-1].unique()}')
sounds2['Activity'] = sounds2['Activity'].replace({'STANDING': 1, 'SITTING': 2, 'LAYING': 3, 'WALKING': 4, 'WALKING_DOWNSTAIRS':5, 'WALKING_UPSTAIRS':6})
print(f'Activities values after labeling {sounds2.iloc[:,-1].unique()}')


#=============================== Plot sounds ===========================

data = pd.read_csv('data/user01_data.csv')

palette = sns.color_palette("husl", 6)

# Create figure and axes objects
fig, (ax1, ax2, ax3, ax4, ax5, ax6) = plt.subplots(6, 1, figsize=(10, 15))

# Plot 
ax1.plot(data.iloc[:,0], data.iloc[:,0], color=palette[0])
#ax1.set_title('')

ax2.plot(data.iloc[:,1].index, data.iloc[:,1], color=palette[1])
#ax2.set_title('')

# Plot anomalies
ax3.plot(data.iloc[:,2].index, data.iloc[:,2], color=palette[2])
#ax3.set_title('')

ax4.plot(data.iloc[:,3].index,data.iloc[:,3], color=palette[3])
#ax4.set_title('')

ax5.plot(data.iloc[:,4].index, data.iloc[:,4], color=palette[4])
#ax5.set_title('')

ax6.plot(data.iloc[:,5].index, data.iloc[:,5], color=palette[5])
#ax6.set_title('')

# Add figure title and legend
fig.suptitle('', fontsize=14, fontweight='bold')
plt.show()

#=============================== Detect outliers ==================================
# Fit DBSCAN to the data
clustering = DBSCAN(eps=5, min_samples=2).fit(sounds2)
labels = clustering.labels_


# Count the number of occurrences of each label
label_counts = dict(Counter(clustering.labels_))

# Print the number of clusters (excluding outliers -1)
num_clusters = len([k for k in label_counts if k != -1])
print(f"Number of clusters: {num_clusters}")
num_outliers = len([k for k in label_counts if k == -1])
print(f"Number of outliers: {num_outliers}")

# Get the unique labels and set colors for each cluster
unique_labels = set(labels)
core_samples_mask = np.zeros_like(labels, dtype=bool)
core_samples_mask[clustering.core_sample_indices_] = True
colors = [plt.cm.Spectral(each) for each in np.linspace(0, 1, len(unique_labels))]

# Plot the data for each cluster
for k, col in zip(unique_labels, colors):
    if k == -1:
        # Black used for noise.
        col = [0, 0, 0, 1]

    class_member_mask = labels == k

    # Get the data points for this cluster
    xy = sounds2[class_member_mask & core_samples_mask]

    # Calculate the size of the marker based on the number of points in the cluster
    size = 100 * np.sqrt(np.count_nonzero(class_member_mask))

    # Plot the data for this cluster
    plt.plot(
        xy[0:1].mean(),
        xy[1:2].mean(),
        "o",
        markerfacecolor=tuple(col),
        markeredgecolor="k",
        markersize=14,
        alpha=0.5,
    )
plt.xlim(-5, 35)
plt.ylim(-5, 35)
plt.title(f"Estimated number of clusters: {num_clusters}")
plt.show()

# extract outliers from the data 
outlier_indices = np.where(labels == -1)[0]
outliers = sounds2.iloc[outlier_indices]

# filter out the outliers from the dataset 
sounds3 = sounds2[labels != -1]