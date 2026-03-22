document.getElementById("subcategory").addEventListener("change", function() {
    let subcatId = this.value;

    fetch(`/get-attributes/?subcat_id=${subcatId}`)
    .then(response => response.json())
    .then(data => {
        let container = document.getElementById("attributes-container");
        container.innerHTML = "";

        data.data.forEach(attr => {
            let html = `<label>${attr.attr_name}</label><select name="attribute_values" multiple>`;
            
            attr.values.forEach(val => {
                html += `<option value="${val.id}">${val.value}</option>`;
            });

            html += `</select><br><br>`;
            container.innerHTML += html;
        });
    });
});