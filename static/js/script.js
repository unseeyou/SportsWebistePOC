function filterCancelledTable() {
    var dropdown = document.getElementById("cancelled-filter");
    var filterValue = dropdown.textContent;
    var table = document.getElementById("cancelled-sessions-table");
    var rows = table.getElementsByTagName("tr");

    for (var i = 1; i < rows.length; i++) {
        var row = rows[i];
        var sport = row.getElementsByTagName("td")[0].textContent;
        console.log(filterValue);
        console.log(sport)
        if (filterValue === "all" || sport === filterValue) {
            row.style.display = "";
        } else {
            row.style.display = "none";
        }
    }
}