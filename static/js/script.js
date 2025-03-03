function filterCancelledTable() {
    var dropdown = document.getElementById("cancelled-filter");
    var filterValue = dropdown.options[dropdown.selectedIndex].textContent.toLowerCase();
    var table = document.getElementById("cancelled-sessions-table");
    var rows = table.getElementsByTagName("tr");

    for (var i = 1; i < rows.length; i++) {
        var row = rows[i];
        var sport = row.getElementsByTagName("td")[0].textContent.toLowerCase();
        // console.log(filterValue);
        // console.log(sport)
        if (filterValue === "all" || sport === filterValue) {
            row.style.display = "";
        } else {
            row.style.display = "none";
        }
    }
}

function scrollToTop() {
    document.body.scrollTop = 0; // For Safari
    document.documentElement.scrollTop = 0; // For Chrome, Firefox, IE, and Opera
}

window.onscroll = function() {
    var scrollButton = document.getElementById("scrollButton");
    if (document.body.scrollTop > 20 || document.documentElement.scrollTop > 20) {  // use OR so that it works on Chrome, Firefox, and Safari
        scrollButton.style.display = "block";
    } else {
        scrollButton.style.display = "none";
    }
};