import pandas as pd
import numpy as np


# We read the input CSV file with only the specified columns. These columns can be changed based on our preferences. The reason to choose only these was understood based on how Analysts operate.
input_file = "MIHA.csv"
columns_to_read = ['Application #', 'Organization Name', 'Peer Score', 'Peer Rank', 'Panel Score', 'Panel Rank', 'Rank']
table = pd.read_csv(input_file, usecols=columns_to_read)



# We convert non-numeric and non-float values to 0. We do this since Torque database download has a lot of entries with textual values in Peer and Panel Scores' columns.
table['Peer Score'] = pd.to_numeric(table['Peer Score'], errors='coerce').fillna(0)
table['Panel Score'] = pd.to_numeric(table['Panel Score'], errors='coerce').fillna(0)



# We normalize Peer Score and Panel Score. We use Min-Max Normalization, which was found to be the most efficient Normalization technique previously during the MIHA exercise in October
table['Normalized Peer Score'] = (table['Peer Score'] - table['Peer Score'].min()) / (table['Peer Score'].max() - table['Peer Score'].min())
table['Normalized Panel Score'] = (table['Panel Score'] - table['Panel Score'].min()) / (table['Panel Score'].max() - table['Panel Score'].min())



# We calculate the normalized score as the average of normalized peer score and normalized panel score
table['Normalized Score'] = (table['Normalized Peer Score'] + table['Normalized Panel Score']) / 2



# We sort the above by normalized score in descending order
table = table.sort_values(by='Normalized Score', ascending=False)



# Here, we assign the normalized rank based on the above sorting
table['Normalized Rank'] = table['Normalized Score'].rank(ascending=False)


# We save the output to a new CSV file (Later we integrate this in Torque UI to make it clickable download)
output_file = "MIHA_Scores_Normalized.csv"
table.to_csv(output_file, index=False)