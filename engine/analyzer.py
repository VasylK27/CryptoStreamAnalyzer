class PriceAnalyzer:
    def __init__(self, groups, threshold = 0.01):
        """
        :param groups: List of groups for comparison with config.json
        :param threshold: Threshold in percent
        """
        self.prices = {}
        self.groups = groups
        self.threshold = threshold

    async def process_update(self, data):
        """
        Receives data from BinanceWS and performs analysis.
        """
        symbol = data['symbol']
        self.prices[symbol] = {
            'bid': data['bid'],
            'ask': data['ask']
        }

        if len(self.prices) >= 2:
            return self.find_opportunities()
        return None
    
    def find_opportunities(self):
        results = []
        
        for group_data in self.groups:
            pairs = group_data["pairs"]
            current_threshold = group_data.get("threshold", self.threshold)
            
            for i in range(len(pairs)):
                for j in range(i + 1, len(pairs)):
                    s1, s2 = pairs[i], pairs[j]

                    if s1 in self.prices and s2 in self.prices:
                        price1 = self.prices[s1]['ask']
                        price2 = self.prices[s2]['ask']

                        diff = abs(price1 - price2)
                        percent_diff = (diff / max(price1, price2)) * 100

                        if percent_diff >= current_threshold:
                            results.append({
                                'pair': f"{s1} vs {s2}",
                                'diff_usd': round(diff, 2),
                                'diff_percent': round(percent_diff, 4),
                                'direction': s1 if price1 > price2 else s2
                            })
        return results
