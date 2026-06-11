async function shortenURL() {
  const longUrl = document.getElementById('longUrl').value.trim();
  const shortUrlBox = document.getElementById('shortUrl');
  const msg = document.getElementById('shortenMessage');

  if (!longUrl) {
    msg.className = 'message error';
    msg.textContent = 'Please enter a URL';
    return;
  }

  try {
    const res = await fetch(`${API}/shorten`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'Authorization': `Bearer ${getToken()}`
      },
      body: JSON.stringify({ long_url: longUrl })
    });

    const data = await res.json();

    if (res.status === 201) {
      shortUrlBox.value = data.short_url;
      msg.className = 'message success';
      msg.textContent = 'Short URL created successfully';
      loadHistory();
    } else if (res.status === 401) {
      logout();
    } else {
      msg.className = 'message error';
      msg.textContent = data.error || 'Something went wrong';
    }
  } catch {
    msg.className = 'message error';
    msg.textContent = 'Could not connect to server';
  }
}

function copyShortUrl() {
  const shortUrl = document.getElementById('shortUrl').value;
  if (!shortUrl) return;
  navigator.clipboard.writeText(shortUrl);
  const btn = document.getElementById('copyBtn');
  btn.textContent = 'Copied!';
  setTimeout(() => btn.textContent = 'Copy', 2000);
}

async function loadHistory() {
  const tbody = document.getElementById('historyBody');

  try {
    const res = await fetch(`${API}/analytics`, {
      headers: { 'Authorization': `Bearer ${getToken()}` }
    });

    if (res.status === 401) {
      logout();
      return;
    }

    const data = await res.json();
    const links = data.links;

    if (!links || links.length === 0) {
      tbody.innerHTML = `
        <tr>
          <td colspan="4" class="empty-state">
            No links yet. Shorten your first URL above!
          </td>
        </tr>`;
      return;
    }

    tbody.innerHTML = links.map(link => `
      <tr>
        <td class="long-url" title="${link.long_url}">
          <a href="${link.long_url}" target="_blank">${link.long_url}</a>
        </td>
        <td>
          <a href="${link.short_url || `http://${API.split('//')[1]}/${link.short_code}`}" 
             target="_blank">
            ${link.short_code}
          </a>
        </td>
        <td><span class="badge">${link.click_count}</span></td>
        <td>${new Date(link.created_at).toLocaleDateString()}</td>
      </tr>
    `).join('');

  } catch {
    tbody.innerHTML = `
      <tr>
        <td colspan="4" class="empty-state">
          Could not load history.
        </td>
      </tr>`;
  }
}