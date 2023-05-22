import pandas as pd
import numpy as np
import datetime

#API for importing data from Torque, all commented for now as focus is on finalizing the logic

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


input_file = "MIHA_panel.csv"
columns_to_read = ['Application #', 'Organization', 'Judge Name', 'Anonymous Judge Name', 'Trait', 'Trait Score', 'Overall Score Rank']
table = pd.read_csv(input_file, usecols=columns_to_read)

# We normalize scores using min-max method for each judge
min_max_normalized_scores = table.groupby("Anonymous Judge Name")["Trait Score"].transform(lambda x: (x - x.min()) / (x.max() - x.min()))

# We normalize scores using z-score method for each judge
z_score_normalized_scores = table.groupby("Anonymous Judge Name")["Trait Score"].transform(lambda x: (x - x.mean()) / x.std())

# Add normalized scores to our Table
table["Min-Max Normalized Score"] = min_max_normalized_scores
table["Z-Score Normalized Score"] = z_score_normalized_scores

# We pivot our Table to get scores by trait
pivoted_table = table.pivot_table(index=["Application #", "Organization"], columns="Trait", values=["Trait Score", "Min-Max Normalized Score", "Z-Score Normalized Score"], aggfunc="mean")

# Calculate the overall sum of normalized scores per normalization style
pivoted_table["Min-Max Overall Score"] = pivoted_table["Min-Max Normalized Score"].sum(axis=1)
pivoted_table["Z-Score Overall Score"] = pivoted_table["Z-Score Normalized Score"].sum(axis=1)

# We rank applications by the overall score
pivoted_table["Min-Max Rank"] = pivoted_table["Min-Max Overall Score"].rank(ascending=False)
pivoted_table["Z-Score Rank"] = pivoted_table["Z-Score Overall Score"].rank(ascending=False)

# We reset the index and print the output table
output_table = pivoted_table.reset_index()
print(output_table)

# We get the current timestamp and append it to the output file name
current_timestamp = datetime.datetime.now().strftime("%Y%m%d%H%M%S")
output_file = f"MIHA_Normalized_{current_timestamp}.csv"

# We save the output to a new CSV file (Later we integrate this in Torque UI to make it clickable download)
output_table.to_csv(output_file, index=False)