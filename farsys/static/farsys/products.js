
document.addEventListener('DOMContentLoaded', function() {
    // Get all products in memory
    getProducts()

    // Filter products live search
    document.getElementById('search').addEventListener('keyup', ()=> search())
});


function getProducts(){
    fetch('/find_product')
    .then(response => response.json())
    .then(prod =>{
        data = prod
    })
}

function search(){
    var input = document.getElementById('search')
    const box = document.getElementById('result')
    let filtered = []

    box.innerHTML = ""
    filtered = data.filter(info => info['name'].includes(input.value.toUpperCase()))
    console.log(filtered)
    if (filtered.length > 0){
        filtered.map(item =>{
            box.innerHTML += 
            `<tr id="${item.id}">
                <td >${item.name}</td>
                <td>${item.stock}</td>
                <td>${item.price_1}</td>
                <td>${item.price_2}</td>
                <td>${item.price_3}</td>
                <td>${item.obs}</td>
                <td><button class="edit" type="submit" value="${item.id}" onclick="toEdit(this)"><i class="material-icons">edit</i></button></td>
            </tr>`
        })
    } else {
        box.innerHTML = "No se encontró ningún producto."
    }
}

function toEdit(a){
    document.getElementById('input').value = a.value
}
