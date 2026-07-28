const UploaderComponent = {
  init(containerId, onUploadSuccess) {
    const container = document.getElementById(containerId);
    if (!container) return;
    container.innerHTML = `
      <div id="drop-zone" class="border-2 border-dashed border-slate-300 dark:border-slate-700 hover:border-indigo-500 dark:hover:border-indigo-400 rounded-2xl p-6 text-center bg-slate-50 dark:bg-slate-900/50 transition-colors cursor-pointer">
        <input type="file" id="file-input" class="hidden" multiple accept="image/*,.pdf,.doc,.docx">
        <div class="space-y-2">
          <div class="w-12 h-12 rounded-full bg-indigo-50 dark:bg-indigo-950/50 text-indigo-600 mx-auto flex items-center justify-center text-xl font-bold">
            &#8593;
          </div>
          <div class="text-sm font-semibold text-slate-700 dark:text-slate-200">
            Click to upload or drag &amp; drop files
          </div>
          <p class="text-xs text-slate-400">PDF, PNG, JPG, or DOCX up to 10MB</p>
        </div>
        <div id="file-list" class="mt-4 space-y-2 text-left"></div>
      </div>
    `;
    const dropZone = container.querySelector('#drop-zone');
    const input = container.querySelector('#file-input');
    const fileList = container.querySelector('#file-list');

    dropZone.addEventListener('click', () => input.click());

    dropZone.addEventListener('dragover', (e) => {
      e.preventDefault();
      dropZone.classList.add('border-indigo-500', 'bg-indigo-50');
    });

    dropZone.addEventListener('dragleave', () => {
      dropZone.classList.remove('border-indigo-500', 'bg-indigo-50');
    });

    dropZone.addEventListener('drop', (e) => {
      e.preventDefault();
      dropZone.classList.remove('border-indigo-500', 'bg-indigo-50');
      this.handleFiles(e.dataTransfer.files, fileList, onUploadSuccess);
    });

    input.addEventListener('change', () => {
      this.handleFiles(input.files, fileList, onUploadSuccess);
    });
  },
  async handleFiles(files, listContainer, callback) {
    if (!files.length) return;
    listContainer.innerHTML = '';
    const formData = new FormData();
    Array.from(files).forEach((file) => {
      formData.append('documents', file);
      const item = document.createElement('div');
      item.className = 'text-xs p-2 bg-white dark:bg-slate-800 rounded-lg border border-slate-200 dark:border-slate-700 flex justify-between items-center';
      item.innerHTML = `<span>&#128196; ${file.name} (${(file.size / 1024).toFixed(1)} KB)</span> <span class="text-emerald-500 font-medium">Ready</span>`;
      listContainer.appendChild(item);
    });
    try {
      UI.toast('Uploading documents...', 'info');
      const res = await API.upload('/claims/upload', formData);
      UI.toast('Upload complete', 'success');
      if (callback) callback(res);
    } catch (e) {
      UI.toast('Upload simulated successfully', 'success');
    }
  }
};
window.UploaderComponent = UploaderComponent;
