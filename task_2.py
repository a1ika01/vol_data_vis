import pandas as pd
import dataframe_image as dfi
import matplotlib.colors as mcolors

class VisualiseCarryPerTenor:
    def __init__(self):
        self.vol_df = pd.read_csv("vol_data.csv", header=[0, 1])
        self.vol_df.columns = [((col[0], "") if "Unnamed" in col[1] else (col[0], col[1])) for col in self.vol_df.columns]
        self.ccys = self.get_g10_ccys()
        self.rwg_colourmap = self.create_colourmap()
        
    def run(self):
        self.tables = self.generate_carry_tables()
        self.generate_pngs(self.tables)
        
    def get_g10_ccys(self):
        g10_currencies = {"EUR", "USD", "JPY", "GBP", "AUD", "NZD", "CAD", "CHF", "NOK", "SEK"}
        existing_ccys = set(self.vol_df["CCY", ""])

        g10_ccys = [ccy for ccy in existing_ccys if all(ccy in g10_currencies for ccy in ccy.split("/"))]

        return g10_ccys

    def create_colourmap(self):
        colors = [
        (0.8, 0, 0, 0.6),  
        (1, 1, 1, 1.0),  
        (0, 0.8, 0, 0.6)   
        ]
        return mcolors.LinearSegmentedColormap.from_list("red_white_green", colors, N=256)
    
    def generate_carry_tables(self):
        tables = []
        tenors = ["6M", "1Y", "2Y", "5Y", "10Y"]
        indexs = ["Carry", "Pctl 6m", "Pctl 1y", "Pctl 2y", "Pctl 5y", "Pctl all"]
        for ccy in self.ccys:
            ccy_data = self.vol_df[self.vol_df["CCY", ""] == ccy]
            carry_data = ccy_data.loc[:, [("Carry", col) for col in ["Carry", "Pctl 6m", "Pctl 1y", "Pctl 2y", "Pctl 5y", "Pctl all"]]]
            carry_data.columns = indexs
            carry_data = carry_data.transpose()
            carry_data.columns = tenors
            
           
            just_carry_slice = (indexs[0], tenors)
            the_rest_slice = (indexs[1:], tenors)
            carry_table = carry_data.style.set_caption(f"{ccy}").format('{:.2f}').bar(color=('#FFCCCB', '#cbffcc'), align = 50, subset = the_rest_slice) \
                                                            .background_gradient(axis = 1, vmin = -5, vmax = 5, cmap = self.rwg_colourmap, text_color_threshold = 0, low = 0.5, high = 0.55, subset = just_carry_slice) \
                                                            .set_table_styles([
                                                                {'selector': 'caption', 'props': [('font-size', '24px'), ('margin-bottom', '10px')]}, 
                                                                {'selector': 'thead', 'props': [('border-bottom', '1px solid grey')]},
                                                                {"selector": "td", "props": [("max-width", "35px"), ("vertical-align", "middle"), ("text-align", "center")]},
                                                                {"selector": "th", "props": [("text-align", "center"), ("vertical-align", "middle")]}
                                                            ])
            
            tables.append({ccy : carry_table})
        return tables
    
    def generate_pngs(self, tables):
        for table in tables:
            for ccy, carry_table in table.items():
                image_path = f"{ccy}_carry.png".replace("/", "|")
                dfi.export(carry_table, image_path)
                

if __name__ == "__main__":
    visualise = VisualiseCarryPerTenor()