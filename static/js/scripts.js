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

$('document').ready(function() {
    $('#search_form').on('submit', function(event) {
          selectedProductURLs = []
          event.preventDefault();
          var search_form =  $(event.target);
          var formJsonData = JSON.stringify($(this).serializeArray());

          console.log(formJsonData);

          $.ajax(("/search"), {
              type: 'POST',
              data: {'data':formJsonData},
              context: search_form,
              success: function(result) {
                   $('#search_results').html(result)
              }
          });
    });

    // thanks to Rohan Kumar on stackoverflow
    $('#create_form').on('submit',function() {
        if($('#signup_password').val() != $('#signup_password_confirm').val()) {
            alert('Password does not match confirmation');
            return false;
        }
        return true;
    });
})