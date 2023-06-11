function addEmailGPTRevision(emailId, prompt, emailBody, gptResult) {
  let data = {
    email_id: emailId,
    prompt: prompt,
    email_body: emailBody,
    gpt_result: gptResult,
  };

  let options = {
    method: "POST",
    contentType: "application/json",
    payload: JSON.stringify(data),
  };
  let response = UrlFetchApp.fetch(
    API_BASE_URL + "/email/gpt_revision",
    options
  );
  return JSON.parse(response.getContentText());
}

function scheduleSendEmail(args) {
  let {
    subject,
    content,
    recipients,
    scheduledTime,
    cc = null,
    bcc = null,
    replyTo = null,
    references = null,
  } = args;

  let data = {
    subject: subject,
    content: content,
    recipients: recipients,
    scheduled_time: scheduledTime,
  };

  if (cc) {
    data["cc"] = cc;
  }
  if (bcc) {
    data["bcc"] = bcc;
  }
  if (replyTo) {
    data["reply_to"] = replyTo;
  }
  if (references) {
    data["references"] = references;
  }

  let options = {
    method: "POST",
    contentType: "application/json",
    payload: JSON.stringify(data),
  };
  let response = UrlFetchApp.fetch(API_BASE_URL + "/email/schedule", options);
  return JSON.parse(response.getContentText());
}

function indexEmailThread(threadId, messages) {
  let data = {
    thread_id: threadId,
    messages: messages,
  };

  let options = {
    method: "POST",
    contentType: "application/json",
    payload: JSON.stringify(data),
  };
  let response = UrlFetchApp.fetch(
    API_BASE_URL + "/email/index_thread",
    options
  );
  return JSON.parse(response.getContentText());
}

function addMessagesToThreadIndex(threadId, messages) {
  let data = {
    thread_id: threadId,
    messages: messages,
  };

  let options = {
    method: "POST",
    contentType: "application/json",
    payload: JSON.stringify(data),
  };
  let response = UrlFetchApp.fetch(
    API_BASE_URL + "/email/index_thread/messages",
    options
  );
  return JSON.parse(response.getContentText());
}

function deleteThreadIndex(threadId) {
  let options = {
    method: "DELETE",
    contentType: "application/json",
  };
  let response = UrlFetchApp.fetch(
    API_BASE_URL + `/email/index_thread/${threadId}`,
    options
  );
  return JSON.parse(response.getContentText());
}

function queryThreadIndex(threadId, query) {
  let response = UrlFetchApp.fetch(
    API_BASE_URL + `/email/query_thread/${threadId}?q=${query}`
  );
  return JSON.parse(response.getContentText());
}

function apiWriteFollowUpEmail(history, userInput, instruction = null) {
  let data = {
    history: history,
    user_input: userInput,
  };

  if (instruction) {
    data["instruction"] = instruction;
  }

  let options = {
    method: "POST",
    contentType: "application/json",
    payload: JSON.stringify(data),
  };
  let response = UrlFetchApp.fetch(API_BASE_URL + "/email/follow_up", options);
  return JSON.parse(response.getContentText());
}

function fetchGoogleSearchResult(keyword, getContent = false) {
  let url =
    API_BASE_URL +
    "/crawler/google_result?q=" +
    keyword +
    "&get_content=" +
    getContent;
  let options = {
    method: "GET",
    contentType: "application/json",
  };
  let response = UrlFetchApp.fetch(url, options);
  return JSON.parse(response.getContentText());
}

function indexCollection(collectionId, documents) {
  let data = {
    collection_id: collectionId,
    documents: documents,
  };

  let options = {
    method: "POST",
    contentType: "application/json",
    payload: JSON.stringify(data),
  };
  let response = UrlFetchApp.fetch(
    API_BASE_URL + "/llm/index_collection",
    options
  );
  return JSON.parse(response.getContentText());
}

function addDocumentToCollectionIndex(collectionId, documents) {
  let data = {
    collection_id: collectionId,
    documents: documents,
  };

  let options = {
    method: "POST",
    contentType: "application/json",
    payload: JSON.stringify(data),
  };
  let response = UrlFetchApp.fetch(
    API_BASE_URL + "/llm/index_collection/documents",
    options
  );
  return JSON.parse(response.getContentText());
}

function deleteCollectionIndex(threadId) {
  let options = {
    method: "DELETE",
    contentType: "application/json",
  };
  let response = UrlFetchApp.fetch(
    API_BASE_URL + `/llm/index_collection/${threadId}`,
    options
  );
  return JSON.parse(response.getContentText());
}

function queryCollectionIndex(collectionId, query) {
  let response = UrlFetchApp.fetch(
    API_BASE_URL + `/llm/index_collection/${collectionId}?q=${query}`
  );
  return JSON.parse(response.getContentText());
}
