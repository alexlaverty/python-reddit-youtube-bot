import pandas as pd
import os

class CsvWriter:
    def __init__(self, csv_file="data.csv"):
        self.csv_file = csv_file

    def initialise_csv(self):
        csv_exists = os.path.isfile(self.csv_file)
        if not csv_exists:
            new_csv = pd.DataFrame(columns=["timestamp", "title", "url", "posted"])
            new_csv.to_csv(self.csv_file, index=False)

    def write_entry(self, row):
        csv = pd.read_csv(self.csv_file)
        entry = [row]
        entry_df = pd.DataFrame(entry)
        csv_entry = pd.concat([csv, entry_df])
        csv_entry.to_csv(self.csv_file, index=False)

    def entry_exists(self, title):
        csv = pd.read_csv(self.csv_file)
        return title in set(csv['title'])


if __name__ == "__main__":
    csvwriter = CsvWriter()
    csvwriter.initialise_csv()
    if not csvwriter.entry_exists("My title 3"):
        row = {'timestamp': "mytimestamp", 'title': "My title 3", 'url': "myurl", 'posted': "False"}
        csvwriter.write_entry(row)
