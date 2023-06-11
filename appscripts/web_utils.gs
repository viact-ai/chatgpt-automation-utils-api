function websheetClearResult(sheet, params = {}) {
  let { resultRow, resultCol } = params;

  if (typeof resultRow != "number") {
    return "resultRow must be a number";
  }
  if (!Number.isInteger(resultRow)) {
    return "resultRow must be an integer";
  }

  if (resultCol == null) {
    return "resultCol must not be empty";
  }
  resultCol = fromA1Notation(resultCol);
  if (resultCol.column == null) {
    return "resultCol is not a valid column";
  }
  resultCol = resultCol.column;

  let nResult = sheet.getRange(resultRow, resultCol + 1).getValue();
  if (isNaN(nResult)) {
    return "notthing to clear";
  }

  let lastCol = sheet.getLastColumn();
  sheet.getRange(resultRow, resultCol, nResult + 1, lastCol).clear();
  console.info("Clear crawled result completed");
}

function websheetFetchGoogleResult(sheet, params = {}) {
  let { resultRow, resultCol, keyword, getContent } = params;

  if (typeof resultRow != "number") {
    return "resultRow must be a number";
  }
  if (!Number.isInteger(resultRow)) {
    return "resultRow must be an integer";
  }

  if (resultCol == null) {
    return "resultCol must not be empty";
  }
  resultCol = fromA1Notation(resultCol);
  if (resultCol.column == null) {
    return "resultCol is not a valid column";
  }
  resultCol = resultCol.column;

  if (!keyword) {
    return "keyword cannot be mull";
  }

  if (getContent == null) {
    getContent = false;
  }

  console.info("Running websheetFetchGoogleResult function...");

  let resp = fetchGoogleSearchResult(keyword, getContent);

  let data = [];
  data.push(["Title", "Link", "Desc", "content"]);

  resp.forEach((r) => {
    data.push([
      r["title"],
      r["link"],
      r["description"],
      r["text_content"] ?? "",
    ]);
  });

  websheetClearResult(sheet, params);

  sheet.getRange(resultRow, resultCol).setValue("No. result:");
  sheet.getRange(resultRow, resultCol + 1).setValue(data.length - 1);

  let numCols = data[0].length;
  let _r = sheet.getRange(resultRow + 1, resultCol, data.length, numCols);
  _r.setValues(data); // write the email data to the sheet
  _r.setVerticalAlignment("top");
  _r.setWrap(true);
}

function webQuestionAnswering(sheet, params = {}) {
  let {
    startRow,
    startCol,
    titleCol,
    descCol,
    contentCol,
    resultCell,
    question,
  } = params;

  if (typeof startRow != "number") {
    return "startRow must be a number";
  }
  if (!Number.isInteger(startRow)) {
    return "startRow must be an integer";
  }

  startCol = fromA1Notation(startCol);
  if (startCol.column == null) {
    return "startCol is an invalid column";
  }
  startCol = startCol.column;

  titleCol = fromA1Notation(titleCol);
  if (titleCol.column == null) {
    return "titleCol is an invalid column";
  }
  titleCol = titleCol.column;

  descCol = fromA1Notation(descCol);
  if (descCol.column == null) {
    return "descCol is an invalid column";
  }
  descCol = descCol.column;

  if (contentCol != null) {
    contentCol = fromA1Notation(contentCol);
    if (contentCol.column == null) {
      return "contentCol is an invalid column";
    }
    contentCol = contentCol.column;
  }

  resultCell = fromA1Notation(resultCell);
  if (resultCell.row == null || resultCell.column == null) {
    return "resultCell is an invalid cell";
  }

  if (question == null) {
    return "question must not be empty";
  }

  let noSearchResult = sheet.getRange(startRow, startCol + 1).getValue();
  if (noSearchResult == 0) {
    return "No seach result found";
  }

  let titles = sheet
    .getRange(startRow + 2, titleCol, noSearchResult, 1)
    .getValues();
  titles = flatten1DArray(titles);

  let descs = sheet
    .getRange(startRow + 2, descCol, noSearchResult, 1)
    .getValues();
  descs = flatten1DArray(descs);

  let contents = [];
  if (contentCol) {
    contents = sheet
      .getRange(startRow + 2, descCol, noSearchResult, 1)
      .getValues();
    contents = flatten1DArray(contents);
  }

  console.info("Running GPT Prompt");
  setStatus(sheet, "RUNNING", WEB_TRIGGER_ACTION_CELL);
  setExecResult(sheet, "RUNNING_PROMPT");

  let tempCollectionId = Utilities.getUuid();
  zip(titles, descs, contents).forEach((e, i) => {
    let [title, desc, content] = e;

    let doc = `Title: ${title}\n\nDescription:\n${desc}`;
    if (content && content.length > 0) {
      doc += `\n\nContent:\n${content}`;
    }

    if (i == 0) {
      let resp = indexCollection(tempCollectionId, [doc]);
      console.log(`First message response: ${JSON.stringify(resp)}`);
    } else {
      let resp = addDocumentToCollectionIndex(tempCollectionId, [doc]);
      console.log(`${i} message response: ${JSON.stringify(resp)}`);
    }
  });

  let queryResp = queryCollectionIndex(tempCollectionId, question);
  let answer = queryResp["result"];
  console.log(`Answer for question ${question}: ${answer}`);

  console.log(`Result cell ${resultCell.row} - ${resultCell.column}`);
  sheet.getRange(resultCell.row, resultCell.column).setValue(answer.trim());

  let deleteResp = deleteCollectionIndex(tempCollectionId);
  console.log(`Delete thread result: ${JSON.stringify(deleteResp)}`);

  setExecResult(sheet, "RUN_PROMPT_COMPLETED", WEB_EXEC_RESULT_CELL);
}
