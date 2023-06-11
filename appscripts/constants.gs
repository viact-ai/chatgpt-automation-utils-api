const TRIGGER_SHEET_NAME = "Email";

const WEB_TRIGGER_SHEET_NAME = "Web retrieval";

const F_CRAWL_EMAIL = "CRAWL_EMAIL";
const F_GPT_PROMPT = "GPT_PROMPT";
const F_SEND_EMAIL = "SEND_EMAIL";
const F_QUESTION_ANSWERING = "QUESTION_ANSWERING";

const F_FOLLOW_UP_FETCH_EMAIL = "FETCH_EMAIL";
const F_FOLLOW_UP_WRITE_EMAIL = "WRITE_FOLLOW_UP";
const F_FOLLOW_UP_SEND_EMAIL = "SEND_FOLLOW_UP";

const F_FETCH_GOOGLE_RESULT = "GOOGLE_SEARCH";

const A_RUN = "RUN";
const A_CLEAR_RESULT = "CLEAR_RESULT";
const A_RUN_CUSTOM_PROMPT = "RUN_CUSTOM_PROMPT";

const FUNC_NAME_CELL = { row: 1, col: 2 };
const PARAMS_RANGE = { row: 2, col: 2 };
const TRIGGER_ACTION_CELL = { row: 6, col: 2 };
const TRIGGER_FUNC_CHANGE_CELL = { row: 1, col: 2 };
const EXEC_RESULT_CELL = { row: 7, col: 2 };

const EMAIL_FUNCTIONS_SHEET = "Email functions";

const FOLLOW_UP_PREFIX_SHEET_NAME = "follow-up";
const FOLLOW_UP_FUNC_NAME_CELL = { row: 2, col: 2 };
const FOLLOW_UP_TRIGGER_ACTION_CELL = { row: 6, col: 2 };
const FOLLOW_UP_TRIGGER_FUNC_CHANGE_CELL = { row: 2, col: 2 };
const FOLLOW_UP_PARAMS_RANGE = { row: 3, col: 2 };
const FOLLOW_UP_EXEC_RESULT_CELL = { row: 7, col: 2 };
const FOLLOW_UP_TRIGGER_CHANGE_CELL = { row: 1, col: 2 };

const WEB_FUNCTIONS_SHEET = "Web functions";
const WEB_FUNC_NAME_CELL = { row: 1, col: 2 };
const WEB_PARAMS_RANGE = { row: 2, col: 2 };
const WEB_TRIGGER_ACTION_CELL = { row: 6, col: 2 };
const WEB_TRIGGER_FUNC_CHANGE_CELL = { row: 1, col: 2 };
const WEB_EXEC_RESULT_CELL = { row: 7, col: 2 };

const S_COMPLETED = "COMPLETED";
const S_TRIGGERED = "TRIGGERED";
const S_RUNNING = "RUNNING";
const S_ERROR = "ERROR";
const S_CRAWLING_EMAIL = "CRAWLING_EMAIL";
const S_CRAWLING_EMAIL_DONE = "CRAWLING_EMAIL_DONE";
const S_INVALID_PARAM = "INVALID_PARAM";

const CODE_NO_ERROR = 0;
const CODE_INVALID_PARAM = 1;
const CODE_ERROR = 2;

const API_BASE_URL = "https://chatgpt-automation-api.viact.net";

const COMPANY_EMAIL_SUFFIX = ["@viact.ai", "@viact.net"];
