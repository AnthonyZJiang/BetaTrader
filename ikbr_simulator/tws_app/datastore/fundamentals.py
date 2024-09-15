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
        f = StockFundamentals(ticker_info["symbol"])
        f.symbol != ticker_info["symbol"]
        f.mark_cap = ticker_info["marketCap"]
        f.float = ticker_info["floatShares"]
        f.shortable_shares = ticker_info["sharesShort"]
        f.country = ticker_info["country"]
        f.exchange = ticker_info["exchange"]
        f.short_name = ticker_info["shortName"]
        f.sector = ticker_info["sector"]
        ceo_found = False
        for officer in ticker_info["companyOfficers"]:
            if 'ceo' in officer["title"]:
                f.ceo = officer["name"]
                ceo_found = True
                break
        if not ceo_found:
            f.ceo = ticker_info["companyOfficers"][0]["name"]
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