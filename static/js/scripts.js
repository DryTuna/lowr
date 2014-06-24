function toggleRowSelect(row) {
    if($(row).hasClass("warning"))
        $(row).removeClass("warning");
    else
        $(row).addClass("warning");
}