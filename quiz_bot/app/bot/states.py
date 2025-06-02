from aiogram.fsm.state import State, StatesGroup

class SurveyStates(StatesGroup):
    company_name = State()
    position_and_contacts = State()
    implementation_stage = State()
    pain_points = State()
    pain_points_details = State()
    main_barrier = State()
    direct_replacement = State()
    direct_replacement_details = State()
    pilot_testing = State()
    software_classes = State()
    software_classes_details = State()
    event_interest = State()
    solution_help = State()