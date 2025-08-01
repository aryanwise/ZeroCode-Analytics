import pandas as pd
import matplotlib.pyplot as plt

# Step 1: Load dataset
data_path = input("Enter the path to your dataset (CSV file): ")
try:
    df = pd.read_csv(data_path)
    print("✅ Dataset loaded successfully.")
except Exception as e:
    print("❌ Error loading dataset:", e)
    exit()

# Main CLI Loop
while True:
    print("\n📊 Pandas Dataset Analysis CLI")
    print("[1] General Dataset Info")
    print("[2] Data Selection & Filtering")
    print("[3] Data Cleaning")
    print("[4] Sorting Data")
    print("[5] Grouping and Aggregation")
    print("[6] Handling Missing Data")
    print("[7] Creating New Columns")
    print("[8] Merging / Joining Datasets")
    print("[9] Data Visualization")
    print("[10] Exporting Data")
    print("[11] Exit")

    choice = input("Select an option (1-11): ")

    # Step 1
    if choice == "1":
        print(
            "\n[1] Head\n[2] Tail\n[3] Full\n[4] Shape\n[5] Columns\n[6] Dtypes\n[7] Null Count\n[8] Summary"
        )
        sub = input("Choose (1–8): ")
        if sub == "1":
            print(df.head())
        elif sub == "2":
            print(df.tail())
        elif sub == "3":
            print(df)
        elif sub == "4":
            print(df.shape)
        elif sub == "5":
            print(df.columns.tolist())
        elif sub == "6":
            print(df.dtypes)
        elif sub == "7":
            print(df.isnull().sum())
        elif sub == "8":
            print(df.describe())

    # Step 2
    elif choice == "2":
        print(
            "\n[1] One Column\n[2] Multiple Columns\n[3] Condition\n[4] Two Conditions\n[5] iloc/loc"
        )
        sub = input("Choose (1–5): ")
        if sub == "1":
            col = input("Column: ")
            print(df[col]) if col in df else print("Invalid column.")
        elif sub == "2":
            cols = input("Columns (comma-separated): ").split(",")
            (
                print(df[cols])
                if all(c in df for c in cols)
                else print("Invalid column(s).")
            )
        elif sub == "3":
            cond = input("Condition (e.g. Age > 30): ")
            try:
                print(df.query(cond))
            except:
                print("❌ Invalid query.")
        elif sub == "4":
            cond1 = input("First condition: ")
            cond2 = input("Second condition: ")
            try:
                print(df.query(f"{cond1} and {cond2}"))
            except:
                print("❌ Invalid query.")
        elif sub == "5":
            mode = input("iloc or loc: ").lower()
            start = int(input("Start index: "))
            end = int(input("End index: "))
            print(df.iloc[start:end]) if mode == "iloc" else print(df.loc[start:end])

    # Step 3
    elif choice == "3":
        print(
            "\n[1] Drop Column\n[2] Drop Row\n[3] Rename Column\n[4] Drop Duplicates\n[5] Convert Dtype"
        )
        sub = input("Choose (1–5): ")
        if sub == "1":
            col = input("Column to drop: ")
            df.drop(columns=col, inplace=True, errors="ignore")
        elif sub == "2":
            idx = int(input("Row index: "))
            df.drop(index=idx, inplace=True, errors="ignore")
        elif sub == "3":
            old = input("Old name: ")
            new = input("New name: ")
            df.rename(columns={old: new}, inplace=True)
        elif sub == "4":
            df.drop_duplicates(inplace=True)
        elif sub == "5":
            col = input("Column: ")
            dtype = input("New dtype (int, float, str): ")
            try:
                df[col] = df[col].astype(dtype)
            except:
                print("❌ Conversion failed.")

    # Step 4
    elif choice == "4":
        col = input("Column to sort by: ")
        asc = input("Ascending (y/n): ").lower() == "y"
        df.sort_values(by=col, ascending=asc, inplace=True)
        print(df)

    # Step 5
    elif choice == "5":
        group_col = input("Group by column: ")
        agg_col = input("Aggregate column: ")
        func = input("Function (mean, sum, count, min, max): ")
        try:
            grouped = df.groupby(group_col)[agg_col].agg(func)
            print(grouped)
        except Exception as e:
            print("❌ Error:", e)

    # Step 6
    elif choice == "6":
        print("\n[1] Fill with Value\n[2] Fill with Mean\n[3] Drop Null Rows")
        sub = input("Choose (1–3): ")
        if sub == "1":
            col = input("Column: ")
            val = input("Value: ")
            df[col].fillna(val, inplace=True)
        elif sub == "2":
            col = input("Column: ")
            df[col].fillna(df[col].mean(), inplace=True)
        elif sub == "3":
            df.dropna(inplace=True)

    # Step 7
    elif choice == "7":
        print("\n[1] Add col1 + col2\n[2] Apply formula")
        sub = input("Choose (1–2): ")
        if sub == "1":
            c1 = input("Column 1: ")
            c2 = input("Column 2: ")
            new = input("New column: ")
            df[new] = df[c1] + df[c2]
        elif sub == "2":
            code = input("Lambda logic (e.g. lambda x: x['col1'] * 2): ")
            new = input("New column: ")
            try:
                df[new] = df.apply(eval(code), axis=1)
            except:
                print("❌ Error applying function.")

    # Step 8
    elif choice == "8":
        path2 = input("Second CSV path: ")
        try:
            df2 = pd.read_csv(path2)
            key = input("Join key: ")
            how = input("Join method (inner, left, right, outer): ")
            df = df.merge(df2, on=key, how=how)
            print("✅ Merge complete.")
        except Exception as e:
            print("❌ Merge failed:", e)

    # Step 9
    elif choice == "9":
        print("\n[1] Bar Plot\n[2] Histogram\n[3] Line Plot")
        sub = input("Choose (1–3): ")
        col = input("Column to plot: ")
        if sub == "1":
            df[col].value_counts().plot(kind="bar")
        elif sub == "2":
            df[col].plot(kind="hist")
        elif sub == "3":
            df[col].plot(kind="line")
        plt.title(f"{col} Plot")
        plt.show()

    # Step 10
    elif choice == "10":
        save_path = input("Save filename (e.g. output.csv): ")
        df.to_csv(save_path, index=False)
        print("✅ File exported.")

    # Exit
    elif choice == "11":
        print("👋 Exiting tool.")
        break

    else:
        print("⚠️ Invalid input. Try again.")
