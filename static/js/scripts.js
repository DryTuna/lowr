// maintain a list of the products selected, so we can submit them
selectedProducts = []
function toggleRowSelect(row_id) {
    if($(row_id).hasClass("warning")) {
        $(row_id).removeClass("warning");
        selectedProducts.splice(selectedProducts.indexOf(row_id), 1);
    } else {
        $(row_id).addClass("warning");
        selectedProducts.push(row_id);
    }
}