// SPECZ: spz-ui-k2

function renderLoginForm() {
  return `
    <form method="post" action="/api/login">
      <input type="email" name="email" required>
      <input type="password" name="password" required>
      <button type="submit">Log in</button>
    </form>`;
}

module.exports = { renderLoginForm };
