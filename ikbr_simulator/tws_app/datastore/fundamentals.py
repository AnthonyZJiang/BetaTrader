from rich import print

class StockFundamentals():
    
    def __init__(self, symbol) -> None:
        self.symbol = symbol
        self.mark_cap = 0
        self.float = 0
        self.shortable_shares = 0
        self.country = ""
        self.exchange = ""
        self.short_name = ""
        self.ceo = ""
        self.sector = ""
    
    @staticmethod
    def from_yf(ticker_info):
        def get_key_value(key, dict, default=None):
            return dict[key] if key in dict else default
        f = StockFundamentals(ticker_info["symbol"])
        f.symbol != ticker_info["symbol"]
        f.mark_cap = get_key_value("marketCap", ticker_info, -1)
        f.float = get_key_value("floatShares", ticker_info, -1)
        f.shortable_shares = get_key_value("shortableShares", ticker_info, -1)
        f.country = get_key_value("country", ticker_info, "Unknown")
        f.exchange = get_key_value("exchange", ticker_info, "Unknown")
        f.short_name = get_key_value("shortName", ticker_info, "Unknown")
        f.sector = get_key_value("sector", ticker_info, "Unknown")
        ceo_found = False
        for officer in get_key_value("companyOfficers", ticker_info, []):
            title = get_key_value("title", officer, "").lower()
            if title and 'ceo' in title:
                f.ceo = get_key_value("name", officer, "Unknown")
                ceo_found = True
                break
        if not ceo_found and "companyOfficers" in ticker_info and len(ticker_info["companyOfficers"]) > 0:
            f.ceo = get_key_value("name", ticker_info["companyOfficers"][0], "Unknown")
        return f
        
    def print(self) -> None:
        float_color = "[green]" if self.float < 2000000 else "[orange]" if self.float < 5000000 else "[red]"
        country_color = "[red]" if self.country.lower == "china" else "[green]"
        print(f"Symbol: [green]{self.symbol}")
        print(f"Short Name: [green]{self.short_name}")
        print(f"Sector: [green]{self.sector}")
        print(f"Market Cap: [green]${self.mark_cap:,}")
        print(f"Float: {float_color}{self.float:,}")
        print(f"Shortable Shares: [green]{self.shortable_shares:,}")
        print(f"Country: {country_color}{self.country}")
        print(f"CEO: [green]{self.ceo}")
        print(f"Exchange: [green]{self.exchange}")