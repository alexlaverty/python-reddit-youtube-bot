import pandas as pd
import os


class CsvWriter:
    def __init__(self, csv_file="data.csv"):
        self.csv_file = csv_file
        self.headers = ["id",
                        "title",
                        "thumbnail",
                        "duration",
                        "compiled",
                        "uploaded"]

    def initialise_csv(self):
        csv_exists = os.path.isfile(self.csv_file)
        if not csv_exists:
            new_csv = pd.DataFrame(columns=self.headers)
            new_csv.to_csv(self.csv_file, index=False)

    def write_entry(self, row):
        csv = pd.read_csv(self.csv_file)
        entry = [row]
        entry_df = pd.DataFrame(entry)
        csv_entry = pd.concat([csv, entry_df])
        csv_entry.to_csv(self.csv_file, index=False)

    def is_uploaded(self, id):
        csv = pd.read_csv(self.csv_file)
        return bool(
            len(
                csv.loc[(csv['id'] == id) & (csv['uploaded'] == True)]
                )
            )

    def set_uploaded(self, id):
        c = pd.read_csv(self.csv_file)
        for index, row in c.iterrows():
            if row['id'] == id:
                c.at[index, 'uploaded'] = "true"
        c.to_csv(self.csv_file, index=False)


if __name__ == "__main__":
    csvwriter = CsvWriter()
    csvwriter.initialise_csv()
    print(csvwriter.is_uploaded("snppah"))
    csvwriter.set_uploaded("snppah")
    print(csvwriter.is_uploaded("snppah"))
