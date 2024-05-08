MAX_RESULT_PAGES = 100

MAX_MONTHLY_VISITS = 100
MAX_DAILY_MESSAGES = 100
MAX_WEEKLY_CONNECTIONS = 100

DATE_FORMAT = "%Y-%m-%d %H:%M:%S"

ERR_NO_USERNAME = "¡Introduce tu nombre de usuario!"
ERR_NO_PASSWORD = "¡Introduce tu contraseña!"
ERR_NO_NEW_PASSWORD = "¡Introduce tu nueva contraseña!"
ERR_NO_CONFIRM_PASSWORD = "¡Confirma tu nueva contraseña!"
ERR_USER_OR_PASS_WRONG = "¡Usuario o contraseña incorrectos!"
ERR_USER_ALREADY_EXISTS = "¡Este nombre de usuario ya existe!"
ERR_CONFIRM_PASSWORD = "¡Confirma tu contraseña!"
ERR_PASSWORDS_NOT_MATCH = "¡Las contraseñas no coinciden!"
ERR_CORPORATE_EMAIL = "¡Utiliza tu correo corporativo como nombre de usuario!"
ERR_EMPTY_MESSAGE = "¡Introduce un mensaje!"
ERR_NO_LINKEDIN_USER = "¡Introduce un nombre de usuario de LinkedIn!"
ERR_NO_LINKEDIN_PASS = "¡Introduce una contraseña de LinkedIn!"
ERR_LINKEDIN_LOGIN_WRONG = "¡Usuario o contraseña de LinkedIn incorrectos!"
ERR_NO_SHOTS_LEFT = "¡No tienes suficientes acciones restantes!"
ERR_NUMERICAL_SHOTS = "Por favor, introduce un número entre 1 y "
ERR_RANGE_INT = "¡Introduce un entero positivo!"

ACTION_VISIT_PROFILES = "visitar perfiles"
ACTION_WRITE_MESSAGES = "escribir mensajes"
ACTION_SEND_CONNECTIONS = "enviar invitaciones"

ACTION_PROFILE_VISITED = 'Perfil visitado'
ACTION_MESSAGE_WRITTEN = 'Mensaje enviado'
ACTION_CONNECTION_SENT = 'Solicitud de conexión'

URL_LINKEDIN_HOME = "https://www.linkedin.com"
URL_LINKEDIN_LOGIN = "https://www.linkedin.com/uas/login-submit"
URL_LINKEDIN_SEARCH_PEOPLE = "https://www.linkedin.com/search/results/people/?keywords="

ELEMENT_SESSION_KEY = "//*[@id='session_key']"
ELEMENT_SESSION_PASSWORD = "//*[@id='session_password']"
ELEMENT_BUTTON_SUBMIT = "//button[@type='submit']"
ELEMENT_EMPTY_STATE = '//h2[contains(@class, "artdeco-empty-state__headline")]'
ELEMENT_PAGE_PROFILES = '//*[@class="app-aware-link  scale-down "]'
ELEMENT_BUTTON_CONNECT = "Conectar"
ELEMENT_BUTTON_SEND_NOW = "//button[@aria-label='Enviar ahora']"

DEEP_2_3 = '&network=%5B"S"%2C"O"%5D'
DEEP_1 = '&network=%5B"F"%5D'
DEEP_2 = '&network=%5B"S"%5D'

PATH_WELCOME_NAME = "/html/body/div[6]/div[3]/div/div/div[2]/div/div/div/div/div[1]/div[1]/a/div[2]"
PATH_NUMBER_RESULTS = "//div[3]/div[2]/div/div[1]/main/div/div/div[1]/h2"

OUTPUT_CSV = "perfiles.csv"