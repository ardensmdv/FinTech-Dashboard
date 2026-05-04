# =======================================================================================
# PIECE 0: THE LIBRARY
# =======================================================================================
import yfinance as yf
import math
import time
import pandas as pd
from datetime import datetime
from tabulate import tabulate
import feedparser

# =======================================================================================
# PIECE 1: DEFINE THE COMPANIES GLOSSARIES
# =======================================================================================
LISTCO_FINTECH = {
    "Alibaba"       : "BABA",
    "Tencent"       : "0700.HK",
    "Sea Group"     : "SE",
    "Grab"          : "GRAB",
    "GoTo"          : "GOTO",
    "LendingClub"   : "LC",
    "Lufax"         : "LU",
    "FinVolution"   : "FINV",
    "FICO"          : "FICO",
    "TransUnion"    : "TRU",
    "Lemonade"      : "LMND",
    "Waterdrop"     : "WDH"
}

LISTCO_FINTECH_INFO = {
    "Alibaba": {
        "Classification"    : "BigTech",
        "Region"            : "China"
    },
    "Tencent": {
        "Classification"    : "BigTech",
        "Region"            : "China"
    },
    "Sea Group": {
        "Classification"    : "E-wallet",
        "Region"            : "SEA"
    },
    "Grab": {
        "Classification"    : "E-wallet",
        "Region"            : "SEA"
    },
    "GoTo": {
        "Classification"    : "E-wallet",
        "Region"            : "SEA"
    },
    "LendingClub": {
        "Classification"    : "Lending",
        "Region"            : "USA"
    },
    "Lufax": {
        "Classification"    : "Lending",
        "Region"            : "China"
    },
    "FinVolution": {
        "Classification"    : "Lending",
        "Region"            : "China"
    },
    "FICO": {
        "Classification"    : "Credit Engine",
        "Region"            : "USA"
    },
    "TransUnion": {
        "Classification"    : "Credit Engine",
        "Region"            : "USA"
    },
    "Lemonade": {
        "Classification"    : "InsurTech",
        "Region"            : "USA"
    },
    "Waterdrop": {
        "Classification"    : "InsurTech",
        "Region"            : "China"
    }
}
print("\nPiece 1 Completed.\n")
# print(f"{3154.75:,.2f}")   # should print 3,154.75

# =======================================================================================
# PIECE 2: DEFINE THE FUNCTION TO CALL KEY STUFF FROM YAHOO FINANCE
# =======================================================================================
def get_key_info(tick, fx_rate=1):

    stock_name = yf.Ticker(tick)
    stock_info  = stock_name.info          

    def to_billions(value):
        if value and value !=0:
            if isinstance(value, float):
                if math.isnan(value):
                    return "N/A"
            result = f"{round((value * fx_rate) / 1e9, 2):,.2f}"
            # print(f"DEBUG to_billions: {value} → {result}")
            return result
        return "N/A"
    
    def format_multiple(value, net_income=None, ebitda=None, revenue=None, outlier_cap=500):
        # setting to not include the outlier
        if net_income is not None and net_income < 0:
            return "n.m."
        if ebitda is not None and ebitda < 0:
            return "n.m."
        if value is None or value == 0:
            return "N/A"
        if isinstance(value, float) and math.isnan(value):
            return "N/A"
        if value < 0:
            return "n.m."
        if value > outlier_cap:
            return "n.m."
        # if underlying metric is negative → n.m.
        return f"{round(value, 2)}x"
    
    net_income = stock_info.get("netIncomeToCommon", 0) or 0
    ebitda     = stock_info.get("ebitda", 0) or 0
    revenue     = stock_info.get("totalRevenue", 0) or 0


    result = {
        "Market Cap ($B)"       : to_billions(stock_info.get("marketCap", 0)),
        "Revenue ($B)"          : to_billions(stock_info.get("totalRevenue", 0)),
        "Net Profit ($B)"       : to_billions(stock_info.get("netIncomeToCommon", 0)),
        "Enterprise Value ($B)" : to_billions(stock_info.get("enterpriseValue", 0)),
        "EBITDA ($B)"           : to_billions(stock_info.get("ebitda", 0)),
        # multiples start here
        "Trailing P/E"          : format_multiple(stock_info.get("trailingPE"), net_income=net_income),
        "Trailing EV/EBITDA"    : format_multiple(stock_info.get("enterpriseToEbitda"), ebitda=ebitda),
        "Trailing EV/Revenue"   : format_multiple(stock_info.get("enterpriseToRevenue"), revenue=revenue)
        }
    
    return result
print("Piece 2 Completed.\n")
    

# =======================================================================================
# PIECE 3: IDENTIFYING AND AUTOMATING FX RATE
# =======================================================================================
def get_fx_rate(currency):

    if currency == "USD":
        return 1
    
    try:
        # I'm building the yahoo finance fx ticker
        fx_ticker = f"{currency}USD=X"
        fx_stock  = yf.Ticker(fx_ticker)
        fx_info   = fx_stock.info
        rate      = fx_info.get("regularMarketPrice", None)

        if rate and rate > 0:
            readable_rate = 1 / rate
            print(f"1 USD = {readable_rate:,.3f} {currency}")
            return rate
        else:
            print(f"\ncould not fetch")

            return 1
        
    except Exception as e:
        print(f"\n FX error {currency}: {e}")
        return 1
print("Piece 3 Completed.\n")
#for value in LISTCO_FINTECH_INFO:
    #print(value)


# =======================================================================================
# PIECE 4: RUN THE COMPANIES
# =======================================================================================
def run_the_companies():

    run_data = []
    # the [] is a list

    fx_cache = {}
    # the {} is a dictionary

    print("Piece 4 starts\n")
    print("Running the companies...\n")

    for company_name, ticker in LISTCO_FINTECH.items():
        # this means for x = key and y = values in ListCo.FINTECH, get those items

        print(f"{company_name}...", end=" ")

        info = LISTCO_FINTECH_INFO.get(company_name, {})
        # I'm defining to get the company name first (key) so I can refer to the next one

        row = {
            "Company"   : company_name,
            "Category"  : info.get("Classification"),
            "Region"    : info.get("Region"),
        }

        try:
            temp_stock = yf.Ticker(ticker)
            # run the ticker values through Yahoo Finance

            temp_info = temp_stock.info
            # get all the info from those tickers

            currency = temp_info.get("currency", "USD")
            # if it's not found, then go to USD as my default value

            if currency not in fx_cache:
                fx_cache[currency] = get_fx_rate(currency)

            fx_rate = fx_cache[currency]

            financial_data = get_key_info(ticker, fx_rate)
            row.update(financial_data)
            print("✅\n")

            #print(f"{company_name} | Currency: {currency} | FX Rate: {fx_rate}")
            #print(f"  Raw Market Cap : {temp_info.get('marketCap')}")
            #print(f"  Raw Revenue    : {temp_info.get('totalRevenue')}")
            #print(f"  Raw EV         : {temp_info.get('enterpriseValue')}")

        except Exception as e:
            row.update({
                "Country"               : "Error",
                "Market Cap ($B)"       : "Error",
                "Revenue ($B)"          : "Error",
                "Net Profit ($B)"       : "Error",
                "Enterprise Value ($B)" : "Error",
                "EBITDA ($B)"           : "Error",
                "P/E"                   : "Error",
                "EV/EBITDA"             : "Error"
            })
            print(f"The error is {e}")

        run_data.append(row)
        time.sleep(2)

    return run_data

data = run_the_companies()
# this is how you run the function
print("Piece 4 Completed.")


# =======================================================================================
# PIECE 5: DISPLAYING THE TABLE IN TERMINAL FIRST
# =======================================================================================
def show_table(run_data):

    FINTECH_table = pd.DataFrame(run_data)
    # don't forget to import pandas as pd
    
    print("Testing FINTECH Sector")
    print("=" * 120)
    print(f"Data as of:{datetime.now().strftime('%B %d, %Y - %H:%M')}")
    # strftime is string format time
    print("=" * 120)

    print(tabulate(
        FINTECH_table,
        headers = "keys",
        tablefmt = "rounded_outline",
        showindex = False,
        disable_numparse=True
    ))

    return FINTECH_table

show_table(data)


# =======================================================================================
# PIECE 6: SUMMARY - MEDIAN BY CATEGORY AND REGION
# =======================================================================================
def show_summary(FINTECH_table):
    
    multiples = ["Trailing P/E", "Trailing EV/EBITDA", "Trailing EV/Revenue"]
    
    # Convert "23.0x" → 23.0, "n.m." / "N/A" → None
    def clean_multiple(val):
        if isinstance(val, str) and val.endswith("x"):
            try:
                return float(val.replace("x", ""))
            except:
                return None
        return None

    # clean numeric copy
    clean_df = FINTECH_table.copy()
    for col in multiples:
        clean_df[col] = clean_df[col].apply(clean_multiple)

    # --- BY CATEGORY ---
    print("\n" + "=" * 80)
    print("MEDIAN MULTIPLES BY CATEGORY")
    print("=" * 80)
    category_summary = (
        clean_df.groupby("Category")[multiples]
        .median(numeric_only=True)
        .reset_index()
    )
    for col in multiples:
        category_summary[col] = category_summary[col].apply(
            lambda x: f"{round(x, 2)}x" if pd.notna(x) else "n.m."
        )
    print(tabulate(
        category_summary,
        headers="keys",
        tablefmt="rounded_outline",
        showindex=False,
        disable_numparse=True
    ))

    # --- BY REGION ---
    print("\n" + "=" * 80)
    print("MEDIAN MULTIPLES BY REGION")
    print("=" * 80)
    region_summary = (
        clean_df.groupby("Region")[multiples]
        .median(numeric_only=True)
        .reset_index()
    )
    for col in multiples:
        region_summary[col] = region_summary[col].apply(
            lambda x: f"{round(x, 2)}x" if pd.notna(x) else "n.m."
        )
    print(tabulate(
        region_summary,
        headers="keys",
        tablefmt="rounded_outline",
        showindex=False,
        disable_numparse=True
    ))

    return category_summary, region_summary


if __name__ == "__main__":
    FINTECH_table = show_table(data)
    show_summary(FINTECH_table)




# =======================================================================================
# PIECE 7: NEWS FEED
# =======================================================================================
NEWS_QUERIES = {
    # By Sector
    "All"             : "All Financial Technology sector",
    "BigTech"         : "Alibaba Tencent Financial",
    "E-wallet"        : "E-wallet ShopeePay GrabPay Ovo DANA Gopay",
    "Lending"         : "Lending LendingClub Lufax FinVolution",
    "Credit Engine"   : "Credit Engine FICO TransUnion",
    "InsurTech"       : "Insurance Tech Lemonade waterdrop",
    # By Country
    "China"     : "China Financial technology",
    "USA"       : "United States America Financial technology",
    "SEA"       : "Indonesia Singapore Vietnam Malaysia Thailand Financial Technology"
}

def get_news(query_key, num_articles=3):
    query   = NEWS_QUERIES.get(query_key, "Financial Technology")
    url     = f"https://news.google.com/rss/search?q={query.replace(' ', '+')}&hl=en-US&gl=US&ceid=US:en"
    feed    = feedparser.parse(url)
    results = []
    for entry in feed.entries[:num_articles]:
        results.append({
            "title"     : entry.get("title", "N/A"),
            "link"      : entry.get("link", "#"),
            "published" : entry.get("published", "N/A"),
            "source"    : entry.get("source", {}).get("title", "N/A")
        })
    return results