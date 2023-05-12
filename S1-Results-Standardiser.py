# S1 Results Standardiser by ZH for PSS
versionNum = 'v0.0.4'
versionDate = '2023/03/27'

import csv
import os
import sys
import tkinter as tk
from tkinter import filedialog
import customtkinter as ctk
import pandas as pd
import numpy as np
import math
import chemparse


ctk.set_appearance_mode("System")  # Modes: "System" (standard), "Dark", "Light"
ctk.set_default_color_theme("blue")  # Themes: "blue" (standard), "green", "dark-blue"


class App(ctk.CTk):
    def __init__(self, *args, **kwargs):

        # call the parent class init
        super().__init__(*args, **kwargs)   

        # configure the window
        self.title(f'S1 Results Standardiser {versionNum}')
        self.iconbitmap(resource_path("data_sheet_icon.ico"))
        #self.geometry('600x400')

        # configure grid layout
        self.grid_rowconfigure(2, weight=1)

        # create file input frame and widgets
        self.file_input_frame = ctk.CTkFrame(self, width=400)
        self.file_input_frame.grid(row=1, column=0, padx=8, pady=(8,4), sticky='nsew')
        
        self.input_csv_path_entrybox = ctk.CTkEntry(self.file_input_frame, width=290, placeholder_text='Input Results CSV path')
        self.input_csv_path_entrybox.pack(side = tk.LEFT, padx = 8, pady = 8, fill = 'both', expand = True)

        self.input_csv_path_browse_button = ctk.CTkButton(self.file_input_frame, text='Browse', width=20, command=self.input_csv_path_browse_clicked)
        self.input_csv_path_browse_button.pack(side = tk.LEFT, padx = (0,8), pady = 8, fill = 'both', expand = False)

        # main options frame and widgets
        self.main_options_frame = ctk.CTkFrame(self, width=250)
        self.main_options_frame.grid(row=2, column=0, padx=8, pady=4, sticky='nsew')


        # units options toggle
        self.units_options_toggle = ctk.CTkCheckBox(self.main_options_frame, text='Adjust Units', command=self.toggleUnitsOptions)
        self.units_options_toggle.grid(row=1, column=1, padx=8, pady=(8,8), sticky='nsew')
        # units options frame and widgets
        self.units_options_frame = ctk.CTkFrame(self.main_options_frame)
        self.units_options_frame.grid(row=1, column=2, padx=8, pady=(8,8), sticky='nsew')
        self.units_from_label = ctk.CTkLabel(self.units_options_frame, text='Convert From')
        self.units_from_label.pack(side = tk.LEFT, padx = (8,0), pady = 8, fill = 'both', expand = False)
        self.units_from_combobox = ctk.CTkOptionMenu(self.units_options_frame, width=70, values=['ppm','ppb','%'])
        self.units_from_combobox.pack(side = tk.LEFT, padx = (4,4), pady = 8, fill = 'both', expand = False)
        self.units_to_label = ctk.CTkLabel(self.units_options_frame, text='To')
        self.units_to_label.pack(side = tk.LEFT, padx = (0,0), pady = 8, fill = 'both', expand = False)
        self.units_to_combobox = ctk.CTkOptionMenu(self.units_options_frame, width=90, values=['ppm','ppb','%'])
        self.units_to_combobox.pack(side = tk.LEFT, padx = (4,8), pady = 8, fill = 'both', expand = False)
        self.units_inheaders_checkbox = ctk.CTkCheckBox(self.units_options_frame, text='Add Units to Column Headers (e.g. "Fe (ppm)")')
        self.units_inheaders_checkbox.pack(side = tk.BOTTOM, padx = (8,8), pady = 8, fill = 'both', expand = True)
        self.units_options_toggle.toggle()  # Start with section enabled
        self.units_options_toggle.toggle()  # Start with section disabled

        # Compounds options toggle
        self.compounds_options_toggle = ctk.CTkCheckBox(self.main_options_frame, text='Convert Compounds', command=self.toggleCompoundsOptions)
        self.compounds_options_toggle.grid(row=3, column=1, padx=8, pady=(0,8), sticky='nsew')
        # Compounds options frame and widgets
        self.compounds_options_frame = ctk.CTkFrame(self.main_options_frame)
        self.compounds_options_frame.grid(row=3, column=2, padx=8, pady=(0,8), sticky='nsew')
        self.compounds_desc_label = ctk.CTkLabel(self.compounds_options_frame, text="(This will convert Compound concentrations to Elemental concentrations (e.g. 10% Al2O3 -> 5.2925% Al))")
        self.compounds_desc_label.pack(side = tk.LEFT, padx = (8,8), pady = 8, fill = 'both', expand = False)
        self.compounds_ignoreSi_checkbox = ctk.CTkCheckBox(self.compounds_options_frame, text='Ignore SiO2')
        self.compounds_ignoreSi_checkbox.pack(side = tk.BOTTOM, padx = (8,8), pady = 8, fill = 'both', expand = True)
        self.compounds_options_toggle.toggle()  # Start with section enabled
        self.compounds_options_toggle.toggle()  # Start with section disabled

        # LOD options toggle
        self.LOD_options_toggle = ctk.CTkCheckBox(self.main_options_frame, text="Replace '<LOD'", command=self.toggleLODOptions)
        self.LOD_options_toggle.grid(row=4, column=1, padx=8, pady=(0,8), sticky='nsew')
        # LOD options frame and widgets
        self.LOD_options_frame = ctk.CTkFrame(self.main_options_frame)
        self.LOD_options_frame.grid(row=4, column=2, padx=8, pady=(0,8), sticky='nsew')
        self.LOD_label = ctk.CTkLabel(self.LOD_options_frame, text="Replace instances of '< LOD' with:")
        self.LOD_label.pack(side = tk.LEFT, padx = (8,0), pady = 8, fill = 'both', expand = False)
        self.LOD_to_combobox = ctk.CTkComboBox(self.LOD_options_frame, width=90, values=["-1","0","1","10","","ND","T"])
        self.LOD_to_combobox.pack(side = tk.LEFT, padx = (4,4), pady = 8, fill = 'both', expand = False)
        self.LOD_options_toggle.toggle()  # Start with section enabled

        # EmptyCell options toggle
        self.emptycell_options_toggle = ctk.CTkCheckBox(self.main_options_frame, text="Replace Empty Cells", command=self.toggleEmptyCellOptions)
        self.emptycell_options_toggle.grid(row=5, column=1, padx=8, pady=(0,8), sticky='nsew')
        # EmptyCell options frame and widgets
        self.emptycell_options_frame = ctk.CTkFrame(self.main_options_frame)
        self.emptycell_options_frame.grid(row=5, column=2, padx=8, pady=(0,8), sticky='nsew')
        self.emptycell_label = ctk.CTkLabel(self.emptycell_options_frame, text="Replace empty Results/Error values with:")
        self.emptycell_label.pack(side = tk.LEFT, padx = (8,0), pady = 8, fill = 'both', expand = False)
        self.emptycell_to_combobox = ctk.CTkComboBox(self.emptycell_options_frame, width=180, values=["0","1","-1","Not Reported","T"])
        self.emptycell_to_combobox.pack(side = tk.LEFT, padx = (4,4), pady = 8, fill = 'both', expand = False)
        self.emptycell_options_toggle.toggle()  # Start with section enabled
        self.emptycell_options_toggle.toggle()  # Start with section disabled

        # create status bar frame and widgets
        self.status_bar_frame = ctk.CTkFrame(self, width=250)
        self.status_bar_frame.grid(row=3, column=0, padx=8, pady=(4,8), sticky='nsew')

        self.process_results_button = ctk.CTkButton(self.status_bar_frame, text='Process Results', width=70, command=self.process_results_clicked)
        self.process_results_button.grid(row=1, column=1, padx = (8,8), pady = 8, sticky='nsew')

        self.copytoclipboard_button = ctk.CTkButton(self.status_bar_frame, text='Copy Results to Clipboard', width=70, command=None, state=tk.DISABLED)
        self.copytoclipboard_button.grid(row=1, column=3, padx = (16,8), pady = 8, sticky='nsew')

        self.savetofile_button = ctk.CTkButton(self.status_bar_frame, text='Save Results to File', width=70, command=None, state=tk.DISABLED)
        self.savetofile_button.grid(row=1, column=4, padx = (0,8), pady = 8, sticky='nsew')

        # column matchstrs for df
        self.element_column_matchstrs = ['H', 'He', 'Li', 'Be', 'B', 'C', 'N', 'O', 'F', 'Ne', 'Na', 'Mg', 'Al', 'Si', 'P', 'S', 'Cl', 'Ar', 'K', 'Ca', 'Sc', 'Ti', 'V', 'Cr', 'Mn', 'Fe', 'Co', 'Ni', 'Cu', 'Zn', 'Ga', 'Ge', 'As', 'Se', 'Br', 'Kr', 'Rb', 'Sr', 'Y', 'Zr', 'Nb', 'Mo', 'Tc', 'Ru', 'Rh', 'Pd', 'Ag', 'Cd', 'In', 'Sn', 'Sb', 'Te', 'I', 'Xe', 'Cs', 'Ba', 'La', 'Ce', 'Pr', 'Nd', 'Pm', 'Sm', 'Eu', 'Gd', 'Tb', 'Dy', 'Ho', 'Er', 'Tm', 'Yb', 'Lu', 'Hf', 'Ta', 'W', 'Re', 'Os', 'Ir', 'Pt', 'Au', 'Hg', 'Tl', 'Pb', 'Bi', 'Po', 'At', 'Rn', 'Fr', 'Ra', 'Ac', 'Th', 'Pa', 'U', 'Np', 'Pu', 'Am', 'Cm', 'Bk', 'Cf', 'Es', 'Fm', 'Md', 'No', 'Lr', 'Rf', 'Db', 'Sg', 'Bh', 'Hs', 'Mt', 'Ds', 'Rg', 'Cn', 'Nh', 'Fl', 'Mc', 'Lv', 'Ts', 'Og', 'H_IDX', 'He_IDX', 'Li_IDX', 'Be_IDX', 'B_IDX', 'C_IDX', 'N_IDX', 'O_IDX', 'F_IDX', 'Ne_IDX', 'Na_IDX', 'Mg_IDX', 'Al_IDX', 'Si_IDX', 'P_IDX', 'S_IDX', 'Cl_IDX', 'Ar_IDX', 'K_IDX', 'Ca_IDX', 'Sc_IDX', 'Ti_IDX', 'V_IDX', 'Cr_IDX', 'Mn_IDX', 'Fe_IDX', 'Co_IDX', 'Ni_IDX', 'Cu_IDX', 'Zn_IDX', 'Ga_IDX', 'Ge_IDX', 'As_IDX', 'Se_IDX', 'Br_IDX', 'Kr_IDX', 'Rb_IDX', 'Sr_IDX', 'Y_IDX', 'Zr_IDX', 'Nb_IDX', 'Mo_IDX', 'Tc_IDX', 'Ru_IDX', 'Rh_IDX', 'Pd_IDX', 'Ag_IDX', 'Cd_IDX', 'In_IDX', 'Sn_IDX', 'Sb_IDX', 'Te_IDX', 'I_IDX', 'Xe_IDX', 'Cs_IDX', 'Ba_IDX', 'La_IDX', 'Ce_IDX', 'Pr_IDX', 'Nd_IDX', 'Pm_IDX', 'Sm_IDX', 'Eu_IDX', 'Gd_IDX', 'Tb_IDX', 'Dy_IDX', 'Ho_IDX', 'Er_IDX', 'Tm_IDX', 'Yb_IDX', 'Lu_IDX', 'Hf_IDX', 'Ta_IDX', 'W_IDX', 'Re_IDX', 'Os_IDX', 'Ir_IDX', 'Pt_IDX', 'Au_IDX', 'Hg_IDX', 'Tl_IDX', 'Pb_IDX', 'Bi_IDX', 'Po_IDX', 'At_IDX', 'Rn_IDX', 'Fr_IDX', 'Ra_IDX', 'Ac_IDX', 'Th_IDX', 'Pa_IDX', 'U_IDX', 'Np_IDX', 'Pu_IDX', 'Am_IDX', 'Cm_IDX', 'Bk_IDX', 'Cf_IDX', 'Es_IDX', 'Fm_IDX', 'Md_IDX', 'No_IDX', 'Lr_IDX', 'Rf_IDX', 'Db_IDX', 'Sg_IDX', 'Bh_IDX', 'Hs_IDX', 'Mt_IDX', 'Ds_IDX', 'Rg_IDX', 'Cn_IDX', 'Nh_IDX', 'Fl_IDX', 'Mc_IDX', 'Lv_IDX', 'Ts_IDX', 'Og_IDX', 'H Err', 'He Err', 'Li Err', 'Be Err', 'B Err', 'C Err', 'N Err', 'O Err', 'F Err', 'Ne Err', 'Na Err', 'Mg Err', 'Al Err', 'Si Err', 'P Err', 'S Err', 'Cl Err', 'Ar Err', 'K Err', 'Ca Err', 'Sc Err', 'Ti Err', 'V Err', 'Cr Err', 'Mn Err', 'Fe Err', 'Co Err', 'Ni Err', 'Cu Err', 'Zn Err', 'Ga Err', 'Ge Err', 'As Err', 'Se Err', 'Br Err', 'Kr Err', 'Rb Err', 'Sr Err', 'Y Err', 'Zr Err', 'Nb Err', 'Mo Err', 'Tc Err', 'Ru Err', 'Rh Err', 'Pd Err', 'Ag Err', 'Cd Err', 'In Err', 'Sn Err', 'Sb Err', 'Te Err', 'I Err', 'Xe Err', 'Cs Err', 'Ba Err', 'La Err', 'Ce Err', 'Pr Err', 'Nd Err', 'Pm Err', 'Sm Err', 'Eu Err', 'Gd Err', 'Tb Err', 'Dy Err', 'Ho Err', 'Er Err', 'Tm Err', 'Yb Err', 'Lu Err', 'Hf Err', 'Ta Err', 'W Err', 'Re Err', 'Os Err', 'Ir Err', 'Pt Err', 'Au Err', 'Hg Err', 'Tl Err', 'Pb Err', 'Bi Err', 'Po Err', 'At Err', 'Rn Err', 'Fr Err', 'Ra Err', 'Ac Err', 'Th Err', 'Pa Err', 'U Err', 'Np Err', 'Pu Err', 'Am Err', 'Cm Err', 'Bk Err', 'Cf Err', 'Es Err', 'Fm Err', 'Md Err', 'No Err', 'Lr Err', 'Rf Err', 'Db Err', 'Sg Err', 'Bh Err', 'Hs Err', 'Mt Err', 'Ds Err', 'Rg Err', 'Cn Err', 'Nh Err', 'Fl Err', 'Mc Err', 'Lv Err', 'Ts Err', 'Og Err','H_IDX Err', 'He_IDX Err', 'Li_IDX Err', 'Be_IDX Err', 'B_IDX Err', 'C_IDX Err', 'N_IDX Err', 'O_IDX Err', 'F_IDX Err', 'Ne_IDX Err', 'Na_IDX Err', 'Mg_IDX Err', 'Al_IDX Err', 'Si_IDX Err', 'P_IDX Err', 'S_IDX Err', 'Cl_IDX Err', 'Ar_IDX Err', 'K_IDX Err', 'Ca_IDX Err', 'Sc_IDX Err', 'Ti_IDX Err', 'V_IDX Err', 'Cr_IDX Err', 'Mn_IDX Err', 'Fe_IDX Err', 'Co_IDX Err', 'Ni_IDX Err', 'Cu_IDX Err', 'Zn_IDX Err', 'Ga_IDX Err', 'Ge_IDX Err', 'As_IDX Err', 'Se_IDX Err', 'Br_IDX Err', 'Kr_IDX Err', 'Rb_IDX Err', 'Sr_IDX Err', 'Y_IDX Err', 'Zr_IDX Err', 'Nb_IDX Err', 'Mo_IDX Err', 'Tc_IDX Err', 'Ru_IDX Err', 'Rh_IDX Err', 'Pd_IDX Err', 'Ag_IDX Err', 'Cd_IDX Err', 'In_IDX Err', 'Sn_IDX Err', 'Sb_IDX Err', 'Te_IDX Err', 'I_IDX Err', 'Xe_IDX Err', 'Cs_IDX Err', 'Ba_IDX Err', 'La_IDX Err', 'Ce_IDX Err', 'Pr_IDX Err', 'Nd_IDX Err', 'Pm_IDX Err', 'Sm_IDX Err', 'Eu_IDX Err', 'Gd_IDX Err', 'Tb_IDX Err', 'Dy_IDX Err', 'Ho_IDX Err', 'Er_IDX Err', 'Tm_IDX Err', 'Yb_IDX Err', 'Lu_IDX Err', 'Hf_IDX Err', 'Ta_IDX Err', 'W_IDX Err', 'Re_IDX Err', 'Os_IDX Err', 'Ir_IDX Err', 'Pt_IDX Err', 'Au_IDX Err', 'Hg_IDX Err', 'Tl_IDX Err', 'Pb_IDX Err', 'Bi_IDX Err', 'Po_IDX Err', 'At_IDX Err', 'Rn_IDX Err', 'Fr_IDX Err', 'Ra_IDX Err', 'Ac_IDX Err', 'Th_IDX Err', 'Pa_IDX Err', 'U_IDX Err', 'Np_IDX Err', 'Pu_IDX Err', 'Am_IDX Err', 'Cm_IDX Err', 'Bk_IDX Err', 'Cf_IDX Err', 'Es_IDX Err', 'Fm_IDX Err', 'Md_IDX Err', 'No_IDX Err', 'Lr_IDX Err', 'Rf_IDX Err', 'Db_IDX Err', 'Sg_IDX Err', 'Bh_IDX Err', 'Hs_IDX Err', 'Mt_IDX Err', 'Ds_IDX Err', 'Rg_IDX Err', 'Cn_IDX Err', 'Nh_IDX Err', 'Fl_IDX Err', 'Mc_IDX Err', 'Lv_IDX Err', 'Ts_IDX Err', 'Og_IDX Err']
        self.compound_column_matchstrs = ['MgO', 'MgO Err', 'Al2O3', 'Al2O3 Err', 'SiO2', 'SiO2 Err', 'K2O', 'K2O Err']
        self.special_conc_column_matchstrs = ['TREE', 'LREE', 'HREE', 'TREE Err', 'LREE Err', 'HREE Err']

    def input_csv_path_browse_clicked(self):
        newpath = filedialog.askopenfilename(filetypes=[("CSV File", "*.csv")], initialdir = os.getcwd())
        self.input_csv_path_entrybox.delete(0,tk.END)
        self.input_csv_path_entrybox.insert(0,newpath)
    
    def process_results_clicked(self):
        filepath = self.input_csv_path_entrybox.get()
        df = createDFfromCSV(filepath)
        modified_df = self.processResultsinDF(df=df) # and other args

        self.initialiseCopyToClipboardButton(modified_df)
        # df.to_clipboard(index=False)
        # print('Results copied to clipboard')
    
    def initialiseCopyToClipboardButton(self, mdf):
        self.copytoclipboard_button.configure(command=lambda: mdf.to_clipboard(index=False), state=tk.NORMAL)
        self.savetofile_button.configure(command=lambda: self.csvSaveAs(mdf), state=tk.NORMAL)

    def csvSaveAs(self, dataf):
        # save as csv file
        filename = filedialog.asksaveasfilename(initialdir = os.getcwd(),title = "Save As",filetypes = (("CSV File","*.csv"),("all files","*.*")))
        dataf.to_csv(filename, index=False)

    def toggleUnitsOptions(self):
        if self.units_options_toggle.get():
            for child in self.units_options_frame.winfo_children():
                child.configure(state=tk.NORMAL)
        else:
            for child in self.units_options_frame.winfo_children():
                child.configure(state=tk.DISABLED)
    
    def toggleLODOptions(self):
        if self.LOD_options_toggle.get():
            for child in self.LOD_options_frame.winfo_children():
                child.configure(state=tk.NORMAL)
        else:
            for child in self.LOD_options_frame.winfo_children():
                child.configure(state=tk.DISABLED)

    def toggleEmptyCellOptions(self):
        if self.emptycell_options_toggle.get():
            for child in self.emptycell_options_frame.winfo_children():
                child.configure(state=tk.NORMAL)
        else:
            for child in self.emptycell_options_frame.winfo_children():
                child.configure(state=tk.DISABLED)
    
    def toggleCompoundsOptions(self):
        if self.compounds_options_toggle.get():
            for child in self.compounds_options_frame.winfo_children():
                child.configure(state=tk.NORMAL)
        else:
            for child in self.compounds_options_frame.winfo_children():
                child.configure(state=tk.DISABLED)
        
    
    def processResultsinDF(self,df:pd.DataFrame):        
        # CHECK FOR SETTINGS FOR PROCESSING  -  check for section toggles, then individual toggles and settings where applicable
        do_convert_units = False
        do_units_inheaders = False
        if self.units_options_toggle.get():
            print('Modify Units Checked...')
            # check units settings
            units_from = self.units_from_combobox.get()
            units_to = self.units_to_combobox.get()
            unit_conversion_factor = getUnitConversionFactor(units_from,units_to)  # returns factor to multiply by to convert from units_from to units_to in df
            if unit_conversion_factor != 1:
                print('Will Convert Units...')
                do_convert_units = True
            elif unit_conversion_factor == 1:
                print('Will NOT Convert Units (Conversion Factor = 1)...')
            if self.units_inheaders_checkbox.get():
                ('Will Add Units to Headers...')
                do_units_inheaders = True

        do_LOD_replace = False
        if self.LOD_options_toggle.get():
            do_LOD_replace = True
            # check LOD settings
            LOD_replacewith = self.LOD_to_combobox.get()
            print(f'Will Replace <LODs with "{LOD_replacewith}"...')
        
        do_emptycell_replace = False
        if self.emptycell_options_toggle.get():
            do_emptycell_replace = True
            # check empty cell settings
            emptycell_replacewith = self.emptycell_to_combobox.get()
            print(f'Will Replace EmptyCells with "{emptycell_replacewith}"...')

        do_convert_compounds = False
        do_ignoreSi = False
        if self.compounds_options_toggle.get():
            print('Will Convert Compound conc. to Elemental conc. ...')
            do_convert_compounds = True
            if self.compounds_ignoreSi_checkbox.get():
                print('Will Ignore SiO2 in Compound Conversion...')
                do_ignoreSi = True
        
        # PROCESS DATAFRAME
        for col in df.columns:
            # if column name is in element_column_matchstrs or compound_column_matchstrs or special_conc_column_matchstrs, then multiply values in the column by unit_conversion_factor
            if col in self.element_column_matchstrs or col in self.compound_column_matchstrs or col in self.special_conc_column_matchstrs:
                newcol = []
                for row in df[col]:
                    print(f'col={col}, row={row}, rowtype={type(row)}')
                    val = row                
                    if do_convert_units:
                        #print(f'Converting units for {col}')
                        #df[col] = pd.to_numeric(df[col],errors='coerce').multiply(unit_conversion_factor)
                        try:
                            val = float(row) * unit_conversion_factor
                            print(f'In Col "{col}", Converted {row} {units_from} to {units_to} = {val}')
                        except:
                            print(f'in Col "{col}", value "{row}" could not be converted. Proceeding...')

                    if do_emptycell_replace:
                        if (row == '') or (dfValueIsNaN(row)):
                            val = emptycell_replacewith
                            print(f'replaced Empty Cell with "{emptycell_replacewith}" in Col "{col}"')

                    if do_LOD_replace:
                        if row == '< LOD':
                            val = LOD_replacewith
                            #print(f'replaced "< LOD" with "{LOD_replacewith}" in Col "{col}"')
                        
                    newcol.append(val)

                df[col] = newcol

                if do_convert_compounds:
                    if col in self.compound_column_matchstrs:
                        if 'Si' in col and do_ignoreSi:
                            print(f'In Col "{col}", Ignoring SiO2 for Compound Conversion...')
                        else:
                            col_suffix = ''
                            if ' ' in col:  # col has suffix, is not ONLY compound string
                                col_compound = col.split(' ',1)[0]
                                col_suffix = col.split(' ',1)[1]
                            else:
                                col_compound = col
                                col_suffix = ''

                            col_eoi = get_element_from_formula(col_compound)
                            col_compound_factor = compound_to_element_factor(col_eoi, col_compound)
                            print(f'Converting Column "{col}" compound concentrations to elemental concentrations.')

                            newcol = []
                            for row in df[col]:
                                val = row
                                try:
                                    val = float(row) * col_compound_factor
                                    print(f'In Col "{col}", Converted row from {col_compound} conc. to e{col_eoi} conc. = {row} -> {val}')
                                except:
                                    print(f'in Col "{col}", value "{row}" could not be converted from {col_compound}. Proceeding...')
                            
                                newcol.append(val)
                            df[col] = newcol
                            
                            newcolname = f'{col_eoi} {col_suffix}'

                            df.rename(columns={col:newcolname}, inplace=True)
                            col = newcolname  # update col name to reflect change in header

                if do_units_inheaders:
                    df.rename(columns={col:(col + ' (' + units_to + ')')}, inplace=True)
                    col = col + ' (' + units_to + ')'  # update col name to reflect change in header
        
        return df


def getUnitConversionFactor(units_from:str,units_to:str):
    # returns factor to multiply by to convert from units_from to units_to
    if units_from == units_to:
        return 1
    elif units_from == 'ppm' and units_to == 'ppb':
        return 1000
    elif units_from == 'ppm' and units_to == '%':
        return 1/10000
    elif units_from == 'ppb' and units_to == 'ppm':
        return 1/1000
    elif units_from == 'ppb' and units_to == '%':
        return 1/10000000
    elif units_from == '%' and units_to == 'ppm':
        return 10000
    elif units_from == '%' and units_to == 'ppb':
        return 10000000
    else:
        raise Exception("Invalid unit conversion requested")        

def get_element_from_formula(compound:str):
    # Returns the first element in a chemical formula string e.g. 'Fe2O3' returns 'Fe' and 'H2O' returns 'H'
    lowercasecount = 0
    element = ''
    for char in compound:
        if char.isupper():
            if lowercasecount == 1:
                break
            else:
                element += char
        elif char.islower():
            element += char
            lowercasecount += 1
        else:
            break
    return element


def compound_to_element_factor(element_of_interest:str ,compound:str):
    """ Returns the conversion factor to apply to a compound concentration to get the 
        concentration of the element of interest (eoi), given the eoi and compound as strs.
        e.g. given 'Al' and 'Al2O3', returns 0.529251   """
    
    compound_mass = 0
    eoi_mass_single = 0
    eoi_mass = 0
    compound_stoich_dict = {}

    compound_stoich_dict = chemparse.parse_formula(compound)    # returns e.g. {'Al': 2, 'O': 3} from 'Al2O3' 

    masses = {'H': 1.00794, 'He': 4.002602, 'Li': 6.941, 'Be': 9.012182, 'B': 10.811, 'C': 12.0107, 'N': 14.0067,
                  'O': 15.9994, 'F': 18.9984032, 'Ne': 20.1797, 'Na': 22.98976928, 'Mg': 24.305, 'Al': 26.9815386,
                  'Si': 28.0855, 'P': 30.973762, 'S': 32.065, 'Cl': 35.453, 'Ar': 39.948, 'K': 39.0983, 'Ca': 40.078,
                  'Sc': 44.955912, 'Ti': 47.867, 'V': 50.9415, 'Cr': 51.9961, 'Mn': 54.938045,
                  'Fe': 55.845, 'Co': 58.933195, 'Ni': 58.6934, 'Cu': 63.546, 'Zn': 65.409, 'Ga': 69.723, 'Ge': 72.64,
                  'As': 74.9216, 'Se': 78.96, 'Br': 79.904, 'Kr': 83.798, 'Rb': 85.4678, 'Sr': 87.62, 'Y': 88.90585,
                  'Zr': 91.224, 'Nb': 92.90638, 'Mo': 95.94, 'Tc': 98.9063, 'Ru': 101.07, 'Rh': 102.9055, 'Pd': 106.42,
                  'Ag': 107.8682, 'Cd': 112.411, 'In': 114.818, 'Sn': 118.71, 'Sb': 121.760, 'Te': 127.6,
                  'I': 126.90447, 'Xe': 131.293, 'Cs': 132.9054519, 'Ba': 137.327, 'La': 138.90547, 'Ce': 140.116,
                  'Pr': 140.90465, 'Nd': 144.242, 'Pm': 146.9151, 'Sm': 150.36, 'Eu': 151.964, 'Gd': 157.25,
                  'Tb': 158.92535, 'Dy': 162.5, 'Ho': 164.93032, 'Er': 167.259, 'Tm': 168.93421, 'Yb': 173.04,
                  'Lu': 174.967, 'Hf': 178.49, 'Ta': 180.9479, 'W': 183.84, 'Re': 186.207, 'Os': 190.23, 'Ir': 192.217,
                  'Pt': 195.084, 'Au': 196.966569, 'Hg': 200.59, 'Tl': 204.3833, 'Pb': 207.2, 'Bi': 208.9804,
                  'Po': 208.9824, 'At': 209.9871, 'Rn': 222.0176, 'Fr': 223.0197, 'Ra': 226.0254, 'Ac': 227.0278,
                  'Th': 232.03806, 'Pa': 231.03588, 'U': 238.02891, 'Np': 237.0482, 'Pu': 244.0642, 'Am': 243.0614,
                  'Cm': 247.0703, 'Bk': 247.0703, 'Cf': 251.0796, 'Es': 252.0829, 'Fm': 257.0951, 'Md': 258.0951,
                  'No': 259.1009, 'Lr': 262, 'Rf': 267, 'Db': 268, 'Sg': 271, 'Bh': 270, 'Hs': 269, 'Mt': 278,
                  'Ds': 281, 'Rg': 281, 'Cn': 285, 'Nh': 284, 'Fl': 289, 'Mc': 289, 'Lv': 292, 'Ts': 294, 'Og': 294}
  
    try:
        eoi_mass_single = masses[element_of_interest]
    except KeyError:
        print(f'Error: Supplied Element of Interest ({element_of_interest}) for compound ({compound}) not found in molecular mass dictionary')
        return 1

    # Calculate actual EOI mass in case of multiple stoich of EOI in compound (e.g. Al2O3)
    try:
        eoi_mass = eoi_mass_single * compound_stoich_dict[element_of_interest]    # e.g. 26.9815386 * 2 = 53.9630772
    except KeyError:
        print(f'Error: Supplied Element of Interest ({element_of_interest}) not found in compound ({compound})')
        return 1

    for element, quantity in compound_stoich_dict.items():
        try:
            compound_mass += masses[element] * quantity
        except KeyError:
            (f'Error: Element ({element}) in Compound ({compound}) not found in molecular mass dictionary')
            compound_mass = 1
    
    return eoi_mass/compound_mass
    
def dfValueIsNaN(value):
    """ Pandas DataFrame NaN values are all type float.
        This function checks if a value is NaN, and returns True if it is, False if it isn't. """
    if type(value) != float:
        return False
    else:
        return math.isnan(value)




# Takes csv path and returns df, corrected for stupid multi-header bruker nonsense
def createDFfromCSV(csvpath:str): 
    print(f'Attempting to Create DataFrame from CSV at {csvpath}...')
    with open(csvpath,newline='') as f:
        universalHeaderRow = []
        currentSectionHeaderRow = []
        reader = csv.reader(f)
        allrowsasdicts = [] # list of dicts, each dict is a row. column headers are keys
        print(f'CSV opened, reading rows...')
        for row in reader:
            print(row)
            if (row == []) or (row[0] in ['¿','',' ','\n']):  # Blank or BOM row found. (row == [] is in case of completely blank row, as happens with some CSVs)
                print('blank/null/¿ row found, skipping...')
                #continue
            elif row[0] == 'File #':    # Header row found
                print('header row found')
                currentSectionHeaderRow = row
                if universalHeaderRow == []:
                    universalHeaderRow = row
                else:
                    if len(row) > len(universalHeaderRow) and all(item in row for item in universalHeaderRow): # checks all header values in universalHeaderRow are in row
                        universalHeaderRow = row
                    else: 
                        for element in row:
                            if element not in universalHeaderRow:
                                universalHeaderRow.append(element)

            else:   # Data row found
                print('data row found')
                rowdict = {}
                for header, element in zip(currentSectionHeaderRow,row):
                    rowdict[header] = element
                allrowsasdicts.append(rowdict)

    print(f'CSV read, creating DataFrame...')
    df = pd.DataFrame(allrowsasdicts)
    print(f'DataFrame created: {len(df)} rows x {len(df.columns)} columns')
    return df


def resource_path(relative_path):
    """ Get absolute path to resource, works for dev and for PyInstaller """
    base_path = getattr(sys, '_MEIPASS', os.path.dirname(os.path.abspath(__file__)))
    return os.path.join(base_path, relative_path)


def main():
    # create the application
    app = App()
    app.mainloop()

if __name__ == '__main__':
    main()

