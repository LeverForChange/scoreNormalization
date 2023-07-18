# We import necessary libraries

from torqueclient import Torque
import pandas as pd
from sklearn import preprocessing
from torqueclient import Torque
import numpy as np
import datetime
import config

torque = Torque(
    config.TORQUE_LINK,
    config.TORQUE_USERNAME,
    config.TORQUE_API_KEY
)

COMPETITION = config.COMPETITION

SCORE_TYPE = config.SCORE_TYPE
JUDGE_DATA_TYPES = config.JUDGE_DATA_TYPES

#We fetch all application data for the competition through Torque API
def get_proposal_judge_data():
    judge_data_by_proposal = {}
    for proposal in torque.competitions[COMPETITION].proposals:
        judge_data = {}

        for judge_data_type in JUDGE_DATA_TYPES:
            judge_data[judge_data_type] = []
            if proposal["%s %s Judge Data" % (SCORE_TYPE, judge_data_type)]:
                for torque_judge_datum in proposal["%s %s Judge Data" % (SCORE_TYPE, judge_data_type)]["Comments"]:
                    judge_data[judge_data_type].append({
                        "judgename": torque_judge_datum["Anonymous Judge Name"],
                        "rawscore": torque_judge_datum["Score"]["Raw"],
                    })

        judge_data_by_proposal[proposal.key] = {
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
def extract_scores(df):
    traits = ['COMMUNITY-INFORMED', 'IMPACTFUL', 'FEASIBLE', 'SUSTAINABLE']
    for trait in traits:
        df[trait + ' Rawscore'] = df['judgedata'].apply(lambda x: 0 if len(x[trait]) == 0 else sum([int(d['rawscore']) if d['rawscore'] != '' else 0 for d in x[trait]])/len(x[trait]))

        df[trait + ' Z-score Normalized Score'] = normalize_data(df, trait + ' Rawscore', 'zscore')
        df[trait + ' Min-Max Normalized Score'] = normalize_data(df, trait + ' Rawscore', 'min-max')

    # We calculate total rawscore and total normalized score for each row and add them as new columns
    # We compute the rank for the total scores and add them as new columns
    df['Total Rawscore'] = df[[trait + ' Rawscore' for trait in traits]].sum(axis=1)
    df['Rank by Total Rawscore'] = df['Total Rawscore'].rank(method='min', ascending=False)

    df['Total Z-Score Normalized Score'] = df[[trait + ' Z-score Normalized Score' for trait in traits]].sum(axis=1)
    df['Rank by Total Z-Score Normalized Score'] = df['Total Z-Score Normalized Score'].rank(method='min', ascending=False)

    df['Total Min-Max Normalized Score'] = df[[trait + ' Min-Max Normalized Score' for trait in traits]].sum(axis=1)
    df['Rank by Total Min-Max Normalized Score'] = df['Total Min-Max Normalized Score'].rank(method='min', ascending=False)

    return df

def main():
    # We read the csv file into a pandas DataFrame
    torque.bulk_fetch(torque.competitions[COMPETITION].proposals)
    df = get_proposal_judge_data()
    table = pd.DataFrame(df).transpose().reset_index()

    # We use the function we defined to extract and process the scores
    table = extract_scores(table)

    # We save the processed data back to a new csv file
    current_timestamp = datetime.datetime.now().strftime("%Y%m%d%H%M%S")
    output_file = f"{COMPETITION}_Normalized_{current_timestamp}.csv"
    table.to_csv(output_file, index=False)

    print("Normalization done, and the new file is saved!")

if __name__ == "__main__":
    main()
