# def get_element_from_formula(formula):
#     """
#     Takes a chemical formula for an oxide or a sulphide (e.g. 'MgO' or 'MgS' or 'Al2O3')
#     and returns a string containing the symbol for the element of that oxide or sulphide (e.g. 'Mg' or 'Al').
#     """
#     elements = ''
#     for char in formula:
#         if char.isupper():
#             elements += char
#             if len(elements) == 1 and not formula.startswith(elements):
#                 # Handle single-letter element symbols that are not at the beginning of the formula
#                 elements += formula.split(elements)[0][-1]
#                 break
#             elif elements.isalpha() and len(elements) > 1:
#                 break
#         elif char.isdigit() and elements:
#             # Handle formulas that end in a number
#             break

#     if not elements.isalpha() or len(elements) > 2:
#         # Handle formulas with multiple elements
#         for i, char in enumerate(formula):
#             if char.isupper():
#                 if formula[i:i+2].isalpha() and formula[i:i+2] != elements:
#                     elements = formula[i:i+2]
#                     break
#                 else:
#                     elements = char
#             elif char.isdigit() or char.islower():
#                 break

#     return elements

def get_element_from_formula(formula:str):
    element = ''
    lowercasecount = 0
    for char in formula:
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

            
print(get_element_from_formula('MgO'))      # Output: 'Mg'
print(get_element_from_formula('MgS'))      # Output: 'Mg'
print(get_element_from_formula('Al2O3'))    # Output: 'Al'
print(get_element_from_formula('V2O5'))     # Output: 'V'
print(get_element_from_formula('K2O'))      # Output: 'K'
print(get_element_from_formula('H2O'))      # Output: 'H'
print(get_element_from_formula('NaCl'))     # Output: 'Na'


import chemparse

#element_of_interest = get_element_from_formula(compound)    # Assumes first element in formula is the one of interest

def compound_to_element_factor(element_of_interest:str ,compound:str):

    compound_mass = 0
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
    
    




print(compound_to_element_factor('Mg','Al2O3'))
print((26.9815386+26.9815386)/(26.9815386+26.9815386+15.9994+15.9994+15.9994))

