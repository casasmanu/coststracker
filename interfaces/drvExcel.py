import pandas as pd
from openpyxl import load_workbook
import datetime
import logging

## desired actions:
## open csv and create data frame
## add a value to a created data frame
## update existing excel
## close

## Constant Variables
csvPath="C:\DEV\coststracker\GastosMensuales2022.xlsx"
sheetName= "GastosVarios"

#Global Variables

logger = logging.getLogger(__name__)

#load excel file to the global variable
def openExcelFIle(path,sheetName):
    try:
        mainDataFrame = pd.read_excel(path, sheetName)
    except:
        logger.error("Error while trying to read the sheet "+sheetName)
        mainDataFrame=0
    
    return mainDataFrame

def updateExcel(path="C:\DEV\coststracker\GastosMensuales2022.xlsx", sheetName="GastosVarios",sheet_columns=["Description","Cuantity","Extra"],sheet_data=["TestExpense",99,""]):
    #receives info, set timestamp, and return dataframe
    x = datetime.datetime.now()
    tmpData={}
    i=0

    if sheetName=="GastosVarios":
        tmpData.update({"Date":[x]})

    for column in sheet_columns:
        tmpData.update({column:[sheet_data[i]]})
        i+=1

    data=pd.DataFrame.from_dict(tmpData)

    mainDataFrame=openExcelFIle(path,sheetName)

    # CONCAT TWO DATAFRAMES
    mainDataFrame=pd.concat([mainDataFrame,data],ignore_index=True)
    ## APPEND CSV
    writer = pd.ExcelWriter(path,engine="openpyxl", mode='a',if_sheet_exists="replace")
    mainDataFrame.to_excel(writer, sheet_name=sheetName,index=False)

    writer.close()
    
    return True

def readData(path="C:\DEV\coststracker\GastosMensuales2022.xlsx", sheetName= "EDEKA"):
    # read desired excel file data
    mainDataFrame=openExcelFIle(path,sheetName)
    output=mainDataFrame.__str__()
    return output


#print(readData())

#updateExcel(sheetName="EDEKA",sheet_columns=["Producto","Precio","Calidad"],sheet_data=["pera",4.5,"Safa"])
#updateExcel()
# def infoToDataFrame(description="TestExpense",cuantity=99,extra=""):
#     #receives info, set timestamp, and return dataframe
#     x = datetime.datetime.now()
#     output=pd.DataFrame({"Date":[x],"Description":description,"Cuantity":cuantity,"Extra":extra})
#     return output

# ------------------------------ sequence needed to use this module ------------------------------- #
## load main data frame
#mainDataFrame=openExcelFIle(csvPath)
## create de data Frame and update main file
#inputFrame=infoToDataFrame(Description="Kebab",Cuantity=10,Extra="")
#updateExcel(csvPath,inputFrame,sheetName)

