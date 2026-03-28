from fastapi import FastAPI, File , UploadFile , HTTPException 
import pandas as pd 
import io 
from typing import Any 

#-----------APP SETUP------------------------

app = FastAPI(
    title = "CSV Data Analysis API", 
    description= "Upload a CSV file and receive summary statistics as JSON", 
    version= "1.0.0"
)
#Creates the FastAPI application 
#title, description show up in /docs

#------------------Root Endpoint-------------------------------

@app.get("/")
def read_root(): 
    """Health check = confirms API is running."""
    return {
        "message": "CSV Analysis API is running." , 
        "usage" : "POST a CSV file to /analyse to get statistics"
    }

#-----------------Analysis Endpoint------------------------------

@app.post("/analyse")
async def analyse_csv(file: UploadFile = File(...)):
    """
    Accept a CSV file and return the summary statistics. 
    
    Args: 
        file: CSV file uploaded via multipart/form-data

    Returns: 
        JSON with shape, column info, numeric stats, null counts
    """

    #-----STEP 1: Validate the file type -------------------------

    if not file.filename.endswith(".csv"): 
        raise HTTPException(
            status_code = 400, 
            detail = "Only .csv files are accepted"
        )
    
    #-----STEP 2: Read the uploaded file into a Pandas DataFrame--
    try: 
        contents = await file.read()

        df = pd.read_csv(io.StringIO(contents.decode("utf-8")))

    except Exception as e:
        raise HTTPException(
            status_code = 422, 
            detail = f"Could not parse CSV: {str(e)}"
        )
    

    #-----STEP 3: Basic Shape Info---------------------------------

    rows, cols = df.shape

     #-----STEP 4: Column level Info---------------------------------


    column_info = {}
    for col in df.columns: 
        column_info[col] = {
            "dtype": str(df[col].dtype), 
            "null_count": int(df[col].isnull().sum()),
            "null_percent": round(
                float(df[col].isnull().mean() * 100 ), 2
            ), 
            "unique_count": int(df[col].nunique()),
        }

    #----STEP 5: Numeric Statistics ------------------------------

    numeric_cols = df.select_dtypes(include=["number"]).columns.tolist()

    numeric_stats: dict[str , Any] = {}

    if numeric_cols: 
        stats_df = df[numeric_cols].describe()

        for col in numeric_cols: 
            numeric_stats[col] = {
                "mean":   round(float(stats_df.loc["mean", col]), 4),
                "median": round(float(df[col].median()), 4), 
                "std":    round(float(stats_df.loc["std", col]), 4), 
                "min":    round(float(stats_df.loc["min", col]), 4), 
                "max":    round(float(stats_df.loc["max", col]), 4), 
                "q25":    round(float(stats_df.loc["25%", col]), 4), 
                "q75":    round(float(stats_df.loc["75%", col]), 4),
            }

    #------STEP 6: Categorical Columns and their values counts---------
    categorical_cols = df.select_dtypes(include=["object", "string"]).columns.tolist()

    categorical_stats: dict[str, Any] = {}

    for col in categorical_cols: 
        value_counts = df[col].value_counts().head(5)

        categorical_stats[col] = { 
            "top_values" : value_counts.to_dict(),
        }

    #-----STEP 7: Assemble and return response-----------------------

    return { 
        "filename": file.filename, 
        "shape": {
            "rows" : rows, 
            "columns" : cols
        }, 
        "columns": column_info, 
        "numeric_statistics": numeric_stats, 
        "categorical_statistics": categorical_stats, 
        "data_quality": {
            "total_nulls": int(df.isnull().sum().sum()),
            "complete_rows": int(df.dropna().shape[0]), 
            "completeness_percent":round(
                float(df.dropna().shape[0] / rows * 100) , 2
            )
        }

                }


