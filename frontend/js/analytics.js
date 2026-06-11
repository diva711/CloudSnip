async function loadRecentClicks() {
  const container = document.getElementById('recentClicks');

  try {
    const res = await fetch(`${API}/analytics`, {
      headers: { 'Authorization': `Bearer ${getToken()}` }
    });

    if (res.status === 401) {
      logout();
      return;
    }

    const data = await res.json();
    const clicks = data.recent_clicks;

    if (!clicks || clicks.length === 0) {
      container.innerHTML = `
        <tr>
          <td colspan="3" class="empty-state">
            No clicks yet. Share your links to see activity here!
          </td>
        </tr>`;
      return;
    }

    container.innerHTML = clicks.map(click => `
      <tr>
        <td>${click.short_code}</td>
        <td>${click.ip_address || 'Unknown'}</td>
        <td>${new Date(click.clicked_at).toLocaleString()}</td>
      </tr>
    `).join('');

  } catch {
    container.innerHTML = `
      <tr>
        <td colspan="3" class="empty-state">
          Could not load click data.
        </td>
      </tr>`;
  }
}