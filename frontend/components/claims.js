const ClaimsComponent = {
  renderList(claims, containerId) {
    const container = document.getElementById(containerId);
    if (!container) return;
    if (!claims || claims.length === 0) {
      container.innerHTML = `
        <div class="p-8 text-center bg-slate-50 dark:bg-slate-900 rounded-2xl border border-dashed border-slate-300 dark:border-slate-800">
          <p class="text-slate-500 text-sm">No claims found.</p>
        </div>
      `;
      return;
    }
    container.innerHTML = claims.map(claim => `
      <div class="p-5 bg-white dark:bg-slate-900 rounded-2xl border border-slate-200 dark:border-slate-800 shadow-sm hover:shadow-md transition-all flex flex-col md:flex-row md:items-center justify-between gap-4">
        <div class="space-y-1">
          <div class="flex items-center gap-3">
            <span class="font-bold text-slate-800 dark:text-slate-100 text-base">#${String(claim.id || 'CLM-000').slice(0, 8).toUpperCase()}</span>
            <span class="px-3 py-1 text-xs font-semibold rounded-full border ${Utils.getStatusBadgeClass(claim.status)}">
              ${claim.status || 'Pending'}
            </span>
          </div>
          <p class="text-sm font-medium text-slate-600 dark:text-slate-300">${claim.title || claim.type || 'General Insurance Claim'}</p>
          <p class="text-xs text-slate-400">Filed on ${Utils.formatDate(claim.createdAt || claim.submitted_at)}</p>
        </div>
        <div class="flex items-center gap-4">
          <div class="text-right">
            <div class="text-xs text-slate-400">Claim Amount</div>
            <div class="text-lg font-extrabold text-slate-900 dark:text-white">${Utils.formatCurrency(claim.amount || claim.claimed_amount)}</div>
          </div>
          <button onclick="ClaimsComponent.viewDetail('${claim.id}')" class="px-4 py-2 bg-slate-100 dark:bg-slate-800 hover:bg-slate-200 text-slate-700 dark:text-slate-200 text-xs font-semibold rounded-xl transition-colors">
            View Details
          </button>
        </div>
      </div>
    `).join('');
  },
  async viewDetail(claimId) {
    try {
      const claim = await API.get(`/claims/${claimId}`);
      const history = (claim.processing_history || []).map(item => `• ${item.event}`).join('\n') || 'No updates yet.';
      window.alert(`Claim ${String(claim.id).slice(0, 8).toUpperCase()}\n\nType: ${claim.type}\nStatus: ${claim.status}\nAmount: ${Utils.formatCurrency(claim.claimed_amount)}\n\nUpdates:\n${history}`);
    } catch (_) {
      // API displays the actionable error toast.
    }
  }
};
window.ClaimsComponent = ClaimsComponent;
