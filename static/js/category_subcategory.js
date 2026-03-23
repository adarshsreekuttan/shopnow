$(document).ready(function(){
$('#category').change(function(){
    var categoryslug = $(this).val();
    $.ajax({
        url: "ajax/load_subcategory",
        data:{'category_slug':categoryslug},
        success: function (data){
            $("#subcategory").html('<option value =""> Select SubCategory </option>');
            data.forEach(function(sub){
                $("#subcategory").append(
                    `<option value='${sub.slug}'>${sub.name}</option>`
                );

            });

        }
    });
});
});