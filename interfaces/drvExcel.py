import pandas as pd
from openpyxl import load_workbook
import datetime

## desired actions:
## open csv and create data frame
## add a value to a created data frame
## update existing excel
## close

## Constant Variables
csvPath="C:\DEV\coststracker\GastosMensuales2022.xlsx"
sheetName= "GastosVarios"

#Global Variables

#load excel file to the global variable
def openExcelFIle(path,sheetName):
    mainDataFrame = pd.read_excel(path, sheetName)
    return mainDataFrame

def updateExcel(path, data ,sheetName):
    global mainDataFrame
    # CONCAT TWO DATAFRAMES
    mainDataFrame=pd.concat([mainDataFrame,inputFrame],ignore_index=True)
    ## APPEND CSV
    writer = pd.ExcelWriter(path,engine="openpyxl", mode='a',if_sheet_exists="replace")
    data.to_excel(writer, sheet_name=sheetName,index=False)
    writer.close()
    return True

def infoToDataFrame(description="TestExpense",cuantity=99,extra=""):
    #receives info, set timestamp, and return dataframe
    x = datetime.datetime.now()
    output=pd.DataFrame({"Date":[x],"Description":description,"Cuantity":cuantity,"Extra":extra})
    return output

# ------------------------------ sequence needed to use this module ------------------------------- #
## load main data frame
mainDataFrame=openExcelFIle(csvPath)
## create de data Frame and update main file
inputFrame=infoToDataFrame(Description="Kebab",Cuantity=10,Extra="")
updateExcel(csvPath,inputFrame,sheetName)

