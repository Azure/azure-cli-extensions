from knack.prompting import prompt_y_n

def get_user_confirmation(message, yes=False):
    if yes:
        return True
    if not prompt_y_n(message):
        return False
    return True