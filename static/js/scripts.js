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


$('document').ready(function(){
    $('#search_form').on('submit', function(event) {
          event.preventDefault();
          var search_form =  $(event.target);
          $.ajax(search_form.action),{
              type: 'GET',
              data: JSON.stringify(search_form.serializeArray()),
              context: search_form,
              success: function(result){
                  var parent = $(this).parent();
                  parent.empty().html(result);

              }
          });
    });
})