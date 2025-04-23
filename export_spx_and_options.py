import datetime
import pandas as pd
import time
import psycopg2
from fetchData import fetchDataIndex, fetchDataOptions

def get_atm_strike(spx_open, step=50):
    return round(spx_open / step) * step

def fetch_day_data(trading_day, expiry_day, strike=None):
    max_retries = 3
    retry_delay = 5

    # Fetch SPX
    for attempt in range(max_retries):
        try:
            spx_df = fetchDataIndex("SPX", trading_day, trading_day).reset_index()
            break
        except Exception as e:
            print(f"[SPX ERROR on {trading_day}] {e}")
            if attempt < max_retries - 1:
                time.sleep(retry_delay)
            else:
                return None

    # Determine ATM strike if needed
    if strike is None:
        strike = get_atm_strike(spx_df.loc[0, "Open"])

    # Fetch CE and PE
    for attempt in range(max_retries):
        try:
            ce_df = fetchDataOptions("SPXW", trading_day, trading_day, strike, expiry_day, "CE").reset_index()
            pe_df = fetchDataOptions("SPXW", trading_day, trading_day, strike, expiry_day, "PE").reset_index()
            break
        except Exception as e:
            print(f"[OPTION ERROR on {trading_day}] {e}")
            if attempt < max_retries - 1:
                time.sleep(retry_delay)
            else:
                return None

    # Rename columns for clarity
    spx_df = spx_df.rename(columns=lambda x: f"{x}_spx" if x != 'timestamp' else x)
    ce_df = ce_df.rename(columns=lambda x: f"{x}_ce" if x != 'timestamp' else x)
    pe_df = pe_df.rename(columns=lambda x: f"{x}_pe" if x != 'timestamp' else x)

    ce_df["OptionType_ce"] = "CE"
    pe_df["OptionType_pe"] = "PE"
    ce_df["Strike_ce"] = strike
    pe_df["Strike_pe"] = strike
    ce_df["Expiry_ce"] = expiry_day
    pe_df["Expiry_pe"] = expiry_day

    # Merge
    merged = spx_df.merge(ce_df, on="timestamp", how="outer")
    merged = merged.merge(pe_df, on="timestamp", how="outer")
    merged["TradingDate"] = trading_day
    return merged

def export_multi_day_data(trading_days, expiry_day, strike=None, output_file="SPX_Options_MultiDay.xlsx"):
    all_data = []
    for day in trading_days:
        print(f"📅 Fetching data for {day}")
        day_df = fetch_day_data(day, expiry_day, strike)
        if day_df is not None:
            all_data.append(day_df)

    if not all_data:
        print("⚠️ No data was fetched. Check errors above.")
        return

    final_df = pd.concat(all_data, ignore_index=True)

    # Export
    final_df.to_excel(output_file, index=False, sheet_name="SPX_and_Options")
    print(f"✅ All data exported to {output_file}")

# Example usage
if __name__ == "__main__":
    expiry_day = datetime.date(2024, 5, 31)

    # Define the list of trading days you want (10–15)
    trading_days = [
        datetime.date(2024, 5, 15),
        datetime.date(2024, 5, 16),
        datetime.date(2024, 5, 17),
        datetime.date(2024, 5, 20),
        datetime.date(2024, 5, 21),
        datetime.date(2024, 5, 22),
        datetime.date(2024, 5, 23),
        datetime.date(2024, 5, 24),
        datetime.date(2024, 5, 27),
        datetime.date(2024, 5, 28),
        datetime.date(2024, 5, 29),
        datetime.date(2024, 5, 30),
        datetime.date(2024, 5, 31),
    ]

    strike = None  # auto ATM; or set manually e.g. 5250
    export_multi_day_data(trading_days, expiry_day, strike)
