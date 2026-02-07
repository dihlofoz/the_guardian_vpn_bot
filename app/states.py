from aiogram.fsm.state import State, StatesGroup

class CreatePromo(StatesGroup):
    waiting_for_code = State()
    waiting_for_type = State()
    waiting_for_value = State()   # либо % скидки, либо кол-во дней
    waiting_for_max_uses = State()

class PromoActivate(StatesGroup):
    waiting_for_promo = State()

class ConvertRPStates(StatesGroup):
    choose_resource = State()      
    choose_amount_type = State()   
    enter_custom_amount = State()

class RpUpgradeFSM(StatesGroup):
    choosing_resource = State()
    choosing_amount = State()
