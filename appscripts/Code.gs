function main() {
  let spreadsheet = SpreadsheetApp.getActiveSpreadsheet(); // trick to grant app permission
}

function _onEditMailSheet(e) {
  let sheet = e.range.getSheet();

  let actionRow = e.range.getRow();
  let actionCol = e.range.getColumn();

  // Get function name
  let fname = sheet
    .getRange(FUNC_NAME_CELL.row, FUNC_NAME_CELL.col)
    .getValue()
    .trim();
  let fParams = readFunctionParams(sheet);

  if (
    actionRow == TRIGGER_FUNC_CHANGE_CELL.row &&
    actionCol == TRIGGER_FUNC_CHANGE_CELL.col
  ) {
    let functions = readAllFunctionsFromSheet();
    switchFunction(sheet, fname, functions);
    return CODE_NO_ERROR;
  }

  if (
    actionRow == TRIGGER_ACTION_CELL.row &&
    actionCol == TRIGGER_ACTION_CELL.col
  ) {
    let action = e.value;
    return execFunction(sheet, fname, fParams, action);
  }
}

function _onFollowUpSheetEdit(e) {
  let sheet = e.range.getSheet();

  let actionRow = e.range.getRow();
  let actionCol = e.range.getColumn();

  // Get function name
  let fname = sheet
    .getRange(FOLLOW_UP_FUNC_NAME_CELL.row, FOLLOW_UP_FUNC_NAME_CELL.col)
    .getValue()
    .trim();
  let fParams = readFunctionParams(sheet, FOLLOW_UP_PARAMS_RANGE);

  if (
    actionRow == FOLLOW_UP_TRIGGER_ACTION_CELL.row &&
    actionCol == FOLLOW_UP_TRIGGER_ACTION_CELL.col
  ) {
    let action = e.value;
    return execFollowUpSheetFunction(sheet, fname, fParams, action);
  }
}

function _onWebRetrievalSheetEdit(e) {
  let sheet = e.range.getSheet();

  let actionRow = e.range.getRow();
  let actionCol = e.range.getColumn();

  // Get function name
  let fname = sheet
    .getRange(WEB_FUNC_NAME_CELL.row, WEB_FUNC_NAME_CELL.col)
    .getValue()
    .trim();
  let fParams = readFunctionParams(sheet, WEB_PARAMS_RANGE);

  if (
    actionRow == WEB_TRIGGER_FUNC_CHANGE_CELL.row &&
    actionCol == WEB_TRIGGER_FUNC_CHANGE_CELL.col
  ) {
    let functions = readAllFunctionsFromSheet(WEB_FUNCTIONS_SHEET);
    switchFunction(sheet, fname, functions, WEB_PARAMS_RANGE);
    return CODE_NO_ERROR;
  }

  if (
    actionRow == WEB_TRIGGER_ACTION_CELL.row &&
    actionCol == WEB_TRIGGER_ACTION_CELL.col
  ) {
    let action = e.value;
    return execWebRetrievalSheetFunction(sheet, fname, fParams, action);
  }
}

function myOnEdit(e) {
  let sheet = e.range.getSheet();

  let sheetName = sheet.getSheetName();

  switch (sheetName) {
    case TRIGGER_SHEET_NAME:
      setStatus(sheet, S_TRIGGERED);
      _onEditMailSheet(e);
      setStatus(sheet, S_COMPLETED);
      break;

    case WEB_TRIGGER_SHEET_NAME:
      setStatus(sheet, S_RUNNING);
      _onWebRetrievalSheetEdit(e);
      setStatus(sheet, S_COMPLETED);
      break;

    default:
      let isFollowUpSheet = sheetName
        .toLowerCase()
        .includes(FOLLOW_UP_PREFIX_SHEET_NAME);
      if (!isFollowUpSheet) {
        console.log(`Sheet ${sheetName} is not triggered`);
        return;
      }

      setStatus(sheet, S_RUNNING, FOLLOW_UP_TRIGGER_ACTION_CELL);
      _onFollowUpSheetEdit(e);
      setStatus(sheet, S_COMPLETED, FOLLOW_UP_TRIGGER_ACTION_CELL);
  }
}
