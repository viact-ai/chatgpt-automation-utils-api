const zip = (...arr) =>
  Array(Math.max(...arr.map((a) => a.length)))
    .fill()
    .map((_, i) => arr.map((a) => a[i]));

// Ref: https://www.labnol.org/convert-column-a1-notation-210601
const getA1Notation = (row, column) => {
  /**
   *
   * @param {number} row - The row number of the cell reference. Row 1 is row number 0.
   * @param {number} column - The column number of the cell reference. A is column number 0.
   * @returns {string} Returns a cell reference as a string using A1 Notation
   *
   * @example
   *
   *   getA1Notation(2, 4) returns "E3"
   *   getA1Notation(2, 4) returns "E3"
   *
   */
  const a1Notation = [`${row + 1}`];
  const totalAlphabets = "Z".charCodeAt() - "A".charCodeAt() + 1;
  let block = column;
  while (block >= 0) {
    a1Notation.unshift(
      String.fromCharCode((block % totalAlphabets) + "A".charCodeAt())
    );
    block = Math.floor(block / totalAlphabets) - 1;
  }
  return a1Notation.join("");
};

const fromA1Notation = (cell) => {
  /**
   *
   * @param {string} cell -  The cell address in A1 notation or a column letter or a row number
   * @returns {object} The row number and column number of the cell (0-based), or null for the missing value
   *
   * @example
   *
   *   fromA1Notation("A2") returns {row: 1, column: 0}
   *   fromA1Notation("D") returns {row: null, column: 3}
   *   fromA1Notation("15") returns {row: 14, column: null}
   *
   */
  if (typeof cell != "string") {
    cell = String(cell);
  }
  if (/^[A-Z]+$/.test(cell.toUpperCase())) {
    const characters = "Z".charCodeAt() - "A".charCodeAt() + 1;
    let column = 0;
    cell
      .toUpperCase()
      .split("")
      .forEach((char) => {
        column *= characters;
        column += char.charCodeAt() - "A".charCodeAt() + 1;
      });
    return { row: null, column: column };
  } else if (/^\d+$/.test(cell)) {
    return { row: parseInt(cell, 10), column: null };
  } else {
    const [, columnName, row] = cell.toUpperCase().match(/([A-Z]+)([0-9]+)/);
    const characters = "Z".charCodeAt() - "A".charCodeAt() + 1;
    let column = 0;
    columnName.split("").forEach((char) => {
      column *= characters;
      column += char.charCodeAt() - "A".charCodeAt() + 1;
    });
    return { row: parseInt(row, 10), column: column };
  }
};

function setExecResult(sheet, status, cell = EXEC_RESULT_CELL) {
  sheet.getRange(cell.row, cell.col).setValue(status);
}

function setStatus(sheet, status, cell = TRIGGER_ACTION_CELL) {
  sheet.getRange(cell.row, cell.col).setValue(status);
}

function convert2datestr(date) {
  return Utilities.formatDate(date, "GMT+0", "yyyy/MM/dd");
}

function switchFunction(sheet, fname, functions, paramsRange = PARAMS_RANGE) {
  if (!(fname in functions)) {
    return CODE_INVALID_PARAM;
  }

  sheet
    .getRange(paramsRange.row, paramsRange.col, 2, sheet.getLastColumn())
    .clear();

  let fParams = functions[fname];
  let startCol = paramsRange.col;
  let startRow = paramsRange.row;
  Object.entries(fParams).forEach((p) => {
    let k = p[0];
    let v = p[1];
    if (v == "") {
      let r = sheet.getRange(startRow, startCol, 1, 1);
      r.setValues([[k]]);
      r.setFontSize(12);
    } else {
      let r = sheet.getRange(startRow, startCol, 2, 1);
      r.setValues([[k], [v]]);
      r.setFontSize(12);
    }
    startCol++;
  });
}

function parseValue(v) {
  let type = typeof v;
  if (type != "string") {
    return v;
  }

  let _v = v.toLowerCase().trim();
  if (_v == "true") return true;
  if (_v == "false") return false;
  if (_v == "null") return null;
  if (_v == "undefined") return undefined;
  if (!isNaN(_v)) return Number(_v);
  return v;
}

function readFunctionParams(sheet, paramsRange = PARAMS_RANGE) {
  let params = {};
  for (let col = 1; col <= sheet.getLastColumn(); col++) {
    let paramName = sheet
      .getRange(paramsRange.row, col + paramsRange.col - 1)
      .getValue();
    if (paramName == "") continue;
    let value = sheet
      .getRange(paramsRange.row + 1, col + paramsRange.col - 1)
      .getValue();
    if (value == "") value = null;
    params[paramName] = parseValue(value);
  }
  return params;
}

function readAllFunctionsFromSheet(sheetName = EMAIL_FUNCTIONS_SHEET) {
  let spreadsheet = SpreadsheetApp.getActive();
  let sheet = spreadsheet.getSheetByName(sheetName);

  let startRow = 2;
  let startCol = 1;
  let endRow = sheet.getLastRow();
  let endCol = sheet.getLastColumn();

  let result = {};

  // cols: ['name', 'desc', 'param', 'param_desc', 'default']
  let i = startRow;
  while (i <= endRow) {
    let range = sheet.getRange(i, startCol);
    if (range.isPartOfMerge()) {
      let mergedRange = range.getMergedRanges()[0];
      let lastRow = mergedRange.getLastRow();

      let fname = mergedRange.getValue();
      result[fname] = {};

      let params = sheet.getRange(i, 3, lastRow - i + 1, 2).getValues();
      params.forEach((p) => {
        result[fname][p[0]] = p[1];
      });

      i = lastRow + 1;
    }
  }

  return result;
}

function execFunction(sheet, fname, fParams, action) {
  console.log(
    `Execute function ${fname} with params ${Object.entries(
      fParams
    )} and action ${action}`
  );

  if (fname == F_CRAWL_EMAIL) {
    if (action == A_RUN) {
      crawlEmail(sheet, fParams);
    } else if (action == A_CLEAR_RESULT) {
      clearEmailCrawled(sheet, fParams);
    }
    return CODE_NO_ERROR;
  }

  if (fname == F_GPT_PROMPT) {
    runGPTPrompt(sheet, fParams, action == A_RUN_CUSTOM_PROMPT);
    return CODE_NO_ERROR;
  }

  if (fname == F_SEND_EMAIL && action == A_RUN) {
    sendEmail(sheet, fParams);
    return CODE_NO_ERROR;
  }

  if (fname == F_QUESTION_ANSWERING && action == A_RUN) {
    questionAnswering(sheet, fParams);
    return CODE_NO_ERROR;
  }

  return CODE_NO_ERROR;
}

function execFollowUpSheetFunction(sheet, fname, fParams, action) {
  console.log(
    `Execute function ${fname} with params ${Object.entries(
      fParams
    )} and action ${action}`
  );

  if (fname == F_FOLLOW_UP_FETCH_EMAIL && action == A_RUN) {
    followUpFetchEmailFromInbox(sheet, fParams);
    return CODE_NO_ERROR;
  }

  if (fname == F_FOLLOW_UP_WRITE_EMAIL && action == A_RUN) {
    followUpWriteEmail(sheet, fParams);
    return CODE_NO_ERROR;
  }

  if (fname == F_FOLLOW_UP_SEND_EMAIL && action == A_RUN) {
    followUpSendEmail(sheet, fParams);
    return CODE_NO_ERROR;
  }
}

function execWebRetrievalSheetFunction(sheet, fname, fParams, action) {
  console.log(
    `Execute function ${fname} with params ${Object.entries(
      fParams
    )} and action ${action}`
  );

  if (fname == F_FETCH_GOOGLE_RESULT && action == A_RUN) {
    websheetFetchGoogleResult(sheet, fParams);
    return CODE_NO_ERROR;
  }

  if (fname == F_QUESTION_ANSWERING && action == A_RUN) {
    webQuestionAnswering(sheet, fParams);
    return CODE_NO_ERROR;
  }
}

function flatten1DArray(arr) {
  return arr.map((e) => e[0]);
}

function parseDateTime(datetimeString) {
  let date = new Date(Date.parse(datetimeString));

  return date;
}

function isCompanyEmail(email) {
  for (let e of COMPANY_EMAIL_SUFFIX) {
    if (email.includes(e)) {
      return true;
    }
  }
  return false;
}

function getEmailFromFromHeader(fromHeader) {
  let emailRegex = /([^\s<]+@[^\s>]+)/; // regular expression to match email address with or without name
  let emailMatch = emailRegex.exec(fromHeader);
  let email = emailMatch[1];
  return email;
}

function getTriggerTypeFromEvent(e) {
  if (!e) return;
  let uid = e.triggerUid;
  if (uid) {
    let trigger = ScriptApp.getProjectTriggers().find(
      (trigger) => trigger.getUniqueId() === uid
    );

    if (trigger) {
      let triggerType = trigger.getEventType();
      console.info(`TriggerType: ${triggerType}`);
      return triggerType.toString();
    }
  }
}
