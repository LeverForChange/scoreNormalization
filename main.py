import pandas as pd
import numpy as np


#API for importing data from Toque, all commented for now as focus is on finalizing the logic

"""
from torqueclient import Torque

torque = Torque(
    "https://torque.leverforchange.org/GlobalView",
    "<USERNAME>",
    "<APIKEY>"
)

COMPETITION = "BaWoP22"

JUDGE_DATA_TYPES = [
    "COMMUNITY-INFORMED",
    "IMPACTFUL",
    "FEASIBLE",
    "SUSTAINABLE",
]

def get_proposal_judge_data():
    {
      "judgedata": {
         "<JUDGE_DATA_TYPE_1>": [
           {
             "judgename": <ANONYMOUS_JUDGE_NAME>,
             "rawscore": <RAW_SCORE>,
           },
           ...
         ],
         "<JUDGE_DATA_TYPE_2>": [...],
         ...
      ],
      "rawscore": <PROPOSAL_RAW_SCORE>
    }
    
    judge_data_by_proposal = {}
    for proposal in torque.competitions[COMPETITION].proposals:
        judge_data = {}

        for judge_data_type in JUDGE_DATA_TYPES:
            judge_data[judge_data_type] = []
            if proposal["Panel %s Judge Data" % judge_data_type]:
                for torque_judge_datum in proposal["Panel %s Judge Data" % judge_data_type]["Comments"]:
                    judge_data[judge_data_type].append({
                        "judgename": torque_judge_datum["Anonymous Judge Name"],
                        "rawscore": torque_judge_datum["Score"]["Raw"],
                    })

        judge_data_by_proposal[proposal.key] = {
            "judgedata": judge_data,
            "rawscore": proposal["Panel Score"]["Raw"],
        }

    return judge_data_by_proposal

def save_proposal_judge_data(judge_data_by_proposal):
    Saves the calculated judge data back out to torque.

    JUDGE_DATA coming in should be a dictionary mapping proposal keys
    to judge data of the form:
    {
      "judgedata": {
         "<JUDGE_DATA_TYPE_1>": [
           {
             "judgename": <ANONYMOUS_JUDGE_NAME>,
             "normalized_score_1": <NORMALIZED_SCORE_1>,
             "normalized_score_2": <NORMALIZED_SCORE_2>,
             ...
           },
           ...
         ],
         "<JUDGE_DATA_TYPE_2>": [...],
         ...
      }
      ],
      "normalized_score_1": <PROPOSAL_NORMALIZED_SCORE_1>,
      "normalized_score_2": <PROPOSAL_NORMALIZED_SCORE_2>,
      ...
    }

    Where the name "normalized_score_X" should be replaced with something
    more informative like "Lowest Dropped" or some such.
    
    for proposal_key, judge_data in judge_data_by_proposal.items():
        torque_proposal = torque.competitions[COMPETITION].proposals[proposal_key]

        proposal_scores = {
            "Lowest Dropped": 0,
            "Intelligent": 0,
            "Normalized": 0,
        }

        for judge_data_type in JUDGE_DATA_TYPES in judge_data:
            torque_judge_data = torque_proposal["Panel %s Judge Data" % judge_data_type]
            scores_by_data_type = {
                "Lowest Dropped": 0,
                "Intelligent": 0,
                "Normalized": 0,
            }
            for judge_datum in judge_data:
                scores_by_data_type["Lowest Dropped"] += judge_datum["Lowest Dropped"]
                scores_by_data_type["Intelligent"] += judge_datum["Intelligent"]
                scores_by_data_type["Normalized"] += judge_datum["Normalized"]
                for torque_judge_datum in torque_judge_data["Comments"]:
                    if torque_judge_datum["Anonymous Judge Name"] == judge_datum["judgename"]:
                        torque_judge_datum["Score"]["Lowest Dropped"] = judge_datum["Lowest Dropped"]
                        torque_judge_datum["Score"]["Intelligent"] = judge_datum["Intelligent"]
                        torque_judge_datum["Score"]["Normalized"] = judge_datum["Normalized"]

            torque_judge_data["Lowest Dropped"] = scores_by_data_type["Lowest Dropped"]
            torque_judge_data["Intelligent"] = scores_by_data_type["Intelligent"]
            torque_judge_data["Normalized"] = scores_by_data_type["Normalized"]

            # This call is the one that actually pushes the data to the server
            torque_proposal["Panel % Judge Data" % judge_data_type] = torque_judge_data

        torque_score = torque_proposal["Panel Score"]

        torque_score["Lowest Dropped"] = proposal_scores["Lowest Dropped"]
        torque_score["Intelligent"] = proposal_scores["Intelligent"]
        torque_score["Normalized"] = proposal_scores["Normalized"]

        # This call is the one that actually pushes the data to the server
        torque_proposal["Panel Score"] = torque_score

def main():
    # Bulk fetch and locally cache all the proposals for this competition to make things speedier
    torque.bulk_fetch(torque.competitions[COMPETITION].proposals)

    proposal_judge_data = get_proposal_judge_data()

    # This is where you populate the judge data
    normalize_judge_data(proposal_judge_data)

    # This is untested (for obvious reasons), but should work
    save_proposal_judget_data(proposal_judge_data)


if __name__ == "__main__":
    main()

"""



# We read the input CSV file with only the specified columns. These columns can be changed based on our preferences. The reason to choose only these was understood based on how Analysts operate.
input_file = "MIHA.csv"
columns_to_read = ['Application #', 'Organization Name', 'Peer Score', 'Peer Rank', 'Panel Score', 'Panel Rank', 'Rank']
table = pd.read_csv(input_file, usecols=columns_to_read)



# We convert non-numeric and non-float values to 0. We do this since Torque database download has a lot of entries with textual values in Peer and Panel Scores' columns.
table['Peer Score'] = pd.to_numeric(table['Peer Score'], errors='coerce').fillna(0)
table['Panel Score'] = pd.to_numeric(table['Panel Score'], errors='coerce').fillna(0)



# Remove extreme outliers for Peer and Panel scores
def remove_outliers(df, column):
    Q1 = df[column].quantile(0.25)
    Q3 = df[column].quantile(0.75)
    IQR = Q3 - Q1
    lower_bound = Q1 - 1.5 * IQR
    upper_bound = Q3 + 1.5 * IQR
    return df[(df[column] >= lower_bound) & (df[column] <= upper_bound)]


table = remove_outliers(table, 'Peer Score')
table = remove_outliers(table, 'Panel Score')




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