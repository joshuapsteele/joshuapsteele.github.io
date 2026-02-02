(function () {
  "use strict";

  function init(container) {
    var input = container.querySelector("[data-amazon-purchases-search]") ||
      container.querySelector(".amazon-purchases-search");
    var count = container.querySelector("[data-amazon-purchases-count]");
    var rows = Array.prototype.slice.call(
      container.querySelectorAll(".amazon-purchases-table tbody tr")
    );

    if (!input || rows.length === 0) {
      return;
    }

    function updateCount(visible) {
      if (!count) return;
      count.textContent = visible + " of " + rows.length;
    }

    function normalize(value) {
      return String(value || "").toLowerCase();
    }

    function filter() {
      var q = normalize(input.value.trim());
      var visible = 0;

      rows.forEach(function (row) {
        var text = normalize(row.textContent);
        var match = q === "" || text.indexOf(q) !== -1;
        row.style.display = match ? "" : "none";
        if (match) visible += 1;
      });

      updateCount(visible);
    }

    input.addEventListener("input", filter);
    filter();
  }

  document.addEventListener("DOMContentLoaded", function () {
    var containers = document.querySelectorAll("[data-amazon-purchases]");
    containers.forEach(init);
  });
})();
