function createMessages(content) {
  let messages = [];
  messages.push({
    role: "user",
    content: content,
  });
  return messages;
}

function createChatCompletion(
  messages,
  model = "gpt-3.5-turbo",
  temperature = 0.8
) {
  const OPENAI_API_KEY =
    PropertiesService.getScriptProperties().getProperty("OPENAI_API_KEY");
  if (!OPENAI_API_KEY || OPENAI_API_KEY == "") {
    throw new Error("Cannot get property OPENAI_API_KEY");
  }

  let url = "https://api.openai.com/v1/chat/completions";
  let headers = {
    "Content-Type": "application/json",
    Authorization: "Bearer " + OPENAI_API_KEY,
    "OpenAI-Organization": "org-g75oa8zltnpiPRvW9eWygSaf",
  };
  let data = {
    model: model,
    messages: messages,
    temperature: temperature,
  };
  let options = {
    method: "post",
    headers: headers,
    payload: JSON.stringify(data),
  };
  let response = UrlFetchApp.fetch(url, options);
  let json = response.getContentText();
  let result = JSON.parse(json);
  return result;
}

function runGPTPrompt(sheet, params = {}, customPrompt = false) {
  let {
    startRow,
    startCol,
    contentCol,
    subjectCol,
    senderCol,
    sentDateCol,
    promptCol,
    commonPrompt,
    resultCol,
  } = params;

  console.log(`startRow: ${startRow}`);
  if (typeof startRow != "number") {
    return "startRow must be a number";
  }
  if (!Number.isInteger(startRow)) {
    return "startRow must be an integer";
  }

  console.log(`startCol: ${startCol}`);
  if (startCol == null) {
    return "startCol must not be empty";
  }
  startCol = fromA1Notation(startCol);
  if (startCol.column == null) {
    return "startCol is invalid column";
  }
  startCol = startCol.column;

  console.log(`contentCol: ${contentCol}`);
  if (contentCol == null) {
    return "contentCol must not be empty";
  }
  contentCol = fromA1Notation(contentCol);
  if (contentCol.column == null) {
    return "contentCol is invalid column";
  }
  contentCol = contentCol.column;

  console.log(`resultCol: ${resultCol}`);
  if (resultCol == null) {
    return "resultCol must not be empty";
  }
  resultCol = fromA1Notation(resultCol);
  if (resultCol.column == null) {
    return "resultCol is invalid column";
  }
  resultCol = resultCol.column;

  if (subjectCol) {
    console.log(`subjectCol: ${subjectCol}`);
    if (subjectCol == null) {
      return "subjectCol must not be empty";
    }
    subjectCol = fromA1Notation(subjectCol);
    if (subjectCol.column == null) {
      return "subjectCol is invalid column";
    }
    subjectCol = subjectCol.column;
  }

  if (senderCol) {
    console.log(`senderCol: ${senderCol}`);
    if (senderCol == null) {
      return "senderCol must not be empty";
    }
    senderCol = fromA1Notation(senderCol);
    if (senderCol.column == null) {
      return "senderCol is invalid column";
    }
    senderCol = subjectCol.column;
  }

  if (sentDateCol) {
    console.log(`sentDateCol: ${sentDateCol}`);
    if (sentDateCol == null) {
      return "sentDateCol must not be empty";
    }
    sentDateCol = fromA1Notation(sentDateCol);
    if (sentDateCol.column == null) {
      return "sentDateCol is invalid column";
    }
    sentDateCol = sentDateCol.column;
  }

  if (commonPrompt == null && promptCol == null) {
    return "commonPrompt and promptCol cannot be null at the same time";
  }

  if (promptCol) {
    console.log(`promptCol: ${promptCol}`);
    promptCol = fromA1Notation(promptCol);
    if (promptCol.column == null) {
      return "promptCol is invalid column";
    }
    promptCol = promptCol.column;
  }

  let noEmails = sheet.getRange(startRow, startCol + 1).getValue();
  if (noEmails == 0) {
    return "No email found";
  }

  setStatus(sheet, S_RUNNING);

  let emailIds = sheet
    .getRange(startRow + 2, startCol, noEmails, 1)
    .getValues();
  emailIds = flatten1DArray(emailIds);
  let contents = sheet
    .getRange(startRow + 2, contentCol, noEmails, 1)
    .getValues();
  contents = flatten1DArray(contents);

  let prompts = [];
  if (promptCol) {
    prompts = sheet.getRange(startRow + 2, promptCol, noEmails, 1).getValues();
    prompts = flatten1DArray(prompts);
  }

  console.info("Running GPT Prompt");
  setStatus(sheet, "RUNNING");
  setExecResult(sheet, "RUNNING_PROMPT");

  sheet.getRange(startRow + 1, resultCol, 1, 1).setValue("Prompt Result");

  let retryTimes = 2;
  let retryItems = [];

  zip(emailIds, contents, prompts).forEach((e, i) => {
    let [emailId, content, prompt] = e;

    console.info(`Processing email ${emailId}`);
    setExecResult(sheet, `Processing email ${emailId}`);

    if (!prompt || prompt == "") {
      prompt = commonPrompt;
    } else if (customPrompt) {
      console.info(`Run custom prompt only, skipping row ${i}`);
      return;
    }
    console.info(`Prompt: ${prompt}`);

    let messages = createMessages(`"""${content}"""\n\n${prompt}`);
    console.info(`Messages: ${JSON.stringify(messages)}`);

    try {
      let result = createChatCompletion(messages);
      let gptResult = result["choices"][0]["message"]["content"];
      let _r = sheet.getRange(startRow + 2 + i, resultCol, 1, 1);
      _r.setValue(gptResult);
      _r.setVerticalAlignment("top");
      _r.setWrap(true);

      let resp = addEmailGPTRevision(emailId, prompt, content, gptResult);
      console.log(resp);
    } catch (err) {
      console.error(err);
      retryItems.push({
        i: i,
        prompt: prompt,
        content: contents[i],
      });
      let _r = sheet.getRange(startRow + 2 + i, resultCol, 1, 1);
      _r.setValue("Retrying");
      _r.setVerticalAlignment("top");
    }
    Utilities.sleep(3000);
  });

  while (retryItems.length > 0) {
    let item = retryItems.pop();
    for (let i = 0; i < retryTimes; i++) {
      let content = item.content;
      let prompt = item.prompt;
      let messages = createMessages(`"""${content}"""\n\n${prompt}`);
      try {
        let result = createChatCompletion(messages);
        let gptResult = result["choices"][0]["message"]["content"];
        let _r = sheet.getRange(startRow + 2 + item.i, resultCol, 1, 1);
        _r.setValue(gptResult);
        _r.setVerticalAlignment("top");
        _r.setWrap(true);
      } catch (err) {
        console.error(`Error ${i}th(st/nd/rd)`);
        Utilities.sleep(10000);
      }
      Utilities.sleep(3000);
    }
  }

  setExecResult(sheet, "RUN_PROMPT_COMPLETED");
}

function questionAnswering(sheet, params = {}) {
  let {
    startRow,
    startCol,
    contentCol,
    subjectCol,
    senderCol,
    sentDateCol,
    question,
    resultCell,
  } = params;

  console.log(`startRow: ${startRow}`);
  if (typeof startRow != "number") {
    return "startRow must be a number";
  }
  if (!Number.isInteger(startRow)) {
    return "startRow must be an integer";
  }

  startCol = fromA1Notation(startCol);
  if (startCol.column == null) {
    return "startCol is invalid column";
  }
  startCol = startCol.column;

  contentCol = fromA1Notation(contentCol);
  if (contentCol.column == null) {
    return "contentCol is invalid column";
  }
  contentCol = contentCol.column;

  if (!resultCell) {
    return "resultCell must not be empty";
  }
  resultCell = fromA1Notation(resultCell);

  if (subjectCol) {
    console.log(`subjectCol: ${subjectCol}`);
    if (subjectCol == null) {
      return "subjectCol must not be empty";
    }
    subjectCol = fromA1Notation(subjectCol);
    if (subjectCol.column == null) {
      return "subjectCol is invalid column";
    }
    subjectCol = subjectCol.column;
  }

  if (senderCol) {
    console.log(`senderCol: ${senderCol}`);
    if (senderCol == null) {
      return "senderCol must not be empty";
    }
    senderCol = fromA1Notation(senderCol);
    if (senderCol.column == null) {
      return "senderCol is invalid column";
    }
    senderCol = subjectCol.column;
  }

  if (sentDateCol) {
    console.log(`sentDateCol: ${sentDateCol}`);
    if (sentDateCol == null) {
      return "sentDateCol must not be empty";
    }
    sentDateCol = fromA1Notation(sentDateCol);
    if (sentDateCol.column == null) {
      return "sentDateCol is invalid column";
    }
    sentDateCol = sentDateCol.column;
  }

  let noEmails = sheet.getRange(startRow, startCol + 1).getValue();
  if (noEmails == 0) {
    return "No email found";
  }

  let emailIds = sheet
    .getRange(startRow + 2, startCol, noEmails, 1)
    .getValues();
  emailIds = flatten1DArray(emailIds);
  let contents = sheet
    .getRange(startRow + 2, contentCol, noEmails, 1)
    .getValues();
  contents = flatten1DArray(contents);

  console.info("Running GPT Prompt");
  setStatus(sheet, "RUNNING");
  setExecResult(sheet, "RUNNING_PROMPT");

  let tempThreadId = Utilities.getUuid();
  zip(emailIds, contents).forEach((e, i) => {
    let [emailId, content] = e;

    if (i == 0) {
      let resp = indexEmailThread(tempThreadId, [content]);
      console.log(`First message response: ${JSON.stringify(resp)}`);
    } else {
      let resp = addMessagesToThreadIndex(tempThreadId, [content]);
      console.log(`${i} message response: ${JSON.stringify(resp)}`);
    }
  });

  let queryResp = queryThreadIndex(tempThreadId, question);
  let answer = queryResp["result"];
  console.log(`Answer for question ${question}: ${answer}`);

  console.log(`Result cell ${resultCell.row} - ${resultCell.column}`);
  sheet.getRange(resultCell.row, resultCell.column).setValue(answer.trim());

  let deleteResp = deleteThreadIndex(tempThreadId);
  console.log(`Delete thread result: ${JSON.stringify(deleteResp)}`);

  setExecResult(sheet, "RUN_PROMPT_COMPLETED");
}
