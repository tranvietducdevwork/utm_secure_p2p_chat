/**
 * Demo toggles — chỉ dùng để trình diễn trước hội đồng.
 */

let storeMessagesOnServer = false;
let storePlaintextOnServer = false;

function getSettings() {
  return {
    storeMessagesOnServer,
    storePlaintextOnServer,
  };
}

function setStoreMessages(enabled) {
  storeMessagesOnServer = Boolean(enabled);
  if (!storeMessagesOnServer) {
    storePlaintextOnServer = false;
  }
  return getSettings();
}

function setStorePlaintext(enabled) {
  storePlaintextOnServer = Boolean(enabled) && storeMessagesOnServer;
  return getSettings();
}

module.exports = {
  getSettings,
  setStoreMessages,
  setStorePlaintext,
};
