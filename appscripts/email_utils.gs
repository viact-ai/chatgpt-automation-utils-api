function cleanEmailBody(bodyPlain) {
  // Clean body
  bodyPlain = bodyPlain.replace(/https?:\/\/[^\s]+/g, "<Link>"); // Replace all link with <Link> token to reduce length
  // Replace multiple consecutive blank lines with 2 blank lines, while trimming whitespace from each line
  bodyPlain = bodyPlain.replace(/ *\n\s*( *\n\s*)+/g, "\n\n");
  bodyPlain = bodyPlain.trim();

  // Remove all &#847;&zwnj; tokens from the body html
  bodyPlain = bodyPlain.replace(/&#847;/g, "");
  bodyPlain = bodyPlain.replace(/&zwnj;/g, "");
  return bodyPlain;
}

function clearEmailCrawled(sheet, params = {}) {
  let { resultRow, resultCol } = params;
  console.info("Clear emails crawled result");

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

  let noEmails = sheet.getRange(resultRow, resultCol + 1).getValue();
  if (isNaN(noEmails)) {
    console.info("No emails crawled result found.");
    return;
  }

  let lastCol = sheet.getLastColumn();
  sheet.getRange(resultRow, resultCol, noEmails + 2, lastCol).clear();
  console.info("Clear emails crawled completed");
}

function crawlEmail(sheet, params = {}) {
  let {
    resultRow = 10,
    resultCol = "A",
    maxThreads,
    maxMessages,
    fromDate,
    toDate,
    senderEmail,
  } = params;

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

  console.info("Crawling email");

  console.info(`Max threads: ${maxThreads}`);
  console.info(`Max messages: ${maxMessages}`);

  setStatus(sheet, S_RUNNING);
  setExecResult(sheet, S_CRAWLING_EMAIL);

  //  var threads = GmailApp.search('is:unread'); // search for all unread emails
  // var threads = GmailApp.getInboxThreads();

  let conditions = [];
  if (fromDate) {
    conditions.push(`after:${convert2datestr(fromDate)}`);
  }
  if (toDate) {
    conditions.push(`before:${convert2datestr(toDate)}`);
  }
  if (senderEmail) {
    conditions.push(`from:${senderEmail}`);
  }
  let threads = [];
  if (conditions.length > 0) {
    let searchString = conditions.join(" ");
    console.info(`Search string Gmail: ${searchString}`);
    threads = GmailApp.search(searchString);
  } else {
    console.info("Get Inbox Threads");
    if (maxThreads != null) {
      threads = GmailApp.getInboxThreads(0, maxThreads);
    } else {
      threads = GmailApp.getInboxThreads();
    }
  }

  let messages = GmailApp.getMessagesForThreads(threads);
  let data = [];

  let len =
    maxMessages != null
      ? Math.min(maxMessages, messages.length)
      : messages.length;
  for (let i = 0; i < len; i++) {
    console.info(`Processing message ${i}...`);

    let message = messages[i][0];
    let threadId = message.getThread().getId();
    let mailId = message.getId();
    let subject = message.getSubject();
    let bodyHtml = message.getBody();
    let bodyPlain = message.getPlainBody();
    let _from = message.getFrom();
    let to = message.getTo();
    let cc = message.getCc();
    let bcc = message.getBcc();
    let date = message.getDate();

    bodyPlain = cleanEmailBody(bodyPlain);

    data.push([threadId, mailId, subject, _from, to, cc, bcc, date, bodyPlain]); // add the email data to an array
  }

  clearEmailCrawled(sheet, params);

  console.info(`Writing ${data.length} result(s)`);
  setExecResult(sheet, "WRITING_RESULT");
  if (data.length > 0) {
    data.splice(0, 0, [
      "ThreadId",
      "EmailId",
      "Subject",
      "Sender",
      "Recipient",
      "CC",
      "BCC",
      "Sent date",
      "Content",
    ]);
    let numRows = data.length;
    let numCols = data[0].length;
    sheet.getRange(resultRow, resultCol, numRows + 1, numCols).clear();
    sheet
      .getRange(resultRow, resultCol, 1, 2)
      .setValues([["No. emails crawled", data.length - 1]]);
    let _r = sheet.getRange(resultRow + 1, resultCol, numRows, numCols);
    _r.setValues(data); // write the email data to the sheet
    _r.setVerticalAlignment("top");
    _r.setWrap(true);
  }
  console.info("Crawling completed");
  setStatus(sheet, S_COMPLETED);
  setExecResult(sheet, S_CRAWLING_EMAIL_DONE);
}

function sendEmail(sheet, params = {}) {
  let {
    startRow,
    startCol,
    subjectCol,
    contentCol,
    recipientsCol,
    sendAtCol,
    resultCol,
  } = params;

  // validate params
  console.log(`startRow: ${startRow}`);
  if (typeof startRow != "number") {
    return "startRow must be a number";
  }
  if (!Number.isInteger(startRow)) {
    return "startRow must be an integer";
  }

  console.log(`startCol: ${startCol}`);
  startCol = fromA1Notation(startCol);
  if (startCol.column == null) {
    return "startCol is not a valid column";
  }
  startCol = startCol.column;

  console.log(`subjectCol: ${subjectCol}`);
  subjectCol = fromA1Notation(subjectCol);
  if (subjectCol.column == null) {
    return "subjectCol is not a valid column";
  }
  subjectCol = subjectCol.column;

  console.log(`contentCol: ${contentCol}`);
  contentCol = fromA1Notation(contentCol);
  if (contentCol.column == null) {
    return "contentCol is not a valid column";
  }
  contentCol = contentCol.column;

  console.log(`recipientsCol: ${recipientsCol}`);
  recipientsCol = fromA1Notation(recipientsCol);
  if (recipientsCol.column == null) {
    return "recipientsCol is not a valid column";
  }
  recipientsCol = recipientsCol.column;

  console.log(`sendAtCol: ${sendAtCol}`);
  sendAtCol = fromA1Notation(sendAtCol);
  if (sendAtCol.column == null) {
    return "sendAtCol is not a valid column";
  }
  sendAtCol = sendAtCol.column;
  console.log(sendAtCol);

  console.log(`resultCol: ${resultCol}`);
  resultCol = fromA1Notation(resultCol);
  if (resultCol.column == null) {
    return "resultCol is not a valid column";
  }
  resultCol = resultCol.column;

  console.info("Start sending email...");
  setStatus(sheet, S_RUNNING);

  let nEmails = sheet.getRange(startRow, startCol + 1).getValue();

  console.info(`Number of email: ${nEmails}`);

  // Skip header row
  startRow += 2;
  let lastRow = startRow + nEmails - 1;

  let subjects = sheet
    .getRange(startRow, subjectCol, lastRow - startRow + 1, 1)
    .getValues();
  subjects = flatten1DArray(subjects);
  let contents = sheet
    .getRange(startRow, contentCol, lastRow - startRow + 1, 1)
    .getValues();
  contents = flatten1DArray(contents);
  let recipients = sheet
    .getRange(startRow, recipientsCol, lastRow - startRow + 1, 1)
    .getValues();
  recipients = flatten1DArray(recipients);
  let sendAts = [];
  if (sendAtCol) {
    sendAts = sheet
      .getRange(startRow, sendAtCol, lastRow - startRow + 1, 1)
      .getValues();
    sendAts = flatten1DArray(sendAts);
  }

  sheet.getRange(startRow - 1, resultCol).setValue("Send email result");
  zip(subjects, contents, recipients, sendAts).forEach((e, i) => {
    let [subject, content, recipient, sendAt] = e;
    if (!subject) {
      sheet.getRange(startRow + i, resultCol).setValue("Subject is null");
      return;
    }
    if (!content) {
      sheet.getRange(startRow + i, resultCol).setValue("Content is null");
      return;
    }
    if (!recipient) {
      sheet.getRange(startRow + i, resultCol).setValue("Recipient is null");
      return;
    }

    // GmailApp.sendEmail(
    //   recipient,
    //   subject,
    //   content,
    // )

    // Sending email
    let scheduledTime = null;
    if (sendAt == null) {
      sheet
        .getRange(startRow + i, resultCol)
        .setValue("SendAt is not specified");
      console.info(`Send at at row ${startRow + i} is not specified`);
      return;
    }

    if (sendAt.toLowerCase() == "now") {
      scheduledTime = new Date();
    } else {
      scheduledTime = parseDateTime(sendAt);
    }

    let resp = scheduleSendEmail({
      subject,
      content,
      recipients: [recipient],
      scheduledTime: scheduledTime.toISOString(),
    });
    console.log(resp);

    let now = new Date();
    let v = sendAt.toLowerCase() == "now" ? "Sent" : "Scheduled";
    let _r = sheet.getRange(startRow + i, resultCol);
    _r.setValue(v);
    _r.setVerticalAlignment("top");
  });
}

function timeDrivenTriggerFollowUpEmailThread(e) {
  let spreadsheet = SpreadsheetApp.getActiveSpreadsheet();
  let sheets = spreadsheet.getSheets();

  let followUpSheets = sheets.filter((s) => {
    if (s.getName().toLocaleLowerCase().includes(FOLLOW_UP_PREFIX_SHEET_NAME)) {
      return true;
    }
    return false;
  });

  if (followUpSheets.length == 0) {
    console.info("No sheet to trigger follow-up email");
    return;
  }

  console.info(`There're ${followUpSheets.length} sheet(s) to follow-up`);
  followUpSheets.forEach((s) => {
    console.info(`Sheet: ${s.getName()}`);
  });

  followUpSheets.forEach((s) => {
    let params = readFunctionParams(s, FOLLOW_UP_PARAMS_RANGE);
    setExecResult(s, "RUNNING", FOLLOW_UP_EXEC_RESULT_CELL);
    let result = autoFollowUpEmail(s, params);
    if (result != CODE_NO_ERROR) {
      console.error(
        `Got error ${result} when run follow-up email for sheet ${s.getName()}`
      );
      setExecResult(s, result, FOLLOW_UP_EXEC_RESULT_CELL);
    }

    setExecResult(s, "COMPLETED", FOLLOW_UP_EXEC_RESULT_CELL);
  });
}

function autoFollowUpEmail(sheet, params = {}) {
  let { threadId, resultRow, resultCol, instruction } = params;

  if (!threadId) {
    return "threadId cannot be empty";
  }

  if (!resultRow) {
    return "resultRow must not be empty";
  }
  if (!Number.isInteger(resultRow)) {
    return "resultRow must be an interger";
  }

  if (!resultCol) {
    return "resultCol must not be empty";
  }
  resultCol = fromA1Notation(resultCol);
  if (resultCol.column == null) {
    return "resultCol is an invalid column name";
  }
  resultCol = resultCol.column;

  let thread = GmailApp.getThreadById(threadId);
  if (!thread) {
    return `cannot find thread with id ${threadId}`;
  }

  let data = [];
  let messages = thread.getMessages();

  // Remove message which is in the trash
  messages = messages.filter((m) => !m.isInTrash());
  console.info(
    `Thread ${threadId} found with ${thread.getMessageCount()} messaage(s) (not count email in trash)`
  );

  messages.forEach((message) => {
    let mailId = message.getId();
    let subject = message.getSubject();
    let bodyHtml = message.getBody();
    let bodyPlain = message.getPlainBody();
    let _from = message.getFrom();
    let to = message.getTo();
    let cc = message.getCc();
    let bcc = message.getBcc();
    let date = message.getDate();

    // console.log('=============================')
    // console.log(`Message-ID: ${message.getHeader('Message-ID')}`)
    // console.log(`Subject: ${message.getHeader('Subject')}`)
    // console.log(`In-Reply-To: ${message.getHeader('In-Reply-To')}`)
    // console.log(`Reply-To: ${message.getHeader('Reply-To')}`)
    // console.log(`References: ${message.getHeader('References')}`)

    bodyPlain = cleanEmailBody(bodyPlain);

    data.push([mailId, subject, _from, to, cc, bcc, date, bodyPlain]); // add the email data to an array
  });

  if (data.length == 0) {
    console.info("no message in thread");
    return "no messages in thread";
  }

  // clear data before write new data
  clearEmailCrawled(sheet, params);

  // add header and write result to sheet
  data.splice(0, 0, [
    "EmailId",
    "Subject",
    "Sender",
    "Recipient",
    "CC",
    "BCC",
    "Sent date",
    "Content",
    "",
  ]);
  data = data.map((e, i) => {
    if (i == 0) return e;
    e.push("");
    return e;
  });
  let numRows = data.length;
  let numCols = data[0].length;
  sheet.getRange(resultRow, resultCol, numRows + 1, numCols).clear();
  sheet
    .getRange(resultRow, resultCol, 1, 2)
    .setValues([["No. emails", data.length - 1]]);
  let _r = sheet.getRange(resultRow + 1, resultCol, numRows, numCols);
  _r.setValues(data); // write the email data to the sheet
  _r.setVerticalAlignment("top");
  _r.setWrap(true);
  data = data.slice(1);

  let lastMessage = messages[messages.length - 1];
  console.info(`lastMessage sender: ${lastMessage.getFrom()}`);

  let userEmail = Session.getActiveUser().getEmail();
  console.info(`user email: ${userEmail}`);

  let history = [];
  messages.forEach((d, idx) => {
    let content = d.getPlainBody();
    content = cleanEmailBody(content);

    let sender = getEmailFromFromHeader(d.getFrom());

    history.push({
      role: isCompanyEmail(sender) ? "assistant" : "human",
      message: content,
    });
  });

  let lastMessageContent = lastMessage.getPlainBody();
  let lastMessageSender = getEmailFromFromHeader(lastMessage.getFrom());
  lastMessageContent = cleanEmailBody(lastMessageContent);

  // Check if the last message is not assistant
  // it means we don't reply the email yet
  if (!isCompanyEmail(lastMessageSender)) {
    // call API to write follow-up email
    console.log(`instruction: ${instruction}`);
    let resp = apiWriteFollowUpEmail(history, lastMessageContent, instruction);
    let replyEmailContent = resp["result"];
    console.info(`Reply email: ${replyEmailContent}`);

    // send reply email
    // _lastMessage.reply(replyEmailContent)

    scheduleSendEmail({
      subject: "Re: " + lastMessage.getSubject(),
      content: replyEmailContent,
      recipients: [lastMessageSender],
      cc: userEmail,
      scheduledTime: new Date().toISOString(),
      replyTo: lastMessage.getHeader("Message-ID"),
      references: lastMessage.getHeader("References"),
    });

    // instead of sending email, just write the follow-up email back to the sheet
    // let d = [
    //   '',
    //   'Re: ' + lastMessage.getSubject(),
    //   'Assistant',
    //   lastMessageSender,
    //   '',
    //   userEmail,
    //   'NOW',
    //   replyEmailContent,
    //   '',
    // ]
    // let _r = sheet.getRange(resultRow + data.length + 2, resultCol, 1, numCols)
    // _r.setValues([d]) // write the email data to the sheet
    // _r.setVerticalAlignment('top')
    // _r.setWrap(true)

    console.info("follow-up email sent");
    setStatus(sheet, "COMPLETED", FOLLOW_UP_TRIGGER_ACTION_CELL);
    setExecResult(sheet, "FOLLOW-UP_EMAIL_SENT", FOLLOW_UP_EXEC_RESULT_CELL);
  }

  return CODE_NO_ERROR;
}

function followUpFetchEmailFromInbox(sheet, params = {}) {
  let { resultRow, resultCol, threadId } = params;

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

  if (threadId == null) {
    return "threadId must not be null";
  }

  let thread = GmailApp.getThreadById(threadId);
  if (!thread) {
    return `cannot find thread with id ${threadId}`;
  }

  console.info("Running followUpFetchEmailFromInbox function");
  let data = [];
  let messages = thread.getMessages();

  // Remove message which is in the trash
  messages = messages.filter((m) => !m.isInTrash());
  console.info(
    `Thread ${threadId} found with ${thread.getMessageCount()} messaage(s) (not count email in trash)`
  );

  messages.forEach((message) => {
    let mailId = message.getId();
    let subject = message.getSubject();
    let bodyHtml = message.getBody();
    let bodyPlain = message.getPlainBody();
    let _from = message.getFrom();
    let to = message.getTo();
    let cc = message.getCc();
    let bcc = message.getBcc();
    let date = message.getDate();

    // console.log('=============================')
    // console.log(`Message-ID: ${message.getHeader('Message-ID')}`)
    // console.log(`Subject: ${message.getHeader('Subject')}`)
    // console.log(`In-Reply-To: ${message.getHeader('In-Reply-To')}`)
    // console.log(`Reply-To: ${message.getHeader('Reply-To')}`)
    // console.log(`References: ${message.getHeader('References')}`)

    bodyPlain = cleanEmailBody(bodyPlain);

    data.push([mailId, subject, _from, to, cc, bcc, date, bodyPlain]); // add the email data to an array
  });

  if (data.length == 0) {
    console.info("no message in thread");
    return "no messages in thread";
  }

  // clear data before write new data
  clearEmailCrawled(sheet, params);

  // add header and write result to sheet
  data.splice(0, 0, [
    "EmailId",
    "Subject",
    "Sender",
    "Recipient",
    "CC",
    "BCC",
    "Sent date",
    "Content",
    "",
  ]);
  data = data.map((e, i) => {
    if (i == 0) return e;
    e.push("");
    return e;
  });
  let numRows = data.length;
  let numCols = data[0].length;
  sheet.getRange(resultRow, resultCol, numRows + 1, numCols).clear();
  sheet
    .getRange(resultRow, resultCol, 1, 2)
    .setValues([["No. emails", data.length - 1]]);
  let _r = sheet.getRange(resultRow + 1, resultCol, numRows, numCols);
  _r.setValues(data); // write the email data to the sheet
  _r.setVerticalAlignment("top");
  _r.setWrap(true);
  data = data.slice(1);
}

function followUpWriteEmail(sheet, params = {}) {
  let { resultRow, resultCol, instruction } = params;

  console.info("Running followUpWriteEmail function");

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

  let noEmails = sheet.getRange(resultRow, resultCol + 1).getValue();
  if (isNaN(noEmails)) {
    console.info("No emails crawled result found.");
    return CODE_NO_ERROR;
  }

  let lastCol = sheet.getLastColumn();
  let emails = sheet
    .getRange(resultRow, resultCol, noEmails + 2, lastCol)
    .getValues();

  emails = emails.slice(2);

  let lastEmail = emails[emails.length - 1];
  let [emailId, subject, sender, recipient, cc, bcc, sentDate, content] =
    lastEmail;
  let lastMessageSender = getEmailFromFromHeader(sender);
  let lastMessageContent = content;
  let lastMessageSubject = subject;

  // Check if the last email is send from assistant
  if (isCompanyEmail(lastMessageSender)) {
    console.info("The last email was sent from assistant");
    return CODE_NO_ERROR;
  }

  let history = [];
  emails.forEach((email, idx) => {
    let [mailId, subject, sender, recipient, cc, bcc, sentDate, content] =
      email;
    sender = getEmailFromFromHeader(sender);

    history.push({
      role: isCompanyEmail(sender) ? "assistant" : "human",
      message: content,
    });
  });

  let userEmail = Session.getActiveUser().getEmail();
  console.info(`user email: ${userEmail}`);

  console.info(`Writing follow-up email with instruction: ${instruction}`);
  let resp = apiWriteFollowUpEmail(history, lastMessageContent, instruction);
  let replyEmailContent = resp["result"];
  console.info(`Generated reply email: ${replyEmailContent}`);

  // write the follow-up email back to the sheet
  let d = [
    "ASSISTANT_OUTPUT",
    "Re: " + lastMessageSubject,
    "info@viact.ai",
    lastMessageSender,
    "",
    userEmail,
    "NOW",
    replyEmailContent,
    "",
  ];
  let numCols = d.length;
  let _r = sheet.getRange(resultRow + emails.length + 2, resultCol, 1, numCols);
  _r.setValues([d]); // write the email data to the sheet
  _r.setVerticalAlignment("top");
  _r.setWrap(true);

  sheet.getRange(resultRow, 2).setValue(emails.length + 1);
}

function followUpSendEmail(sheet, params = {}) {
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

  console.info("Running followUpSendEmail function");

  let noEmails = sheet.getRange(resultRow, resultCol + 1).getValue();
  if (isNaN(noEmails)) {
    console.info("No emails crawled result found.");
    return CODE_NO_ERROR;
  }

  let lastCol = sheet.getLastColumn();
  let emails = sheet
    .getRange(resultRow, resultCol, noEmails + 2, lastCol)
    .getValues();

  emails = emails.slice(2);
  console.log(emails);

  let lastEmail = emails[emails.length - 1];
  let [emailId, subject, sender, recipient, cc, bcc, sentDate, content] =
    lastEmail;
  console.log(lastEmail);
  let lastMessageSender = getEmailFromFromHeader(sender);
  let lastMessageContent = content;
  let lastMessageSubject = subject;

  // Check if the last email is send from assistant
  if (!isCompanyEmail(lastMessageSender)) {
    console.info("The last email is not from our assistant");
    return CODE_NO_ERROR;
  }

  if (emailId != "ASSISTANT_OUTPUT") {
    console.info("last email already sent");
    return CODE_NO_ERROR;
  }

  // the last email was not generated by human
  console.info("Sending email");

  let userEmail = Session.getActiveUser().getEmail();
  console.info(`user email: ${userEmail}`);

  // get penultimate email
  let penultimateEmail = emails[emails.length - 2];
  let penultimateId = penultimateEmail[0];
  let penEmail = GmailApp.getMessageById(penultimateId);

  scheduleSendEmail({
    subject: lastMessageSubject,
    content: lastMessageContent,
    recipients: [lastMessageSender],
    cc: userEmail,
    scheduledTime: new Date().toISOString(),
    replyTo: penEmail.getHeader("Message-ID"),
    references: penEmail.getHeader("References"),
  });

  // instead of sending email, just write the follow-up email back to the sheet
  lastEmail[0] = "SENT";
  let numCols = lastEmail.length;
  let _r = sheet.getRange(resultRow + emails.length + 1, resultCol, 1, numCols);
  _r.setValues([lastEmail]); // write the email data to the sheet
  _r.setVerticalAlignment("top");
  _r.setWrap(true);

  console.info("Completed!");
}
