import getopt
import sys
import config
from torqueclient import Torque
from scoreNormalization.main import main

__doc__ = """
Normalize competition scores and upload

Usage:

  $ python main.py [--csv]

Command-line options:
  --csv                     Output to CSV rather than uploading results back to torque

"""

torque = Torque(
    config.TORQUE_LINK,
    config.TORQUE_USERNAME,
    config.TORQUE_API_KEY
)

competition = config.COMPETITION
score_type = config.SCORE_TYPE
judge_data_types = config.JUDGE_DATA_TYPES

try:
    opts, args = getopt.getopt(
        sys.argv[1:],
        "",
        [
            "csv",
        ],
    )
except getopt.GetoptError as err:
    sys.stderr.write("ERROR: '%s'\n" % err)
    sys.exit(2)

output_to_csv = False
for o, a in opts:
    if o == "--csv":
        output_to_csv = True
    else:
        sys.stderr.write("ERROR: unrecognized option '%s'\n" % o)
        sys.stderr.write(__doc__)
        sys.exit(2)

main(torque, competition, score_type, judge_data_types, output_to_csv)
