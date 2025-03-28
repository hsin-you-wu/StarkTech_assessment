import json
from genson import SchemaBuilder
import pandas as pd
import re

def print_schema(data):
    """ Prints the schema of a json/dict object. """
    builder = SchemaBuilder()
    builder.add_object(data)
    print(builder.to_json(indent=2))

def historicalPriceFull(data):
    """ Restructure "historicalPriceFull" into the same format as others. """
    # extract only the "historical" list
    historical_list = data["historicalPriceFull"]["historical"]
    
    # add symbol property to each data
    for d in historical_list:
        d["symbol"] = "1101.TW"

    # add historical list back to data
    data["historical"] = historical_list

    # remove "historicalPriceFull"
    del data["historicalPriceFull"]

    return data

def tech(data):
    """ Restructure "tech5", "tech20", "tech60" and "tech252". """

    tech_map = {"tech5": "5", "tech20": "20", "tech60": "60", "tech252": "252"}
    var_list = ["sma", "ema", "wma", "dema", "tema", "williams", "rsi", "adx", "standardDeviation"]

    for tech_name, tech_num in tech_map.items():
        if tech_name not in data:
            continue

        for entry in data[tech_name]:
            # extract date
            match = re.match(r"(\d{4}-\d{2}-\d{2})", entry["date"])
            entry["date"] = match.group(1) if match else entry["date"]

            # add symbol
            entry["symbol"] = "1101.TW"

            # rename keys
            for var in var_list:
                entry[f"{var}_{tech_num}"] = entry.pop(var)

    return data


def main():
    # read json
    file_path = "output_clean_date_technical.json"
    with open(file_path, 'r') as file:
        nested_data = json.load(file)
    
    # check data structure
    # print_schema(nested_data)

    # ensure all data are in the same format
    nested_data = historicalPriceFull(nested_data)
    nested_data = tech(nested_data)

    # flat nested data
    df_list = []
    for data in nested_data.values():
        if isinstance(data, list):
            df_list.append(pd.json_normalize(data))
    
    # concat dataframes
    df = pd.concat(df_list, ignore_index=True)

    # merge by "symbol" & "date"
    df = df.groupby(["date", "symbol"], as_index=False).first()

    # back fill quarterly data and delete quartely row
    quarterly_rows = df["period"].notna()
    df = df.sort_values(by="date")
    df.bfill(inplace=True)
    df = df[~quarterly_rows]

    # write to csv
    df.to_csv("cleaned_data.csv", index=False)
    print('Success!')


if __name__ == "__main__":
    main()