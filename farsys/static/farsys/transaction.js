var action = document.getElementById('action').textContent

document.addEventListener('DOMContentLoaded', function() {
    // Add new product
    $('#new').on('changed.bs.select', function (e, clickedIndex, isSelected, previousValue) {
        var name = document.querySelector('.filter-option-inner-inner').textContent
        add_item(e.target.value, name)
    })

    // Define total and formset
    if (action.includes("Registrar")){
        n = 0
        gtotal = 0
    }else{
        n = parseInt(document.getElementById('id_order_items-INITIAL_FORMS').value)
        gtotal = parseFloat(document.getElementById('id_total').value)
    }

    // Clear Modal (new product)
    document.querySelector('#createProduct').addEventListener('click', () => clear());
 
    // Prevent submition on new product creation
    document.querySelector('#modalCreate').addEventListener('submit', function(event){
        event.preventDefault()
        newProduct()
      });

    // Prevent submition on generic product added
    document.querySelector('#modalAdd').addEventListener('submit', function(event){
        event.preventDefault()
        newProduct()
      });

    // Add eventListener on Quantity for edition 
    var data = document.getElementsByClassName('quantity');
    for( const m of data) {
        m.addEventListener('input', () => {
            changeQuant(m.id)
        });
    }

    // Add eventListener on Price for edition 
    var data = document.getElementsByClassName('price');
    for( const m of data) {
        m.addEventListener('input', () => {
            changePrice(m.id)
        });
    }
    
    // Add eventListener on Unit for edition 
    var data = document.getElementsByClassName('unit');
    for( const m of data) {
        m.addEventListener('change', () => {
            var t = document.getElementById(m.id).parentElement.previousElementSibling.firstElementChild.value
            updatePrice(m, t)
        });
    }
});

function add_item(Prod, name){
    // Add Header the first time
    if(n==0){
        document.getElementsByTagName('table')[0].style.display = ""
        document.getElementById('save').style.display = ""
    }

    // Create row for new item
    const newRow = document.createElement('tr')
    newRow.id = n
    var price = 0

    // Get price
    fetch('/get_product/'+ Prod)
    .then(response => response.json())
    .then(prod =>{
        price = prod.price_1
        console.log(prod)
        console.log(price)
        newRow.innerHTML=
        `<td style="display:none"></td>
        <td><select name="order_items-${n}-producto" class="form-control" disabled="disabled" id="id_order_items-${n}-producto">
            <option value="${Prod}" selected="">${name}</option>
        </select></td>
        <td><select name="order_items-${n}-unidad" class="form-control" maxlength="15" id="id_order_items-${n}-unidad" onchange="updatePrice(this, ${Prod})"required>
              <option value="unit_1" selected>unidad</option>
              <option value="unit_2">tira</option>
              <option value="unit_3">caja</option>
        </select></td>
        <td><input type="number" name="order_items-${n}-cantidad" class="form-control" value="1" id="id_order_items-${n}-cantidad" onchange="changeQuant(this.id)" required></td>
        <td><input type="number" name="order_items-${n}-precio" class="form-control" step="0.01" id="id_order_items-${n}-precio" onchange="changePrice(this.id)" required value="${price}"></td>
        <td><input type="number" name="order_items-${n}-total" class="form-control" step="0.01" id="id_order_items-${n}-total" value="${price}"></td>
        <td><a class="delete" title="Delete" onclick="delete_row(this)"><i class="material-icons">delete_outline</i></a></td>
        <td style="display:none"><input type="checkbox" name="order_items-${n}-DELETE" id="id_order_items-${n}-DELETE"></td>
        <!-- Helpers for update stock -->
        <td style="display:none"><input type="number" name="order_items-${n}-stock" id="id_order_items-${n}-stock"></td>
        <td style="display:none"><input value="0"></td>`
        
        gtotal = gtotal + parseFloat(price)
        document.getElementById('id_total').value = Math.round(gtotal*100)/100
        n = n+1
        document.getElementById('id_order_items-TOTAL_FORMS').value = n
    })
    // Insert new row
    document.getElementById('order').append(newRow)
}

function delete_row(row){
    // Rest the value from total
    var toDelete = row.parentElement.previousElementSibling.firstElementChild.value
    gtotal = gtotal-toDelete
    document.getElementById('id_total').value = Math.round(gtotal*100)/100

    // Mark for deletion
    row.parentElement.nextElementSibling.firstChild.checked = true
    row.parentElement.previousElementSibling.previousElementSibling.previousElementSibling.firstElementChild.value = "0"
    row.parentElement.previousElementSibling.previousElementSibling.firstElementChild.value = "0"
    row.parentElement.previousElementSibling.firstElementChild.value = "0"
    row.parentElement.parentElement.style.display = 'none'
}

function changePrice(a) {
    // Update total for row
    element = document.getElementById(a);
    x = element.value;
    y = element.parentElement.previousElementSibling.firstElementChild.value;
    a = Math.round(x * y * 100) / 100

    // Update total of the order
    var antes = element.parentElement.nextElementSibling.firstElementChild.value
    element.parentElement.nextElementSibling.firstElementChild.value = a;

    gtotal = gtotal - antes + a
    document.getElementById('id_total').value = Math.round(gtotal*100)/100
}

function changeQuant(a) {
    //Update total for row
    element = document.getElementById(a);
    x = element.value;
    y = element.parentElement.nextElementSibling.firstElementChild.value;
    a = Math.round(x * y * 100) / 100;

    //Update total of the order
    var antes = element.parentElement.nextElementSibling.nextElementSibling.firstElementChild.value
    element.parentElement.nextElementSibling.nextElementSibling.firstElementChild.value = a;

    gtotal = gtotal - antes + a
    document.getElementById('id_total').value = Math.round(gtotal*100)/100
}

function updatePrice(a, id) {
    var elem = document.getElementById(a.id).parentElement.nextElementSibling.nextElementSibling.firstChild
    fetch('/get_product/'+ id)
    .then(response => response.json())
    .then(prod => {
        var price = ""
        if(a.value == "unit_1"){
            price = prod.price_1  
        }else if(a.value == "unit_2"){
            price = prod.price_2
        }else if(a.value == "unit_3"){
            price = prod.price_3
        }
        elem.value = price     
        changePrice(elem.id)        
    });
}

function activate(){
    // Activate products and total
    var prod = document.querySelectorAll("select[name*='producto']")
    for (const m of prod){
        m.disabled = false
    }
    document.querySelector('#id_total').disabled = false
    
    // Update quantity on edit
    var quantities = document.querySelectorAll('[id*="cantidad"]')
    for (const q of quantities){
        var newQ = q.value
        var top = q.parentElement.parentElement
        var oldQ = top.children[9].firstElementChild.value
        top.children[8].firstElementChild.value = newQ - oldQ    
    } 
}

// JS for Modal

function newProduct(){
    let myform
    // Create a product
    if(document.getElementById("createProd").classList.contains("show")){
        myform = document.getElementById('modalCreate')
        $('#createProd').modal('hide')
    // Add a Generic medicine
    }else{
        myform = document.getElementById('modalAdd')
        $('#addProd').modal('hide')
    }
    // Asign form and post it
    let dataForm = new FormData(myform);
    dataForm.append('modal', 'True');

    fetch('product',{
        method: 'POST',
        body: dataForm,
    })
    .then(response => response.json())
    // Add new product in order (front)
    .then(result => {
        add_item(result.prod, result.name)
    });
}


function clear(){
    document.getElementById('id_name').value = ''
    document.getElementById('id_category').value = ''
    document.getElementById('id_price_1').value = '0.0'
    document.getElementById('id_price_2').value = '0.0'
    document.getElementById('id_price_3').value = '0.0'
    document.getElementById('id_unit_1').value = '0'
    document.getElementById('id_unit_2').value = '0'
    document.getElementById('id_unit_3').value = '0'
    document.getElementById('id_stock').value = '0'
    document.getElementById('id_obs').value = ''
}
