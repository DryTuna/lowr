// maintain a list of the products selected, so we can submit them



selectedProductURLs = []
function toggleRowSelect(product_url) {
    product_listing = $(document.getElementById(product_url));
    if(product_listing.hasClass("warning")) {
        product_listing.removeClass("warning");
        selectedProductURLs.splice(selectedProductURLs.indexOf(product_url), 1);
    } else {
        product_listing.addClass("warning");
        selectedProductURLs.push(product_url);
    }
}

function submitItems() {
          $.ajax(("/submititems"), {
                type: 'POST',
                data: JSON.stringify(selectedProductURLs),
                contentType: 'application/json',
                context: document.body,
                success: function(result) {
                    location.href = result;
                }
            });
        }

$('document').ready(function() {

    $('#search_form').on('submit', function(event) {
                  selectedProductURLs = []
                  event.preventDefault();
                  var search_form =  $(event.target);
                  var formJsonData = JSON.stringify($(this).serializeArray());
                  $("body").addClass("loading");

                  $.ajax(("/search"), {
                      type: 'POST',
                      data: {'data':formJsonData},
                      context: search_form,
                      success: function(result) {
                          document.getElementById('submit_items_wrapper').style.display = 'block'
                          $("body").removeClass("loading");
                          $('#search_results').html(result)
                      }
                  });
            });
})
