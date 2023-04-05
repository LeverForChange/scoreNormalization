Choice of DB - Chose MIHA instead of BaWoP for this early version because Torque download of BaWoP doesn't have Peer Scores. Since the very point of Normalization is to account for both Peer and Panel Scores and then rationalize on its variance, I chose an alternative db which had Peer Scores - MIHA.

Another point of clarification was that in both, BaWoP and MIHA, I found a lot of rows where there were textual values that were about something else in columns like 'Peer Score' and 'Panel Score' instead of the score themselves. Such rows have been pushed and ranked down in the code. But I would love to know if there was a reason why those rows didn't have numeric scores. Still an early version that will be refined on your feedback. 


Python File - For simplicity of testing for everyone since LFC has stringent software download rules on its PCs, kept this version as only one file on Github - the main.py code. 


Database Download - For the db it refers to, do download the MIHA db with all columns on Torque and rename it "MIHA.csv". Keep it in the same folder as main.py