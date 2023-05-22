from torqueclient import Torque
import pandas as pd
import numpy as np
import datetime
import seaborn as sns
import matplotlib.pyplot as plt

torque = Torque(
    "link",
    "username",
    "apikey"
)

COMPETITION = "competition_name"

JUDGE_DATA_TYPES = [
    "COMMUNITY-INFORMED",
    "IMPACTFUL",
    "FEASIBLE",
    "SUSTAINABLE",
]

def get_proposal_judge_data():
    """Gets the raw judge scoring data for all proposals in a dictionary mapping the proposal key
    to the following dictionary:"""

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


def normalize_judge_data(judge_data_by_proposal):
    """Normalizes judge data using min-max normalization and z-score normalization."""

    for proposal_key, judge_data in judge_data_by_proposal.items():
        for judge_data_type, data in judge_data["judgedata"].items():
            raw_scores = np.array([datum['rawscore'] for datum in data])
            min_max_normalized_scores = (raw_scores - np.min(raw_scores)) / (np.max(raw_scores) - np.min(raw_scores))
            z_score_normalized_scores = (raw_scores - np.mean(raw_scores)) / np.std(raw_scores)
            for i, datum in enumerate(data):
                datum["Min-Max Normalized"] = min_max_normalized_scores[i]
                datum["Z-Score Normalized"] = z_score_normalized_scores[i]

def main():
    # Bulk fetch and locally cache all the proposals for this competition to make things speedier
    torque.bulk_fetch(torque.competitions[COMPETITION].proposals)

    proposal_judge_data = get_proposal_judge_data()

    normalize_judge_data(proposal_judge_data)

    # Create a DataFrame from the proposal_judge_data dictionary
    table = pd.DataFrame(proposal_judge_data).transpose().reset_index()
    table.rename(columns={"index": "Proposal Key"}, inplace=True)

    # Rename "rawscore" column to "Raw Trait Score"
    table = table.rename(columns={"rawscore": "Raw Trait Score"})

    # Check for missing data
    missing_data = table.isnull().sum()
    print(f"Missing data in each column:\n{missing_data}\n")

    # Fill missing trait scores with column median
    table["Raw Trait Score"].fillna(table["Raw Trait Score"].median(), inplace=True)

    # Checking and handling outliers (Replace with upper whisker if data point is greater)
    Q1 = table["Raw Trait Score"].quantile(0.25)
    Q3 = table["Raw Trait Score"].quantile(0.75)
    IQR = Q3 - Q1

    upper_whisker = Q3 + 1.5 * IQR
    table["Raw Trait Score"] = np.where(table["Raw Trait Score"] > upper_whisker, upper_whisker, table["Raw Trait Score"])

    # Plot score distributions for each judge
    #for judge in table["Anonymous Judge Name"].unique():
        #sns.displot(table[table["Anonymous Judge Name"]==judge]["Raw Trait Score"], kde=True)
        #plt.title(f"Distribution of scores for {judge}")
        #plt.show()

    # Before normalizing scores, calculate and print skewness and kurtosis for each judge
    for judge in table["Anonymous Judge Name"].unique():
        scores = table[table["Anonymous Judge Name"]==judge]["Raw Trait Score"]
        skewness = scores.skew()
        kurtosis = scores.kurt()
        print(f"Scores for {judge}: skewness = {skewness:.2f}, kurtosis = {kurtosis:.2f}")

    """Skewness gives an idea of the symmetry of the distribution around the mean. A skewness value close to 0 suggests that the data is fairly symmetric. Negative skewness indicates that the data is skewed to the left, while positive skewness indicates that the data is skewed to the right.
    Kurtosis measures the "tailedness" of the distribution. A high kurtosis value indicates a distribution with heavy tails, which means there are more outliers. A low kurtosis value indicates a distribution with light tails, meaning fewer outliers.
    These statistics can help give an idea of the distribution of scores for each judge"""

    # We normalize scores using min-max method for each judge
    min_max_normalized_scores = table.groupby("Anonymous Judge Name")["Raw Trait Score"].transform(lambda x: (x - x.min()) / (x.max() - x.min()))

    # We normalize scores using z-score method for each judge
    z_score_normalized_scores = table.groupby("Anonymous Judge Name")["Raw Trait Score"].transform(lambda x: (x - x.mean()) / x.std())

    # Add normalized scores to our Table
    table["Min-Max Normalized Score"] = min_max_normalized_scores
    table["Z-Score Normalized Score"] = z_score_normalized_scores

    # Reposition the "Raw Trait Score" column before Min-Max and Z-Score normalization columns
    table = table[['Application #', 'Organization', 'Judge Name', 'Anonymous Judge Name', 'Trait', 'Raw Trait Score', 'Min-Max Normalized Score', 'Z-Score Normalized Score', 'Overall Score Rank']]

    # We pivot our Table to get scores by trait
    pivoted_table = table.pivot_table(index=["Application #", "Organization"], columns="Trait", values=["Raw Trait Score", "Min-Max Normalized Score", "Z-Score Normalized Score"], aggfunc="mean")

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
    output_file = f"BaWoP_Normalized_{current_timestamp}.csv"

    # We save the output to a new CSV file
    table.to_csv(output_file, index=False)


if __name__ == "__main__":
    main()
