from openpyxl import Workbook, load_workbook

wb = load_workbook('exemplo.xlsx')
sheet = wb["Sheet1"]

formula = "=SUM(C2:C7)"
sheet['C8'] = formula
wb.save("formula.xlsx")


from openpyxl.formula.translate import Translator
sheet['D8'] = Translator(formula, origin="C8").translate_formula("D8")
sheet['D8'].value

wb.save("formula.xlsx")


# Você pode consultar as fórmulas disponíveis aqui
from openpyxl.utils import FORMULAE
FORMULAE
