from fastapi import FastAPI,HTTPException
import os
import joblib
from typing import Optional

app = FastAPI(
    title="Customer Churn Prediction API",
    description= "An API to prdict customer churn using machine"
)

@app.get('/') # this is get method and root endpoint
def greet():
    return {'message':'whats up'}

MODEL_PATH = 'best_balanced_churn_model.pkl' #this is a constant variable


if not os.path.exists(MODEL_PATH):
    raise FileNotFoundError(f'model file not found at {MODEL_PATH}')

model = joblib.load(MODEL_PATH) #Load the model at startup

#Input schema
#PYDANTIC MODEL

from pydantic import BaseModel,Field,field_validator

class CustomerData(BaseModel):
    Gender:str = Field(...,example='Male') #... means compulsary
    Age:int = Field(...,ge=18,le=100,example=45)
    Tenure:int = Field(...,ge=0,le=100,example=12)
    Services_Subscribed:int = Field(...,ge=0,le=10,example=3)
    Contract_Type:str = Field(...,example='Month-to-month')
    MonthlyCharges:float = Field(...,ge=0,example=70.5)
    TotalCharges:float = Field(...,ge=0,example=500.75)
    TechSupport:str = Field(...,example='Yes')
    OnlineSecurity:str = Field(...,example='Yes')
    InternetService:str = Field(...,example='Fiber optic')

    @field_validator('Gender')
    @classmethod
    def validate_gender(cls,value):
        allowed = {'Male','Female'}
        if value not in allowed:
            raise ValueError(f'Gender must be {allowed}')
        return value
    
    @field_validator('Contract_Type')
    @classmethod
    def validate_contract_type(cls,value):
        allowed = {'Month-to-month','One year','Two year'}
        if value not in allowed:
            raise ValueError(f'Contract_Type must be {allowed}')
        return value
    
    @field_validator('TechSupport','OnlineSecurity')
    @classmethod
    def validate_tech_support(cls,value):
        allowed = {'Yes','No'}
        if value not in allowed:
            raise ValueError(f'Tech_Support must be {allowed}')
        return value
    
    @field_validator('InternetService')
    @classmethod
    def validate_internet_service(cls,value):
        allowed = {'DSL','Fiber optic','No'}
        if value not in allowed:
            raise ValueError(f'Internet_service must be {allowed}')
        return value
    


#output Schema
class PredictionResponse(BaseModel):
    churn_prediction:int
    churn_label:str
    churn_probability:Optional[float]

#prediction endpoint
import pandas as pd

@app.post('/Predict',response_model=PredictionResponse)
def predict(customer:CustomerData):
    #conver request to dataframe
    try:

        input_df = pd.DataFrame([customer.model_dump()])

        #Model prediction
        prediction = model.predict(input_df)[0]

        #Probability
        probability = None
        if hasattr(model,'predict_proba'):
            probability = model.predict_proba(input_df)[0][1]

        return PredictionResponse(
            churn_prediction=prediction,
            churn_label='Churn'if prediction ==1 else 'Not Churn',
            churn_probability=probability
        )
    except Exception as e:
        raise HTTPException(status_code=500,detail=str(e))