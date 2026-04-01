function riskApp() {
  return {
    tab: 'review',
    inputText: '', docType: 'live', loading: false,
    results: [], selected: null, showModal: false,
    wordlist: [], wlSearch: '', wlShowForm: false, wlForm: {}, wlEditing: null,
    rulesList: [], ruleShowForm: false, ruleForm: {}, ruleEditing: null,
    historyList: [],

    init() {},

    jumpToResults() {
      this.showModal = false;
      this.$nextTick(() => {
        document.getElementById('result-summary')?.scrollIntoView({ behavior: 'smooth' });
      });
    },

    highlightWords(text, matchedWords) {
      const esc = text.replace(/&/g,'&amp;').replace(/</g,'&lt;').replace(/>/g,'&gt;');
      if (!matchedWords || matchedWords.length === 0) return esc;
      const words = [...new Set(matchedWords.map(m => m.word))]
        .sort((a, b) => b.length - a.length);
      let result = esc;
      for (const w of words) {
        const escaped = w.replace(/[.*+?^${}()|[\]\\]/g, '\\$&');
        result = result.replace(
          new RegExp(escaped, 'g'),
          `<strong><u style="color:#e74c3c;text-decoration-color:#e74c3c">${w}</u></strong>`
        );
      }
      return result;
    },

    async submitReview() {
      if (!this.inputText.trim()) return;
      this.loading = true; this.results = []; this.selected = null;
      try {
        const resp = await fetch('/api/review', {
          method: 'POST',
          headers: {'Content-Type': 'application/json'},
          body: JSON.stringify({text: this.inputText, doc_type: this.docType})
        });
        const data = await resp.json();
        this.results = data.sentences || [];
        if (this.results.length > 0) this.showModal = true;
      } finally { this.loading = false; }
    },

    async loadWordlist() {
      const resp = await fetch(`/api/wordlist?search=${encodeURIComponent(this.wlSearch)}&page_size=200`);
      const data = await resp.json();
      this.wordlist = data.items;
    },

    editWord(w) {
      this.wlForm = {...w}; this.wlEditing = w.id; this.wlShowForm = true;
    },

    async saveWord() {
      const url = this.wlEditing ? `/api/wordlist/${this.wlEditing}` : '/api/wordlist';
      const method = this.wlEditing ? 'PUT' : 'POST';
      const savedWord = this.wlForm.word;
      await fetch(url, {method, headers: {'Content-Type': 'application/json'}, body: JSON.stringify(this.wlForm)});
      this.wlShowForm = false; this.wlEditing = null;
      this.wlSearch = savedWord;
      await this.loadWordlist();
    },

    async toggleWord(w) {
      await fetch(`/api/wordlist/${w.id}`, {
        method: 'PUT', headers: {'Content-Type': 'application/json'},
        body: JSON.stringify({enabled: !w.enabled})
      });
      await this.loadWordlist();
    },

    async deleteWord(id) {
      if (!confirm('确认删除此词条？')) return;
      await fetch(`/api/wordlist/${id}`, {method: 'DELETE'});
      await this.loadWordlist();
    },

    async loadRules() {
      const resp = await fetch('/api/rules');
      this.rulesList = await resp.json();
    },

    editRule(r) {
      this.ruleForm = {...r}; this.ruleEditing = r.id; this.ruleShowForm = true;
    },

    async saveRule() {
      const url = this.ruleEditing ? `/api/rules/${this.ruleEditing}` : '/api/rules';
      const method = this.ruleEditing ? 'PUT' : 'POST';
      await fetch(url, {method, headers: {'Content-Type': 'application/json'}, body: JSON.stringify(this.ruleForm)});
      this.ruleShowForm = false; this.ruleEditing = null;
      await this.loadRules();
    },

    async toggleRule(r) {
      await fetch(`/api/rules/${r.id}`, {
        method: 'PUT', headers: {'Content-Type': 'application/json'},
        body: JSON.stringify({enabled: !r.enabled})
      });
      await this.loadRules();
    },

    async deleteRule(id) {
      if (!confirm('确认删除此规则？')) return;
      await fetch(`/api/rules/${id}`, {method: 'DELETE'});
      await this.loadRules();
    },

    async loadHistory() {
      const resp = await fetch('/api/history');
      const data = await resp.json();
      this.historyList = data.items;
    },

    async loadHistoryDetail(id) {
      const resp = await fetch(`/api/history/${id}`);
      const data = await resp.json();
      this.inputText = data.raw_text;
      this.results = data.sentences;
      this.selected = null;
      this.tab = 'review';
    },
  };
}
