// maintain a list of the products selected, so we can submit them
selectedProductURLs = []
function toggleRowSelect(product_url) {
    if($(product_url).hasClass("warning")) {
        $(product_url).removeClass("warning");
        selectedProductURLs.splice(selectedProductURLs.indexOf(product_url), 1);
    } else {
        $(product_url).addClass("warning");
        selectedProductURLs.push(product_url);
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
          }
    });
})