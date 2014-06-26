// maintain a list of the products selected, so we can submit them



selectedProducts = []
function toggleRowSelect(product_url) {
    product_listing = $(document.getElementById(product_url));
    if(product_listing.hasClass("warning")) {
        product_listing.removeClass("warning");
        for(i = 0; i < selectedProducts.length; i++) {
            if(selectedProducts[i].url == product_url) {
                selectedProducts.splice(selectedProducts.indexOf(product_url), 1);
                break;
            }
        }
    } else {
        product_listing.addClass("warning");
        // whichever is less, the prime price or the price
        tds = document.getElementById(product_url).getElementsByTagName('td');
        price_col = tds[tds.length - 1];
        prime_price_col = tds[tds.length - 2];
        var prime_price = parseFloat(prime_price_col.innerHTML.replace("$", "").trim());
        var price = parseFloat(price_col.innerHTML.replace("$", "").trim());
        if(isNaN(price) || Math.round(price) == 0) {
            price = prime_price;
        } else if(!isNaN(prime_price) && Math.round(prime_price) != 0) {
          price = Math.min(price, prime_price);
        }
        selectedProducts.push({"url": product_url,
                               "desired_price": parseFloat(document.getElementById("search_min_price").value),
                               "last_price": price});
    }
}

function submitItems() {
  $.ajax(("/submititems"), {
        type: 'POST',
        data: JSON.stringify(selectedProducts),
        contentType: 'application/json',
        context: document.body,
        success: function(result) {
            location.href = result;
        }
    });
}

$('document').ready(function() {

    $('#search_form').on('submit', function(event) {
                  selectedProducts = []
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
