from app.api.route_enterprise import router as enterprise_router
from app.api.route_respondent import router as respondent_router
from app.api.route_survey import router as survey_router
from app.api.route_question import router as question_router
from app.api.route_survey_answer import router as survey_answer_router
from app.api.route_software_category import router as software_category_router

from app.db import init_db
from fastapi import FastAPI
import uvicorn

from app import on_startup, on_shutdown

app = FastAPI(on_startup=[on_startup, init_db],
               on_shutdown=[on_shutdown])

app.include_router(enterprise_router)
app.include_router(respondent_router)
app.include_router(survey_router)
app.include_router(question_router)
app.include_router(survey_answer_router)
app.include_router(software_category_router)

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
