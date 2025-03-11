import pandas as pd
import sys
import dataframe_image as dfi
from PIL import Image
import os
import matplotlib.colors as mcolors

class GenerateVolatilityGrids:
    def __init__(self):
        self.vol_df = pd.read_csv("vol_data.csv", header=[0, 1])
        self.vol_df.columns = [((col[0], "") if "Unnamed" in col[1] else (col[0], col[1])) for col in self.vol_df.columns]
        self.rwg_colourmap = self.create_colourmap()

    def run(self, ccys):
        ccys = self.verify_ccys(ccys)
        self.grids = self.generate_grids(ccys)
        self.generate_pngs(self.grids)
        
    def create_colourmap(self):
        colors = [
        (0.8, 0.2, 0.2, 0.4),  
        (1, 1, 1, 1.0),        
        (0.2, 0.8, 0.2, 0.4)   
        ]
        return mcolors.LinearSegmentedColormap.from_list("red_white_green", colors, N=256).reversed()
    
    def get_existing_ccys(self):
        return set(self.vol_df["CCY", ""])
         
    def verify_ccys(self, ccys):
        if not ccys:
            print("No currency pairs were passed.")
            sys.exit(1)

        ccys = [ccy.upper() for ccy in ccys]
        existing_ccys = self.get_existing_ccys()
        if len(ccys) == 1 and ccys[0] == "ALL":
            return existing_ccys
        valid_ccys = [ccy for ccy in ccys if ccy in existing_ccys]
        invalid_ccys = [ccy for ccy in ccys if ccy not in existing_ccys]

        if invalid_ccys:
            print(f"The following currency pairs do not exist in csv or there was a typo: {', '.join(invalid_ccys)}")
        
        if not valid_ccys:
            print("no valid currency pairs were passed.")
            sys.exit(1)

        return valid_ccys
    
    def generate_grids(self, ccys):
        grids = []
        tenors = ["6M", "1Y", "2Y", "5Y", "10Y"]
        columns = ["10dp", "25dp", "ATM", "25dc", "10dc"]
        for ccy in ccys:
            ccy_data = self.vol_df[self.vol_df["CCY", ""] == ccy]

            implied_vol_data = ccy_data.loc[:, [("Vol", col) for col in ["10P", "25P", "ATM", "25C", "10C"]]]
            four_week_shift_data = ccy_data.loc[:, [("Vol 4wk-chg", col) for col in ["10P", "25P", "ATM", "25C", "10C"]]]
            vol_pctl_data = ccy_data.loc[:, [("Vol Pctl all", col) for col in ["10P", "25P", "ATM", "25C", "10C"]]]

            implied_vol_table = implied_vol_data.style.set_caption(f"{ccy}").relabel_index(tenors, axis=0).relabel_index(columns, axis=1) \
                                .format('{:.2f}').set_table_styles([
                                                                {'selector': 'caption', 'props': [('font-size', '24px'), ('margin-bottom', '10px')]}, 
                                                                {'selector': 'thead', 'props': [('border-bottom', '1px solid grey')]},
                                                                {"selector": "td", "props": [("max-width", "35px"), ("vertical-align", "middle"), ("text-align", "center")]},
                                                                {"selector": "th", "props": [("text-align", "center"), ("vertical-align", "middle")]}
                                                            ])

            four_week_shift_table = four_week_shift_data.style.set_caption(f"{ccy}").relabel_index(tenors, axis=0).relabel_index(columns, axis=1) \
                                .format('{:.2f}').bar(color=('#FFCCCB', '#cbffcc'), align = "zero").set_table_styles([
                                                                {'selector': 'caption', 'props': [('font-size', '24px'), ('margin-bottom', '10px')]}, 
                                                                {'selector': 'thead', 'props': [('border-bottom', '1px solid grey')]},
                                                                {"selector": "td", "props": [("max-width", "35px"), ("text-align", "center"), ("vertical-align", "middle")]},
                                                                {"selector": "th", "props": [("text-align", "center"), ("vertical-align", "middle")]}
                                                                ])
            
            vol_pctl_table = vol_pctl_data.style.set_caption(f"{ccy}").relabel_index(tenors, axis=0).relabel_index(columns, axis=1) \
                                .format('{:.2f}').background_gradient(axis = None, vmin = 0, vmax = 100, cmap = self.rwg_colourmap, text_color_threshold = 0, low= 0.5, high = 0.55).set_table_styles([
                                                                {'selector': 'caption', 'props': [('font-size', '24px'), ('margin-bottom', '10px')]}, 
                                                                {'selector': 'thead', 'props': [('border-bottom', '1px solid grey')]},
                                                                {"selector": "td", "props": [("max-width", "35px"), ("text-align", "center"), ("vertical-align", "middle")]},
                                                                {"selector": "th", "props": [("text-align", "center"), ("vertical-align", "middle")]}
                                                            ])
            
            grid = {ccy : [implied_vol_table, four_week_shift_table, vol_pctl_table]}
            grids.append(grid)
        return grids

    def generate_pngs(self, grids):
        image_paths = ["vol.png", "shift.png", "pctl.png"]
        for grid in grids:
            for ccy, tables in grid.items():
                
                dfi.export(tables[0], image_paths[0])
                dfi.export(tables[1], image_paths[1])
                dfi.export(tables[2], image_paths[2])

                images = [Image.open(img) for img in image_paths]
                y_space = 30
                total_height = sum(img.height for img in images) + 2*y_space
                max_width = max(img.width for img in images)

                merged_img = Image.new("RGB", (max_width, total_height), (255, 255, 255))

                y = 0
                for img in images:
                    merged_img.paste(img, (0, y))
                    y = y + img.height + y_space

                filename = ccy.replace("/", "|")+".png"
                merged_img.save(filename)
                
        for img in image_paths:
            os.remove(img)

if __name__ == "__main__":
    ccys = sys.argv[1:]
    generator = GenerateVolatilityGrids()
    generator.run(ccys)

    
    