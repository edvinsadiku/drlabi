document.addEventListener("alpine:init", () => {
  Alpine.data("patientWorkspace", () => ({
    active: "overview",
    query: "",
    tooth: "",
    success: "",
    modalTitle: "",
    modalUrl: "",
    modalNext: "",
    loading: false,
    opener: null,
    allowed: [
      "overview",
      "activity",
      "trajtimet",
      "marreveshjet",
      "pagesat",
      "shto-pages",
      "dokumente",
      "recetat",
      "arkiva-histori",
      "arkiva-ortho",
      "arkiva-financa",
    ],
    init() {
      const params = new URL(location).searchParams;
      if (this.allowed.includes(params.get("tab")))
        this.active = params.get("tab");
      this.$nextTick(() => this.revealActiveTab());
      const key = "patient-success-" + this.$root.dataset.patientId;
      // Server feedback may include allocation details; show it once instead of a second generic banner.
      this.success = document.querySelector(".notice-stack .notice") ? "" : sessionStorage.getItem(key) || "";
      sessionStorage.removeItem(key);
      window.addEventListener("popstate", () => {
        const tab = new URL(location).searchParams.get("tab");
        this.active = this.allowed.includes(tab) ? tab : "overview";
        this.$nextTick(() => this.revealActiveTab());
      });
      window.addEventListener("message", (event) => {
        if (
          event.origin !== location.origin ||
          event.source !== this.$refs.workflowFrame.contentWindow
        )
          return;
        if (event.data?.type === "patient-modal-close") {
          this.closeModal();
          return;
        }
        if (event.data?.type !== "patient-modal-done") return;
        sessionStorage.setItem(key, this.modalTitle + " u ruajt me sukses.");
        const url = new URL(location);
        url.searchParams.set("tab", this.modalNext || "overview");
        url.searchParams.delete("workflow");
        this.closeModal();
        location.assign(url);
      });
    },
    revealActiveTab() {
      const tabs = this.$root.querySelector('.patient-tabs');
      const active = tabs?.querySelector('button.selected');
      if (!tabs || !active) return;
      const container = tabs.getBoundingClientRect(), item = active.getBoundingClientRect();
      if (item.left < container.left) tabs.scrollLeft -= container.left - item.left + 8;
      else if (item.right > container.right) tabs.scrollLeft += item.right - container.right + 8;
    },
    set(tab) {
      if (!this.allowed.includes(tab)) return;
      this.active = tab;
      this.$nextTick(() => this.revealActiveTab());
      const url = new URL(location);
      url.searchParams.set("tab", tab);
      url.searchParams.delete("workflow");
      history.pushState({}, "", url);
    },
    filterTooth(code) {
      this.tooth = code;
      this.query = "";
      this.set("trajtimet");
    },
    matches(el) {
      const codes = (el.dataset.teeth || "").match(/\d+/g) || [];
      return (
        (!this.tooth || codes.includes(this.tooth)) &&
        (!this.query ||
          (el.dataset.search || "")
            .toLocaleLowerCase()
            .includes(this.query.toLocaleLowerCase()))
      );
    },
    visibleTreatments() {
      return Array.from(this.$root.querySelectorAll(".treatment-card")).some(
        (el) => this.matches(el),
      );
    },
    openModal(title, url, next) {
      this.opener = document.activeElement;
      this.modalTitle = title;
      this.modalUrl = url;
      this.modalNext = next;
      this.loading = true;
      this.$refs.workflowDialog.showModal();
      document.body.style.overflow = "hidden";
    },
    closeModal() {
      this.$refs.workflowDialog.close();
      this.modalUrl = "";
      document.body.style.overflow = "";
      this.opener?.focus();
    },
  }));
});
