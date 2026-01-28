const username = "rockin12345678";
const password = "Varun123456789";

browser.webRequest.onAuthRequired.addListener(
  function(details) {
    return {
      authCredentials: {
        username: username,
        password: password
      }
    };
  },
  {urls: ["<all_urls>"]},
  ["blocking"]
);
