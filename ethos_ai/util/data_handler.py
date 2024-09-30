from datetime import datetime
import os


class DataHandler:

    ExportPath = "exports"

    @staticmethod
    def save_list_to_markdown(
        path: str,
        filename: str,
        data: list[dict[str, any]],
        useTimeStamps: bool = False,
    ):
        """
        Save data to a markdown file.
        :param path: The directory path where the file will be saved.
        :type path: str
        :param filename: The name of the file.
        :type filename: str
        :param data: The data to be saved in the file. It should be a dictionary where the keys represent the column names and the values represent the data rows.
        :type data: list[dict[str, str]]
        :param useTimeStamps: Optional. If True, a timestamp will be added to the filename. Default is False.
        :type useTimeStamps: bool
        :raises Exception: If there is an error saving the data to the markdown file.
        """
        try:
            # Make sure the directory exists
            os.makedirs(path, exist_ok=True)

            if useTimeStamps:
                # Generate a file path based on the current date and time
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                filepath = os.path.join(path, f"{filename}_{timestamp}.md")
            else:
                # Use the provided filename
                filepath = os.path.join(path, f"{filename}.md")

            # Get the current date and time
            current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

            # Write the data to the file
            with open(filepath, "w") as f:
                # Write title with filepath and current date and time
                title_line = f"# Exported Data\n\n**File Path:** `{filepath}`\n\n**Export Date & Time:** {current_time}\n\n"
                f.write(title_line)

                keys = []
                for row in data:
                    if keys != row.keys():
                        keys = row.keys()
                        # Generate markdown chart header
                        mdChartHeader1 = "| " + " | ".join(keys) + " |\n"
                        f.write(mdChartHeader1)
                        mdChartHeader2 = (
                            "| " + " | ".join(["---" for _ in keys]) + " |\n"
                        )
                        f.write(mdChartHeader2)

                    # Generate markdown chart rows
                    row = (
                        "| "
                        + " | ".join(
                            str(value).replace("\n", "<br>") for value in row.values()
                        )
                        + " |\n"
                    )
                    f.write(row)

                print(f"Data saved to {filepath}")
        except Exception as e:
            raise Exception(
                f"Error saving data {data} to markdown file (path: {path}) {filename} (use timestamps: {useTimeStamps}): {e}"
            )

    @staticmethod
    def save_dict_to_markdown(
        path: str,
        filename: str,
        data: dict[str, list[str]],
        useTimeStamps: bool = False,
    ):
        """
        Save data to a markdown file.
        :param path: The directory path where the file will be saved.
        :type path: str
        :param filename: The name of the file.
        :type filename: str
        :param data: The data to be saved in the file. It should be a dictionary where the keys represent the column names and the values represent the data rows.
        :type data: dict
        :param useTimeStamps: Optional. If True, a timestamp will be added to the filename. Default is False.
        :type useTimeStamps: bool
        :raises Exception: If there is an error saving the data to the markdown file.
        """
        try:
            # Make sure the directory exists
            os.makedirs(path, exist_ok=True)

            if useTimeStamps:
                # Generate a file path based on the current date and time
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                filepath = os.path.join(path, f"{filename}_{timestamp}.md")
            else:
                # Use the provided filename
                filepath = os.path.join(path, f"{filename}.md")

            # Get the current date and time
            current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

            # Write the data to the file
            with open(filepath, "w") as f:
                # Write title with filepath and current date and time
                title_line = f"# Exported Data\n\n**File Path:** `{filepath}`\n\n**Export Date & Time:** {current_time}\n\n"
                f.write(title_line)

                # Generate markdown chart header
                mdChartHeader1 = "| " + " |".join(data.keys()) + " |\n"
                f.write(mdChartHeader1)
                mdChartHeader2 = "| " + " |".join(["---" for _ in data.keys()]) + " |\n"
                f.write(mdChartHeader2)

                # Generate markdown chart rows
                for i in range(len(data[list(data.keys())[0]])):
                    row = (
                        "| "
                        + " |".join([str(data[key][i]) for key in data.keys()])
                        + " |\n"
                    )
                    f.write(row)

                print(f"Data saved to {filepath}")
        except Exception as e:
            raise Exception(
                f"Error saving data {data} to markdown file (path: {path}) {filename} (use timestamps: {useTimeStamps}): {e}"
            )
