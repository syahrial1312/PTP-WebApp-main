usedSpareparts = usedSpareparts.map(up => ({ id: up[0], nama: up[1], qty: up[2] }));
allSpareparts = allSpareparts.map(as => ({ id: as[0], nama: as[1] }));

function addRow(){
    let table = document.getElementById("selectedSparepartTable").getElementsByTagName('tbody')[0];
    let rowCount = table.rows.length;
    let row = table.insertRow(rowCount);

    row.innerHTML = `
        <td>${rowCount + 1}</td>
        <td><input type="text" name="id" onkeyup="searchTable(event, this)"></td>
        <td><input type="text" name="nama" onkeyup="searchTable(event, this)"></td>
        <td><input type="number" min="1"></td>
        <td class="remove-btn" onclick="removeRow(this)">❌</td>
    `;
}

function removeRow(button) {
    let row = button.parentNode;
    row.parentNode.removeChild(row);
    updateRowNumbers();
}

function updateRowNumbers() {
    let rows = document.querySelectorAll("#selectedSparepartTable tbody tr");
    rows.forEach((row, index) => {
        row.cells[0].innerText = index + 1;
    });
}

function selected(id, name, qty) {
    // console.log(name)
    let table = document.getElementById("selectedSparepartTable").querySelector("tbody")
    let existingRow = [...table.rows].find(row => row.cells[1].innerText === String(id));
    
    if (existingRow) {
        let qtyInput = existingRow.cells[3].querySelector("input");
        qtyInput.value = parseInt(qtyInput.value) + 1;
        return;
    }
    else {
        console.log("Gak masuk existing");    
    }
    let rowCount = table.rows.length;
    let row = table.insertRow(rowCount);
    row.innerHTML = `
        <td>${rowCount + 1}</td>
        <td><input type="hidden" name="sparepart_id[]" value="${id}">${id}</td>
        <td>${name}</td>
        <td><input type="number" name="sparepart_qty[]" value="${qty}" min="1"></td>
        <td style="color: red; cursor: pointer;" onclick="removeRow(this)">❌</td>
    `;  
}


usedSpareparts.forEach(sparepart => {
    selected(sparepart.id, sparepart.nama, sparepart.qty);
});

// function searchTable() {
//     let suggestionBox = document.getElementById("suggestionBox");
//     let input = document.getElementById("nama").value.toLowerCase();
//     suggestionBox.innerHTML = "";

//     if (input === "") {
//         suggestionBox.style.display = "none";
//         return;
//     }

//     let filteredSpareparts = allSpareparts.filter(sparepart =>
//         sparepart.name.toLowerCase().includes(input) || sparepart.id.includes(input)
//     );

//     if (filteredSpareparts.length === 0) {
//         suggestionBox.style.display = "none";
//         return;
//     }

//     filteredSpareparts.forEach(sparepart => {
//         let item = document.createElement("a");
//         item.className = "list-group-item list-group-item-action";
//         item.innerHTML = `<strong>${sparepart.id}</strong> - ${sparepart.nama}`;
//         item.style.cursor = "pointer";
//         item.onclick = () => selectSparepart(sparepart.id, sparepart.nama);
//         suggestionBox.appendChild(item);
//     });

//     suggestionBox.style.display = "block";
// }


function searchTable(event, inputElement) {
    let suggestionBox = document.getElementById("suggestionBox");

    // Ambil input dari elemen input nama yang sesuai
    // let inputElement = document.querySelector("input[name='nama']");
    if (!inputElement) {
        console.error("Elemen input nama tidak ditemukan.");
        return;
    }

    let input = inputElement.value.toLowerCase();
    suggestionBox.innerHTML = "";

    if (input === "") {
        suggestionBox.style.display = "none";
        return;
    }

    let filteredSpareparts = allSpareparts.filter(sparepart =>
        sparepart.nama?.toLowerCase().includes(input) 
        // || sparepart.id.includes(input)
    );

    if (filteredSpareparts.length === 0) {
        suggestionBox.style.display = "none";
        return;
    }

    filteredSpareparts.forEach(sparepart => {
        let item = document.createElement("a");
        item.className = "list-group-item list-group-item-action";
        item.innerHTML = `<strong>${sparepart.id}</strong> - ${sparepart.nama}`;
        item.style.cursor = "pointer";
        item.onclick = () => selected(sparepart.id, sparepart.nama, 1);
        suggestionBox.appendChild(item);
    });

    suggestionBox.style.display = "block";
}
