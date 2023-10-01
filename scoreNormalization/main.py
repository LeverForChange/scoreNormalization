# We import necessary libraries

import pandas as pd
from sklearn import preprocessing
from torqueclient import Torque
import numpy as np
import datetime

#We fetch all application data for the competition through Torque API
def get_proposal_judge_data(proposals, score_type, judge_data_types):
    judge_data_by_proposal = {}
    for proposal in proposals:
        if (
            ("%s Score" % score_type) not in proposal.keys() or
            "Raw" not in proposal["%s Score" % score_type] or
            not proposal["%s Score" % score_type]["Raw"]
        ):
            continue

        judge_data = {}

        for judge_data_type in judge_data_types:
            judge_data[judge_data_type] = []
            if proposal["%s %s Judge Data" % (score_type, judge_data_type)]:
                for torque_judge_datum in proposal["%s %s Judge Data" % (score_type, judge_data_type)]["Comments"]:
                    judge_data[judge_data_type].append({
                        "judgename": torque_judge_datum["Anonymous Judge Name"],
                        "rawscore": torque_judge_datum["Score"]["Raw"],
                    })

        judge_data_by_proposal[proposal["Application #"]] = {
            "judgedata": judge_data,
            "Organization": proposal["Organization Name"],
        }

    return judge_data_by_proposal


# This function is used to normalize the data based on the selected method.
# It takes a dataframe, the column to be normalized, and the method of normalization.
def normalize_data(df, column, method='zscore'):
    if method == 'zscore':
        scaler = preprocessing.StandardScaler() # For z-score normalization
    elif method == 'min-max':
        scaler = preprocessing.MinMaxScaler() # For min-max normalization
    else:
        raise ValueError(f"Unknown normalization method: {method}")

    reshaped_data = df[column].values.reshape(-1, 1)
    scaled_data = scaler.fit_transform(reshaped_data)
    return scaled_data

# We define this function to extract and process the scores from the judgedata column.
def extract_scores(df, judge_data_types):
    for trait in judge_data_types:
        df[trait + ' Rawscore'] = df['judgedata'].apply(lambda x: 0 if len(x[trait]) == 0 else sum([int(d['rawscore']) if d['rawscore'] != '' else 0 for d in x[trait]])/len(x[trait]))

        df[trait + ' Z-score Normalized Score'] = normalize_data(df, trait + ' Rawscore', 'zscore')
        df[trait + ' Min-Max Normalized Score'] = normalize_data(df, trait + ' Rawscore', 'min-max')

    # We calculate total rawscore and total normalized score for each row and add them as new columns
    # We compute the rank for the total scores and add them as new columns
    df['Total Rawscore'] = df[[trait + ' Rawscore' for trait in judge_data_types]].sum(axis=1)
    df['Rank by Total Rawscore'] = df['Total Rawscore'].rank(method='min', ascending=False)

    df['Total Z-Score Normalized Score'] = df[[trait + ' Z-score Normalized Score' for trait in judge_data_types]].sum(axis=1)
    df['Rank by Total Z-Score Normalized Score'] = df['Total Z-Score Normalized Score'].rank(method='min', ascending=False)

    df['Total Min-Max Normalized Score'] = df[[trait + ' Min-Max Normalized Score' for trait in judge_data_types]].sum(axis=1)
    df['Rank by Total Min-Max Normalized Score'] = df['Total Min-Max Normalized Score'].rank(method='min', ascending=False)

    return df

def main(torque, competition, score_type, judge_data_types, output_to_csv=False):
    """This entry point is for acting on the server, rather than in memory.  So it
    fetches all the data from the server, requiring torque parameters."""

    # We read the csv file into a pandas DataFrame
    torque.bulk_fetch(torque.competitions[competition].proposals)
    df = get_proposal_judge_data(torque.competitions[competition].proposals, competition, score_type, judge_data_types)
    table = pd.DataFrame(df).transpose().reset_index()

    # We use the function we defined to extract and process the scores
    table = extract_scores(table, judge_data_types)

    if output_to_csv:
        # We save the processed data back to a new csv file
        current_timestamp = datetime.datetime.now().strftime("%Y%m%d%H%M%S")
        output_file = f"{competition}_Normalized_{current_timestamp}.csv"
        table.to_csv(output_file, index=False)
        print("Normalization done, and the results are saved in %s!" % output_file)
    else:
        for record in table.to_dict(orient='records'):
            current_rank = torque.competitions[competition].proposals[record["index"]]["%s Rank" % score_type]
            current_score = torque.competitions[competition].proposals[record["index"]]["%s Score" % score_type]
            current_score["LFC Min-Max Normalized"] = round(record["Total Min-Max Normalized Score"] * 25, 1)
            current_rank["LFC Min-Max Normalized"] = record["Rank by Total Min-Max Normalized Score"]
            current_score["LFC Z-Score Normalized"] = round(record["Total Z-Score Normalized Score"], 3)
            current_rank["LFC Z-Score Normalized"] = record["Rank by Total Z-Score Normalized Score"]
            torque.competitions[competition].proposals[record["index"]]["%s Rank" % score_type] = current_rank
            torque.competitions[competition].proposals[record["index"]]["%s Score" % score_type] = current_score
        print("Normalization done, and results are back on torque")

def main_memory(proposals, score_type, judge_data_types):
    """This entry point is for running in memory on a list of dictionaries (PROPOSALS),

    Then a dictionary is returned of the form:
    {
       APPLICATION #: {
           "Rank": {
               "LFC Min-Max Normalized" = ...,
               "LFC Z-Score Normalized" = ...,

           "Score": {
               "LFC Min-Max Normalized" = ...,
               "LFC Z-Score Normalized" = ...,
           }
       },
       ...
    }
    Those dictionaries are then updated with the scores (destructively)."""

    # We read the csv file into a pandas DataFrame
    df = get_proposal_judge_data(proposals, score_type, judge_data_types)
    table = pd.DataFrame(df).transpose().reset_index()

    # We use the function we defined to extract and process the scores
    table = extract_scores(table, judge_data_types)

    resp = {}
    for record in table.to_dict(orient='records'):
        resp[record["index"]] = {
            "%s Rank" % score_type: {
                "LFC Min-Max Normalized": record["Rank by Total Min-Max Normalized Score"],
                "LFC Z-Score Normalized": record["Rank by Total Z-Score Normalized Score"],
            },
            "%s Score" % score_type: {
                "LFC Min-Max Normalized": round(record["Total Min-Max Normalized Score"] * 25, 1),
                "LFC Z-Score Normalized": round(record["Total Z-Score Normalized Score"], 3)
            },
        }

    return resp
