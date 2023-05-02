"""Manage the CSV file that contains metadata about Reddit posts."""
import os
from typing import Any, Dict

import pandas as pd
from pandas import DataFrame
from typing import List


class CsvWriter:
    """CSV Writer used to manage the bots database."""

    def __init__(self, csv_file="data.csv") -> None:
        """Initialize a new CSV Writer for managing the bots database.

        Args:
            csv_file: Path to the CSV file used to track video uploads.
        """
        self.csv_file = csv_file
        self.headers = ["id", "title", "thumbnail", "duration", "compiled", "uploaded"]

    def initialise_csv(self) -> None:
        """Initialise a fresh CSV file."""
        csv_exists = os.path.isfile(self.csv_file)
        if not csv_exists:
            new_csv: DataFrame = DataFrame(columns=self.headers)
            new_csv.to_csv(self.csv_file, index=False)

    def write_entry(self, row: Dict[str, Any]) -> None:
        """Save a new record to the CSV file.

        Args:
            row: New record containing metadata about a video.
        """
        csv: DataFrame = pd.read_csv(self.csv_file)
        entry: List[Dict[str, Any]] = [row]
        entry_df: DataFrame = DataFrame(entry)
        csv_entry: DataFrame = pd.concat([csv, entry_df])
        csv_entry.to_csv(self.csv_file, index=False)

    def is_uploaded(self, id: str) -> bool:
        """Validate whether a video has been uploaded.

        Args:
            id: Unique id of the video tbe validated.

        Returns:
            `True` if the video has already been uploaded, else `False`.
        """
        csv: DataFrame = pd.read_csv(self.csv_file)

        # TODO: ???
        results: int = len(csv.loc[(csv["id"] == id) & (csv["uploaded"] == True)])
        if results > 0:
            return True
        else:
            return False

    def set_uploaded(self, id: str) -> None:
        """Update the record to indicate the video has been uploaded.

        Args:
            id: Unique id of the record to be updated.
        """
        c: DataFrame = pd.read_csv(self.csv_file)
        for index, row in c.iterrows():
            if row["id"] == id:
                c.at[index, "uploaded"] = "true"
        c.to_csv(self.csv_file, index=False)


if __name__ == "__main__":
    csvwriter: CsvWriter = CsvWriter()
    csvwriter.initialise_csv()
    print(csvwriter.is_uploaded("snppah"))

    csvwriter.set_uploaded("snppah")
    print(csvwriter.is_uploaded("snppah"))
