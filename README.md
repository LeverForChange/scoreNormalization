- Python File: For simplicity of testing for everyone, kept this version as only one file - the main.py code. Plan to make it more object-oriented later once components get added.

- API pull from Torque and Database Download: For the db it refers to, eventually it will pull through the Torque API. For the sake of testing the logic first, the current version of the code relies on a MIHA database to be kept in the same folder as main.py. So to test, do download MIHA database with all columns from Torque and rename it "MIHA.csv". 

- Choice of DB: Chose MIHA database. In the db, we find a lot of rows where there were textual values that were about something else in columns like 'Peer Score' and 'Panel Score' instead of the score themselves. Such rows have been pushed and ranked down in the code. (Would love to know if there was a reason why those rows didn't have numeric scores.) 

- Removing Outliers from database: we've removed extreme outliers from the Peer and Panel scores by using the interquartile range (IQR) method. Through this, we first calculate the 1st and 3rd quartiles and then the IQR (the difference between the two). Then, we remove any rows with Peer or Panel scores outside the range (Q1 - 1.5IQR) to (Q3 + 1.5IQR)

PS: Still an early version that will be refined on your feedback. 
