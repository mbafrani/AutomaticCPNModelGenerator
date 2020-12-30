class Wizard {

  constructor() {
    this.pageViews = [];
    this.pageViewContents = [];
    this.data = {};
    this.currentPageIndex = -1;
    this.previousPageIndex = -1;
    this.storePageChangesInMemory = false;
  }

  setUsePreviousPageFromMemory = useFromMemory => {
    this.storePageChangesInMemory = useFromMemory
  }

  setSharedDataForKey = (key, value) => {
    this.data[key] = value
  }

  getSharedDataForKey = key => this.data[key]

  getWizardSharedData = () => this.data

  setupPage = (loadPageAgain) => {
    const wizardContent = $("#wizard-content")[0];
    $(wizardContent).animate({
      opacity: 0
    }, 400, () => {
      $(wizardContent).html(this.pageViewContents[this.currentPageIndex]).animate({
        opacity: 1
      }, 400);

      const wizardTitle = $("#wizard-title")[0];
      $(wizardTitle).text(this.pageViews[this.currentPageIndex].title);

      const leftButton = $("#wizard-nav-left-btn")[0];
      $(leftButton).text(this.pageViews[this.currentPageIndex].leftBtnText);
      $(leftButton).off("mousedown");
      $(leftButton).on("mousedown", this.pageViews[this.currentPageIndex].leftBtnListener);

      const rightButton = $("#wizard-nav-right-btn")[0];
      $(rightButton).text(this.pageViews[this.currentPageIndex].rightBtnText);
      $(rightButton).off("mousedown");
      $(rightButton).on("mousedown", this.pageViews[this.currentPageIndex].rightBtnListener);

      // TODO: Check if this works
      if (loadPageAgain) {
        this.pageViews[this.currentPageIndex].onLoadListener && this.pageViews[this.currentPageIndex].onLoadListener()
      }

    });
  }

  addPage = (title, onLoadListener, leftBtnText, leftBtnListener, rightBtnText, rightBtnListener) => {
    onLoadListener && (onLoadListener = onLoadListener.bind(this));
    leftBtnListener && (leftBtnListener = leftBtnListener.bind(this));
    rightBtnListener && (rightBtnListener = rightBtnListener.bind(this));
    this.pageViews.push({
      title: title,
      onLoadListener: onLoadListener,
      leftBtnText: leftBtnText,
      leftBtnListener: leftBtnListener,
      rightBtnText: rightBtnText,
      rightBtnListener: rightBtnListener
    })
  }

  showWizard = () => {

    // show a loading gif until the wizard partial views are loaded
    $("#wizard-content").html(
      '<div class="wizard__page">\
          <img src="images/loading.gif" />\
      <\/div>'
    );

    const partialViews = [
      "wizard-import-log.html",
      "wizard-process-model.html",
      "wizard-view-params.html",
      "wizard-change-params.html",
      "wizard-process-model.html",
    ]
    const promises = []
    for (let i = 0; i < partialViews.length; i++) {
      promises.push($.get("views/" + partialViews[i]))
    }

    Promise.all(promises).then((contents) => {
      this.pageViewContents = $("<div/>").append(contents).find(".wizard__page");
      this.currentPageIndex = 0;
      this.setupPage(true)
    });
  }

  viewNextPage = (pageNumber, loadPageListener=true) => {
    if (this.storePageChangesInMemory) {
        const content = $("#wizard .wizard__page")[0];
        this.pageViewContents[this.currentPageIndex] = content
    }
    this.previousPageIndex = this.currentPageIndex;
    typeof pageNumber == "number" ? this.currentPageIndex = (pageNumber - 1) : this.currentPageIndex++;
    this.setupPage(loadPageListener)
  }

  viewPreviousPage = (pageNumber, loadPageListener=true) => {
    this.previousPageIndex = this.currentPageIndex;
    typeof pageNumber == "number" ? this.currentPageIndex = pageNumber - 1 : this.currentPageIndex--;
    this.setupPage(loadPageListener)
  }

  getCurrentPageNumber = () => this.currentPageIndex + 1

  disableLeftButton = () => {
    const leftButton = $("#wizard-nav-left-btn")[0];
    $(leftButton).prop("disabled", true);
    $(leftButton).addClass("wizard__nav__btn-disabled")
  }

  enableLeftButton = () => {
    const leftButton = $("#wizard-nav-left-btn")[0];
    $(leftButton).prop("disabled", false);
    $(leftButton).removeClass("wizard__nav__btn-disabled")
  }

  disableRightButton = () => {
    const rightButton = $("#wizard-nav-right-btn")[0];
    $(rightButton).prop("disabled", true);
    $(rightButton).addClass("wizard__nav__btn-disabled")
  }

  enableRightButton = () => {
    const rightButton = $("#wizard-nav-right-btn")[0];
    $(rightButton).prop("disabled", false);
    $(rightButton).removeClass("wizard__nav__btn-disabled")
  }

}

export default Wizard
