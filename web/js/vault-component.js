/**
 * DECEPTRON Vault Component
 * A reusable premium UI for selecting uploaded evidence.
 */

const VaultComponent = (function() {
    let vaultModal = null;
    let currentUploads = [];
    let onSelectCallback = null;

    // Initialize Vault Modal HTML
    function init() {
        if (document.getElementById('deceptronVaultModal')) return;

        const modalHTML = `
            <div id="deceptronVaultModal" class="fixed inset-0 hidden items-center justify-center p-4 bg-black/90 backdrop-blur-3xl transition-all duration-300" style="z-index: 100000 !important;">
                <div class="vault-container relative w-full max-w-5xl bg-neutral-900 border border-white/10 rounded-[2.5rem] shadow-2xl overflow-hidden glass transition-all duration-300 scale-95 opacity-0">
                    <!-- Header -->
                    <div class="flex items-center justify-between p-6 border-b border-white/5">
                        <div class="flex items-center space-x-3">
                            <div class="w-10 h-10 rounded-xl bg-cyan-500/10 flex items-center justify-center border border-cyan-500/20">
                                <i class="fas fa-vault text-cyan-400"></i>
                            </div>
                            <div>
                                <h3 class="text-sm font-black text-white uppercase tracking-[0.2em]">Forensic Vault</h3>
                                <p class="text-[9px] text-cyan-500/50 font-bold uppercase tracking-widest mt-0.5">Secure Evidence Selection</p>
                            </div>
                        </div>
                        <button onclick="VaultComponent.close()" class="w-10 h-10 rounded-xl bg-white/5 hover:bg-white/10 text-gray-400 hover:text-white transition-all flex items-center justify-center">
                            <i class="fas fa-times"></i>
                        </button>
                    </div>

                    <!-- Search Bar -->
                    <div class="p-6 pb-0">
                        <div class="relative group">
                            <i class="fas fa-search absolute left-4 top-1/2 -translate-y-1/2 text-gray-500 group-focus-within:text-cyan-400 transition-colors"></i>
                            <input type="text" id="vaultSearch" placeholder="Search evidence vault..." 
                                   class="w-full bg-black/40 border border-white/10 rounded-2xl py-3.5 pl-12 pr-4 text-sm text-white placeholder-gray-600 focus:outline-none focus:border-cyan-500/50 focus:ring-4 focus:ring-cyan-500/10 transition-all">
                        </div>
                    </div>

                    <!-- List Area -->
                    <div class="p-6 h-[450px] overflow-y-auto custom-scrollbar" id="vaultList">
                        <!-- Items injected here -->
                    </div>
                </div>
            </div>

            <style>
                #deceptronVaultModal .vault-container { background: rgba(17, 17, 17, 0.95); }
                #deceptronVaultModal .glass { backdrop-filter: blur(40px); }
                
                body.light-mode #deceptronVaultModal .vault-container { 
                    background: #ffffff !important; 
                    border-color: rgba(0, 219, 255, 0.4) !important;
                    box-shadow: 0 40px 100px rgba(0, 118, 214, 0.15) !important;
                }
                body.light-mode #deceptronVaultModal h3 { color: #0f172a !important; }
                body.light-mode #deceptronVaultModal #vaultSearch { 
                    background: #f8fafc !important; 
                    border-color: #e2e8f0 !important; 
                    color: #0f172a !important; 
                }

                .vault-item {
                    transition: all 0.4s cubic-bezier(0.4, 0, 0.2, 1);
                    cursor: pointer;
                    margin-bottom: 12px;
                    border: 1px solid rgba(255, 255, 255, 0.05);
                }
                .vault-item:hover {
                    transform: translateX(10px) scale(1.02);
                    background: rgba(0, 219, 255, 0.08);
                    border-color: rgba(0, 219, 255, 0.3);
                    box-shadow: 0 10px 30px rgba(0, 219, 255, 0.1);
                }
                
                body.light-mode .vault-item {
                    background: #f8fafc;
                    border-color: #e2e8f0;
                }
                body.light-mode .vault-item:hover {
                    background: #ffffff;
                    border-color: rgba(0, 219, 255, 0.6);
                    box-shadow: 0 15px 40px rgba(0, 118, 214, 0.1);
                }

                body.light-mode .vault-item h4 { color: #1e293b !important; }
                body.light-mode .vault-item p { color: #64748b !important; }

                .custom-scrollbar::-webkit-scrollbar { width: 6px; }
                .custom-scrollbar::-webkit-scrollbar-track { background: transparent; }
                .custom-scrollbar::-webkit-scrollbar-thumb { background: rgba(0, 219, 255, 0.2); border-radius: 10px; }
                body.light-mode .custom-scrollbar::-webkit-scrollbar-thumb { background: rgba(0, 118, 214, 0.15); }
            </style>
        `;

        document.body.insertAdjacentHTML('beforeend', modalHTML);
        vaultModal = document.getElementById('deceptronVaultModal');

        // Search event
        document.getElementById('vaultSearch').addEventListener('input', (e) => {
            renderItems(e.target.value);
        });

        // Close on backdrop
        vaultModal.addEventListener('click', (e) => {
            if (e.target === vaultModal) close();
        });
    }

    async function open(callback) {
        init();
        onSelectCallback = callback;
        
        // Reset search
        document.getElementById('vaultSearch').value = '';
        
        // Show modal with animation
        vaultModal.classList.remove('hidden');
        vaultModal.classList.add('flex');
        setTimeout(() => {
            vaultModal.querySelector('.vault-container').classList.remove('scale-95', 'opacity-0');
            vaultModal.querySelector('.vault-container').classList.add('scale-100', 'opacity-100');
        }, 10);

        // Fetch data
        renderLoader();
        try {
            currentUploads = await eel.get_uploads()();
            renderItems();
        } catch (err) {
            console.error("Vault pull failed:", err);
            renderError();
        }
    }

    function close() {
        if (!vaultModal) return;
        const container = vaultModal.querySelector('.vault-container');
        container.classList.add('scale-95', 'opacity-0');
        setTimeout(() => {
            vaultModal.classList.remove('flex');
            vaultModal.classList.add('hidden');
        }, 300);
    }

    function renderLoader() {
        document.getElementById('vaultList').innerHTML = `
            <div class="flex flex-col items-center justify-center h-full space-y-6">
                <div class="relative w-16 h-16">
                    <div class="absolute inset-0 border-4 border-cyan-500/10 rounded-full"></div>
                    <div class="absolute inset-0 border-4 border-t-cyan-500 rounded-full animate-spin shadow-[0_0_15px_rgba(0,219,255,0.3)]"></div>
                </div>
                <p class="text-[10px] font-black uppercase tracking-[0.4em] text-cyan-400 animate-pulse">Syncing with Forensics Cloud...</p>
            </div>
        `;
    }

    function renderError() {
        document.getElementById('vaultList').innerHTML = `
            <div class="flex flex-col items-center justify-center h-full space-y-4 text-red-400">
                <i class="fas fa-exclamation-triangle text-2xl"></i>
                <p class="text-[10px] font-bold uppercase tracking-widest text-center">Encryption Link Severed.<br>Please re-authenticate.</p>
            </div>
        `;
    }

    function renderItems(filter = '') {
        const list = document.getElementById('vaultList');
        const searchTerm = filter.toLowerCase();
        
        const filtered = currentUploads.filter(item => 
            item.filename.toLowerCase().includes(searchTerm)
        );

        if (filtered.length === 0) {
            list.innerHTML = `
                <div class="flex flex-col items-center justify-center h-full space-y-4 opacity-50 animate-pulse">
                    <div class="w-16 h-16 rounded-full bg-cyan-500/5 flex items-center justify-center border border-cyan-500/10">
                        <i class="fas fa-ghost text-3xl text-cyan-400"></i>
                    </div>
                    <p class="text-[10px] font-black uppercase tracking-[0.3em] text-gray-500">Neural Buffer Empty: No Records</p>
                </div>
            `;
            return;
        }

        list.innerHTML = filtered.map(item => {
            const isVideo = item.type === 'video';
            const icon = isVideo ? 'fa-video' : 'fa-microphone';
            
            return `
                <div class="vault-item p-4 bg-white/5 border border-white/5 rounded-2xl flex items-center justify-between group"
                     onclick="VaultComponent.select('${item.id}')">
                    <div class="flex items-center space-x-4">
                        <div class="w-12 h-12 rounded-xl bg-cyan-500/10 flex items-center justify-center border border-cyan-500/20 group-hover:bg-cyan-500 group-hover:text-black transition-all">
                            <i class="fas ${icon} text-lg text-cyan-400 group-hover:text-black"></i>
                        </div>
                        <div>
                            <h4 class="text-sm font-bold text-white group-hover:text-cyan-400 transition-colors">${item.filename}</h4>
                            <p class="text-[10px] text-gray-500 uppercase font-bold tracking-tighter mt-1">${item.size} • ${item.timestamp}</p>
                        </div>
                    </div>
                    
                    <div class="flex items-center space-x-3">
                        <span class="px-2.5 py-1 rounded-full bg-emerald-500/10 text-emerald-400 text-[8px] font-black uppercase tracking-tighter border border-emerald-500/20">
                            Clearance: Level 4
                        </span>
                        <i class="fas fa-chevron-right text-[10px] text-white/20 group-hover:text-cyan-400 transition-colors"></i>
                    </div>
                </div>
            `;
        }).join('');
    }

    function select(id) {
        const item = currentUploads.find(u => u.id === id);
        if (item && onSelectCallback) {
            onSelectCallback(item);
            close();
        }
    }

    return {
        open,
        close,
        select
    };
})();
