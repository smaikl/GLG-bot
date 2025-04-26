from aiogram.fsm.state import State, StatesGroup


class DeliveryStates(StatesGroup):
    waiting_for_stage = State()


class EditProfileStates(StatesGroup):
    choosing_field = State()
    entering_new_value = State()

class RegistrationStates(StatesGroup):
    waiting_for_role = State()
    waiting_for_name = State()
    waiting_for_phone = State()
    waiting_for_email = State()
    waiting_for_company = State()
    confirmation = State()


class OrderCreationStates(StatesGroup):
    waiting_for_cargo_type = State()
    waiting_for_weight = State()
    waiting_for_dimensions = State()
    waiting_for_pickup_address = State()
    waiting_for_delivery_address = State()
    waiting_for_pickup_date = State()
    waiting_for_comment = State()
    waiting_for_documents = State()
    confirmation = State()


class OrderSearchStates(StatesGroup):
    waiting_for_filter = State()
