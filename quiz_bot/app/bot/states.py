from aiogram.fsm.state import State, StatesGroup

class SurveyStates(StatesGroup):
    company_name = State()
    position = State()
    phone_number = State()
    email = State()
    implementation_stage = State()
    pain_points = State()
    pain_points_page = State()  # State for tracking pagination
    pain_points_selection = State()  # New state for selecting an option after pagination
    pain_points_other = State()  # New state for custom "Other" option
    pain_points_functionality_details = State()  # Follow-up for functionality
    pain_points_integration_details = State()  # Follow-up for integration
    pain_points_personnel_details = State()  # Follow-up for personnel
    pain_points_compatibility_details = State()  # Follow-up for compatibility
    pain_points_costs_details = State()  # Follow-up for costs
    pain_points_support_details = State()  # Follow-up for support
    main_barrier = State()
    direct_replacement = State()
    direct_replacement_details = State()
    pilot_testing = State()
    software_classes = State()
    software_classes_details = State()
    event_interest = State()
    solution_help = State()